import numpy as np
import pandas as pd
import re

# NLTK
from nltk.corpus import stopwords

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim import utils, models

from utils.clean_funcs.clean import remove_stopwords, make_bigrams, lemmatization, sent_to_words
from ngrams_maker import NGramsMaker

class TopicsFinder:
    
    def __init__(self, data_file_path, no_of_ngrams=2, addl_stop_words=[]):

        if (no_of_ngrams < 1):
            raise ValueError("no_of_ngrams must be greater than 0.")
            
        self.stop_words = set(stopwords.words('english') + addl_stop_words)
        self.no_of_ngrams = no_of_ngrams
        
        df = self._setup_dataframe(data_file_path)
        self.data_lemmatized, self.id2word, self.corpus = self._preprocess_data(df)
        
        
    def _setup_dataframe(self, data_file_path):
        
        data = pd.read_excel(data_file_path)
        df = data[['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL', \
                   'SUP_STATUS','Please briefly describe an example of one burdensome administrative task or process which you believe is "low value"']]
        df.columns = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS','TEXT']
        full_df = df[df['TEXT'].isnull()==False]
        full_df = df[df['TEXT'].isna()==False]
        full_df = df[df['COMPONENT'].isna()==False]
        full_df = df[df['GRADELEVEL'].isna()==False]
        full_df.dropna(subset=['TEXT'],inplace=True)
        
        return full_df
    

    def _preprocess_data(self, df):
        text_list = df['TEXT'].values.tolist()

        # Remove Emails
        text_list = [re.sub('\S*@\S*\s?', '', str(sent)) for sent in text_list]

        # Remove new line characters
        text_list = [re.sub('\s+', ' ', str(sent)) for sent in text_list]

        # Remove distracting single quotes
        text_list = [re.sub("\'", "", str(sent)) for sent in text_list]

        data_words = list(sent_to_words(text_list))

        # Remove Stop Words
        data_words_nostops = [[word for word in simple_preprocess(str(doc)) if word not in self.stop_words] for doc in data_words]

        # Form n-grams
        maker = NGramsMaker(self.no_of_ngrams, data_words)    
        data_words_ngrams = maker.make_ngrams(data_words_nostops)

        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_ngrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        corpus = [id2word.doc2bow(text) for text in data_lemmatized]
        
        return data_lemmatized, id2word, corpus
    
       
    def fit_LDA_model(self, no_of_topics):
        # TODO: search for the optimal hyper-parameters
        print("Fitting LDA model...")
        model = gensim.models.ldamodel.LdaModel(corpus= self.corpus, num_topics= no_of_topics, id2word= self.id2word,
                random_state=100, update_every=1, chunksize=100, passes=10, alpha='auto', per_word_topics=True)
        coherencemodel = CoherenceModel(model= model, texts= self.data_lemmatized, dictionary= self.id2word, coherence='c_v')
        print("Done.")
        
        return model, coherencemodel
    
    def get_topics(self, model, num_words_in_topic = 10):
        return model.show_topics(num_words= num_words_in_topic, formatted=True)
    
    def get_coherencescore(self, coherencemodel):
        return coherencemodel.get_coherence()
    
    

    
    
    
        