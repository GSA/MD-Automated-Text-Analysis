import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from textfilereader import TextFileReader
from topicsanalyser import TopicsAnalyser
from topics_modeling_wizard import Ui_TopicsModelingWizard
from PyQt5.QtWidgets import (
    # QMainWindow,
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
        self.setWindowTitle('GSA Topics Modeling Tool')
        self.resize(719, 410)
        
        self.ui.browse_btn.clicked.connect(self.getfile)
        self.ui.DataFilePage.validatePage = self.validate_file_inputs
        self.ui.TopicsModelingPage.validatePage = self.run_topics_analyser
                
        self.setup_validators()
        
    def run_topics_analyser(self):        
        status = self.validate_inputs()
        if (status != 0):
            return

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
        return True
        

    def setup_validators(self):
       # check if the text is an empty string
        rx = QRegExp('^(?!\\s*$).+')
        self.filename_validator = QRegExpValidator(rx)

    def validate_inputs(self):
        self.error_dialog = QErrorMessage()
        errors = []
        filename_val_status, _, _ = self.filename_validator.validate(self.ui.data_file_txt.text(), 0)
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
            self.ui.data_file_txt.setText(filename)        

    def validate_file_inputs(self):
        # TODO
        return True
   
   
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
window.show()
sys.exit(app.exec_())

        