from PyQt5 import uic
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QLineEdit, QSpinBox, QFileDialog)
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
from topicsanalyser import TopicsAnalyser

class TopicsAnalyser_UI(QMainWindow):
    def __init__(self):
        super(TopicsAnalyser_UI, self).__init__()
        uic.loadUi('main_form.ui', self)
        
        self.run_btn = self.findChild(QPushButton, 'run_btn')
        self.run_btn.clicked.connect(self.run_topics_analyser)

        self.browse_btn = self.findChild(QPushButton, 'browse_btn')
        self.browse_btn.clicked.connect(self.getfile)
       
        self.data_file_txt = self.findChild(QLineEdit, 'data_file_txt')
        self.num_topics_spb = self.findChild(QSpinBox, 'num_topics_spb')
        self.num_ngrams_spb = self.findChild(QSpinBox, 'num_ngrams_spb')
        self.groupby_cols_txt = self.findChild(QLineEdit, 'groupby_cols_txt')
        self.addl_stopwords_txt = self.findChild(QLineEdit, 'addl_stopwords_txt')
       
        # TODO: add field validations
        rx = QRegExp('^(?!\s*$).+')
        validator = QRegExpValidator(rx, self.data_file_txt)
        self.data_file_txt.setValidator(validator)
        
        self.show()
        
    def run_topics_analyser(self):
        groupby_cols_text = self.groupby_cols_txt.text()
        groupby_cols = [col.strip() for col in groupby_cols_text.split(',')]  if (len(groupby_cols_text) > 0) else []

        addl_stopwords_text = self.addl_stopwords_txt.text()
        addl_stopwords = [sw.strip() for sw in addl_stopwords_text.split(',')] if (len(addl_stopwords_text) > 0) else []

        analyser = TopicsAnalyser(self.data_file_txt.text())
        message = analyser.get_topics(self.num_topics_spb.value(), groupby_cols, self.num_ngrams_spb.value(), addl_stopwords)
        self.statusBar().showMessage(message)


    def getfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.data_file_txt.setText(filename)        

        
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
sys.exit(app.exec_())

        