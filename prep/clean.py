import matplotlib.pyplot as plt
import nltk
import re
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('stopwords')
plt.ion()

def clean(doc):
    
    def strip_html_tags(text):
        soup = BeautifulSoup(text, "html.parser")
        stripped_text = soup.get_text()
        return stripped_text

    def strip_urls(text):
        #url regex
        url_re = re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
        stripped_text = url_re.sub('',text)
        return stripped_text

    def strip_emails(text):
        #email address regex
        email_re = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        stripped_text = email_re.sub('',text)
        return stripped_text

    def strip_nonsense(text):
        # leave words that are at least three characters long, do not contain a number, and are no more 
        # than 17 chars long
        no_nonsense = re.findall(r'\b[a-z][a-z][a-z]+\b',text)
        stripped_text = ' '.join(w for w in no_nonsense if w != 'nan' and len(w) <= 17)
        return stripped_text
    
    doc = doc.lower()
    tag_free = strip_html_tags(doc)
    url_free = strip_urls(tag_free)
    email_free = strip_emails(url_free)
    normalized_1 = strip_nonsense(email_free)
    
    stop_free = " ".join([i for i in normalized_1.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(WordNetLemmatizer().lemmatize(word) for word in punc_free.split())
    
    return normalized
