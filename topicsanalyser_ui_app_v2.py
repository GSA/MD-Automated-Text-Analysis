import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from textfilereader import TextFileReader
from topicsanalyser import TopicsAnalyser
from topics_modeling_wizard import Ui_TopicsModelingWizard
from PyQt5.QtWidgets import (
    QWizard,
    QWizardPage,
    QApplication, 
    QFileDialog, 
    QErrorMessage
)

class TopicsAnalyser_UI(QWizard):
    def __init__(self, parent=None):
        super(TopicsAnalyser_UI, self).__init__(parent)
        self.ui = Ui_TopicsModelingWizard()
        self.ui.setupUi(self)
        # register the fields to make them required
        self.ui.DataFilePage.registerField('data_file_txt*', self.ui.data_file_txt)
        self.ui.DataFilePage.registerField('text_col_name_txt*', self.ui.text_col_name_txt)
        
        self.ui.browse_btn.clicked.connect(self.getfile)     
        self.ui.run_btn.clicked.connect(self.run_topics_analyser)
         
                
    def run_topics_analyser(self):        

        def get_wordlist(string_: str):
            return [word.strip() for word in string_.split(',')] if (len(string_) > 0) else []
        
        groupby_cols = get_wordlist(self.ui.groupby_cols_txt.text())
        addl_stopwords = get_wordlist(self.ui.addl_stopwords_txt.text())
        
        # TODO: these column names should come from the input screen
        text_col = 'Reason for filling position(s) with Federal Government Employee -OTHER'
        # text_col = 'Please briefly describe an example of one burdensome administrative task or process which you believe is "low value"'
        other_cols = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS']
        data = TextFileReader.get_dataframe(self.ui.data_file_txt.text(), text_col, other_cols)
        
        analyser = TopicsAnalyser(data)
        message = analyser.get_topics(self.ui.num_topics_spb.value(), groupby_cols, self.ui.num_ngrams_spb.value(), addl_stopwords)
        self.ui.statusbar.showMessage(message)
        
        
    def getfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.ui.data_file_txt.setText(filename)
            
   
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
window.show()
sys.exit(app.exec_())

        