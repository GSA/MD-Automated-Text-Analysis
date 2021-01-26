from pandas import DataFrame
from PyQt5.QtCore import QThread, pyqtSignal
from topicsanalyser import TopicsAnalyser

class TopicsAnalyser_Thread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self,
                 data: DataFrame,
                 output_filename: str,
                 num_topics: int,
                 groupby_cols: list,
                 num_ngrams: int,
                 addl_stopwords: list):        
        QThread.__init__(self)
        self.data = data
        self.output_filename = output_filename
        self.num_topics = num_topics
        self.groupby_cols = groupby_cols
        self.num_ngrams = num_ngrams
        self.addl_stopwords = addl_stopwords
        
    def run(self):
        analyser = TopicsAnalyser(self.data, self.output_filename)
        mod_msg = analyser.get_topics(self.num_topics, self.groupby_cols, self.num_ngrams, self.addl_stopwords)
        self.finished.emit(mod_msg)
            