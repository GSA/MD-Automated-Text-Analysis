import gensim

class NGramsMaker:
    
    def __init__(self, no_of_grams, texts):
        self.no_of_grams = no_of_grams
        self._ngram_dict = {}
        
        self._create_ngrams_model(texts)
    
    def _get_ngram_sentences(self, texts):
        sentences = texts
        for i in range(2, self.no_of_grams + 1):
            sentences = self._ngram_dict[i]['model'][sentences]
            
        return sentences
                       
    def _create_ngrams_model(self, texts):
        self._ngram_dict[1] = {'ngram': texts, 'model': None}

        sentences = texts
        for n in range (2, self.no_of_grams + 1):
            print("n = " + str(n))
            ngram = gensim.models.Phrases(sentences, min_count = 5, threshold=50) # higher threshold fewer phrases.
            ngram_mod = gensim.models.phrases.Phraser(ngram)
            self._ngram_dict[n] = {'ngram': ngram, 'model': ngram_mod}

            if (n < self.no_of_grams):
                sentences = texts
                for i in range(2, n + 1):
                    sentences = self._ngram_dict[i]['ngram'][sentences]
                    
        print("Done.")
        
    def make_ngrams(self, texts):
        return [self._get_ngram_sentences(doc) for doc in texts]