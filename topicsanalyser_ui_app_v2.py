import sys
from PyQt5.QtCore import QRegExp, Qt
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
        self.ui.DataFilePage.validatePage = self.validate_data_file_info
        
        self.ui.browse_btn.clicked.connect(self.getfile)     
        self.ui.run_btn.clicked.connect(self.run_topics_analyser)
        self.ui.add_col_btn.clicked.connect(self.add_other_col_for_import)
        self.ui.remove_col_btn.clicked.connect(self.remove_other_col_for_import)
         
        
                
    def run_topics_analyser(self):        

        def get_wordlist(string_: str):
            return [word.strip() for word in string_.split(',')] if (len(string_) > 0) else []
        
        addl_stopwords = get_wordlist(self.ui.addl_stopwords_txt.text())       
        groupby_cols = [ self.ui.groupby_cols_lst.item(i).text() for i in range(self.ui.groupby_cols_lst.count()) if self.ui.groupby_cols_lst.item(i).checkState() == Qt.Checked]
        
        data = TextFileReader.get_dataframe(self.ui.data_file_txt.text(), self.ui.text_col_name_txt.text(), groupby_cols)
        
        analyser = TopicsAnalyser(data)
        message = analyser.get_topics(self.ui.num_topics_spb.value(), groupby_cols, self.ui.num_ngrams_spb.value(), addl_stopwords)
        # self.ui.statusbar.showMessage(message)
        
        
    def getfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.ui.data_file_txt.setText(filename)
            
            
    def validate_data_file_info(self):
        #TODO: validate the text column name and the other additional columns
        
        # assuming the validation passes
        self.ui.groupby_cols_lst.clear()
        for i in range(self.ui.other_cols_lst.count()):
            item = self.ui.other_cols_lst.item(i).clone()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.ui.groupby_cols_lst.addItem(item)
            
        return True
    
    
    def add_other_col_for_import(self):
        if (self.ui.other_col_txt.text() != ''):
            if (self.ui.other_cols_lst.findItems(self.ui.other_col_txt.text(), Qt.MatchFixedString) == True):
                # TODO: check duplicates
                pass
            
            self.ui.other_cols_lst.addItem(self.ui.other_col_txt.text())
            self.ui.other_col_txt.setText('')
    
    
    def remove_other_col_for_import(self):
        if (self.ui.other_cols_lst.currentRow() != -1):
            self.ui.other_cols_lst.takeItem(self.ui.other_cols_lst.currentRow())
    
   
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
window.show()
sys.exit(app.exec_())

        