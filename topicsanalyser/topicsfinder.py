import pandas as pd
import re

# NLTK
from nltk.corpus import stopwords

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import LdaModel, CoherenceModel

# Utilities
from utils.clean_funcs.clean import lemmatization, sent_to_words
from ngrams_maker import NGramsMaker

class TopicsFinder:
    
    def __init__(self, data: pd.DataFrame, num_ngrams: int= 2, addl_stop_words: [str]= []):

        self.stop_words = set(stopwords.words('english') + addl_stop_words)
        self.num_ngrams = num_ngrams
        self.data_lemmatized, self.id2word, self.corpus = self._preprocess_data(data)

    def _preprocess_data(self, df: pd.DataFrame) -> None:
        text_list = df['TEXT'].values.tolist()

        # Remove Emails
        text_list = [re.sub(r'\S*@\S*\s?', '', str(sent)) for sent in text_list]

        # Remove new line characters
        text_list = [re.sub(r'\s+', ' ', str(sent)) for sent in text_list]

        # Remove distracting single quotes
        text_list = [re.sub(r"\'", "", str(sent)) for sent in text_list]

        data_words = list(sent_to_words(text_list))

        # Remove Stop Words
        data_words_nostops = [[word for word in simple_preprocess(str(doc)) if word not in self.stop_words] for doc in data_words]

        # Form n-grams
        maker = NGramsMaker(data_words, self.num_ngrams)    
        data_words_ngrams = maker.make_ngrams(data_words_nostops)

        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_ngrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        corpus = [id2word.doc2bow(text) for text in data_lemmatized]
        
        return data_lemmatized, id2word, corpus
    
       
    def fit_model(self, **kwargs) -> (LdaModel, CoherenceModel):
        model = LdaModel(corpus= self.corpus, id2word= self.id2word, **kwargs)
        # processes must be set to 1 or multiple copies of the UI application will be created
        coherencemodel = CoherenceModel(model= model, texts= self.data_lemmatized, dictionary= self.id2word, coherence='c_v', processes=1)
        
        return model, coherencemodel    

    
    
    
        