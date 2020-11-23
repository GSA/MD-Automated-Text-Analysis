import numpy as np
import pandas as pd

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim import utils, models

from utils.clean_funcs.clean import remove_stopwords, make_bigrams, lemmatization, sent_to_words
from utils.calc_funcs.calc import compute_coherence_values

class TopicsFinder:
    def __init__(self, data_file_path, no_of_topics, no_of_ngrams, addl_stop_words):
        self.data_file_path = data_file_path
        self.no_of_topics = no_of_topics
        self.no_of_ngrams = no_of_ngrams
        self.addl_stop_words = addl_stop_words
        
    def _setup_dataframe(data_file_path):
        
        data = pd.read_excel(data_file_path)
        df = data[['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS','Please briefly describe an example of one burdensome administrative task or process which you believe is "low value"']]
        df.columns = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS','TEXT']
        full_df = df[df['TEXT'].isnull()==False]
        full_df = df[df['TEXT'].isna()==False]
        full_df = df[df['COMPONENT'].isna()==False]
        full_df = df[df['GRADELEVEL'].isna()==False]
        full_df.dropna(subset=['TEXT'],inplace=True)
        return full_df

    def preprocess_data(df):
        text_list = df['TEXT'].values.tolist()

        # Remove Emails
        text_list = [re.sub('\S*@\S*\s?', '', str(sent)) for sent in text_list]

        # Remove new line characters
        text_list = [re.sub('\s+', ' ', str(sent)) for sent in text_list]

        # Remove distracting single quotes
        text_list = [re.sub("\'", "", str(sent)) for sent in text_list]

        data_words = list(sent_to_words(text_list))

        # Build the bigram and trigram models
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=50) # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=50)  

        # Faster way to get a sentence clubbed as a trigram/bigram
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod= gensim.models.phrases.Phraser(trigram)

        # Remove Stop Words
        data_words_nostops = remove_stopwords(data_words)

        # Form Bigrams
        data_words_bigrams = make_bigrams(data_words_nostops, bigram_mod)

        # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
        # python3 -m spacy download en
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

        # Create Dictionary
        id2word2 = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        corpus = [id2word2.doc2bow(text) for text in data_lemmatized]
        
        return corpus
       
    def train_LDA_model():
        pass
    
    
    
        