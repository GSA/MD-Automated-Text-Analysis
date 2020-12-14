from PyQt5 import QtWidgets, uic
import sys
from topicsanalyser import TopicsAnalyser

class TopicsAnalyser_UI(QtWidgets.QMainWindow):
    def __init__(self):
        super(TopicsAnalyser_UI, self).__init__()
        uic.loadUi('main_form.ui', self)
        
        self.run_btn = self.findChild(QtWidgets.QPushButton, 'run_btn')
        self.run_btn.clicked.connect(self.run_topics_analyser)
        
        self.data_file_txt = self.findChild(QtWidgets.QLineEdit, 'data_file_txt')
        self.num_topics_spb = self.findChild(QtWidgets.QSpinBox, 'num_topics_spb')
        self.num_ngrams_spb = self.findChild(QtWidgets.QSpinBox, 'num_ngrams_spb')
        self.groupby_cols_txt = self.findChild(QtWidgets.QLineEdit, 'groupby_cols_txt')
        self.addl_stopwords_txt = self.findChild(QtWidgets.QLineEdit, 'addl_stopwords_txt')
        self.message_lbl = self.findChild(QtWidgets.QLabel, 'message_lbl')
        # self.statusBar().showMessage('Analyzing data...')
       
        # TODO: add field validations
        
        self.show()
        
    def run_topics_analyser(self):
        groupby_cols_text = self.groupby_cols_txt.text()
        groupby_cols = groupby_cols_text.split(',') if (len(groupby_cols_text) > 0) else []

        addl_stopwords_text = self.addl_stopwords_txt.text()
        addl_stopwords = addl_stopwords_text.split(',') if (len(addl_stopwords_text) > 0) else []

        analyser = TopicsAnalyser(self.data_file_txt.text())
        message = analyser.get_topics(self.num_topics_spb.value(), groupby_cols, self.num_ngrams_spb.value(), addl_stopwords)
        self.statusBar().showMessage(message) 

        
app = QtWidgets.QApplication(sys.argv)
window = TopicsAnalyser_UI()
sys.exit(app.exec_())

        