from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QSpinBox, QFileDialog, QErrorMessage, QProgressBar
from PyQt5.QtCore import QRegExp, QBasicTimer
from PyQt5.QtGui import QRegExpValidator
import sys
from textfilereader import TextFileReader
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
        
        self.setup_validators()

        self.show()
        
    def run_topics_analyser(self):        
        status = self.validate_inputs()
        if (status != 0):
            return

        groupby_cols_text = self.groupby_cols_txt.text()
        groupby_cols = [col.strip() for col in groupby_cols_text.split(',')]  if (len(groupby_cols_text) > 0) else []

        addl_stopwords_text = self.addl_stopwords_txt.text()
        addl_stopwords = [sw.strip() for sw in addl_stopwords_text.split(',')] if (len(addl_stopwords_text) > 0) else []

        # TODO: these column names should come from the input screen
        text_col = 'Reason for filling position(s) with Federal Government Employee -OTHER'
        other_cols = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS']
        data = TextFileReader.get_dataframe(self.data_file_txt.text(), text_col, other_cols)
        
        analyser = TopicsAnalyser(data)
        message = analyser.get_topics(self.num_topics_spb.value(), groupby_cols, self.num_ngrams_spb.value(), addl_stopwords)
        self.statusBar().showMessage(message)

    def setup_validators(self):
        # TODO: add field validations
        # check if the text is an empty string
        rx = QRegExp('^(?!\\s*$).+')
        self.filename_validator = QRegExpValidator(rx)

    def validate_inputs(self):
        self.error_dialog = QErrorMessage()
        errors = []
        filename_val_status, _, _ = self.filename_validator.validate(self.data_file_txt.text(), 0)
        if (filename_val_status != 2):
            errors.append('Data file is required.')

        if (len(errors) > 0):
            self.error_dialog.showMessage('\n'.join(errors))
            return -1
        return 0

    def getfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.data_file_txt.setText(filename)        

        
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
sys.exit(app.exec_())

        