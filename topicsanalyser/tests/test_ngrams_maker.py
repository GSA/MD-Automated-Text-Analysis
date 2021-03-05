import pytest
from pytest_mock import MockerFixture as mocker
import gensim
import collections
from ..ngrams_maker import NGramsMaker

@pytest.mark.skip(reason="no way of currently testing this")
def test_make_ngrams(mocker):
    
    def mock_phrases(sentences, min_count, threshold):
        return [['trees_graph','minors']]

    def mock_phraser(ngram):
        return [['trees_graph','minors']]
    
    mocker.patch(
        'gensim.models.Phrases',
        mock_phrases
    )
    
    mocker.patch(
        'gensim.models.phrases.Phraser',
        mock_phraser
    )
    
    expected = [['trees_graph','minors']]
    texts = [['trees','graph','minors']]
    ngram_maker = NGramsMaker(texts, 2)
    actual = ngram_maker.make_ngrams(texts)
    assert collections.Counter(actual) == collections.Counter(expected)
    
 