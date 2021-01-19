import gensim

class NGramsMaker:
    '''
    A class used to generate n-grams from the input texts
    '''
    
    def __init__(self, texts: [[str]], num_ngrams: int = 2):
        
        if (num_ngrams < 1):
            raise ValueError("num_ngrams must be greater than 0.")
            
        self.num_ngrams = num_ngrams
        self._ngram_dict = {}
        
        self._create_ngrams_model(texts)
        
    
    def _get_ngram_sentences(self, texts: [str]):
        sentences = texts
        for i in range(2, self.num_ngrams + 1):
            sentences = self._ngram_dict[i]['model'][sentences]
            
        return sentences
    
                       
    def _create_ngrams_model(self, texts: [[str]]):
        self._ngram_dict[1] = {'ngram': texts, 'model': None}

        sentences = texts
        for n in range (2, self.num_ngrams + 1):
            ngram = gensim.models.Phrases(sentences, min_count = 5, threshold=50) # higher threshold fewer phrases.
            ngram_mod = gensim.models.phrases.Phraser(ngram)
            self._ngram_dict[n] = {'ngram': ngram, 'model': ngram_mod}

            if (n < self.num_ngrams):
                sentences = texts
                for i in range(2, n + 1):
                    sentences = self._ngram_dict[i]['ngram'][sentences]
            
                            
    def make_ngrams(self, texts: [[str]]) -> [[str]]:
        return [self._get_ngram_sentences(doc) for doc in texts]