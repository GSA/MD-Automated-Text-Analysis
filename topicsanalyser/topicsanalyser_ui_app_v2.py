import sys
import pandas as pd
from mylogging import MyLogging
import ntpath
from textfilereader import TextFileReader
from data_loading_thread import DataLoading_Thread
from topicsanalyser_thread import TopicsAnalyser_Thread
from progress_dialog import ProgressDialog
from topics_modeling_wizard import Ui_TopicsModelingWizard
from utils.exception_formats import system_hook_format
from PyQt5.QtCore import QRegExp, Qt, QRect
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QWizard,
    QWizardPage,
    QApplication, 
    QFileDialog, 
    QErrorMessage,
    QMessageBox,
    QStyle
)

class TopicsAnalyser_UI(QWizard):
    def __init__(self, parent=None):
        super(TopicsAnalyser_UI, self).__init__(parent)
        self.ui = Ui_TopicsModelingWizard()
        self.ui.setupUi(self)
        self.msg = QMessageBox()
        
        # change the icon of the push buttons
        self.ui.add_col_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowForward')))
        self.ui.remove_col_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowBack')))

        # set tooltips on some widgets
        self.ui.other_col_txt.setToolTip(r'Enter the name of a <b>categorical</b> column in the dataset and then press <b>[Enter]</b> or <b>[Add]</b>.')
        self.ui.other_cols_lst.setToolTip('To remove a column, select one from the list and then press <b>[Remove]</b>.')
        self.ui.groupby_cols_lbel.setToolTip('The grouping levels start from the top of list.')
        self.ui.groupby_cols_lst.setToolTip('You can drag and drop to change the order of a column in the list. And select the ones you want for grouping.')
        stop_words_tip = 'Enter optional uncommon stop words separated by commas.'
        self.ui.addl_stopwords_lbl.setToolTip(stop_words_tip)
        self.ui.addl_stopwords_txt.setToolTip(stop_words_tip)
        
        # register the fields to make them required
        self.ui.DataFilePage.registerField('data_file_txt*', self.ui.data_file_txt)
        self.ui.DataFilePage.registerField('text_col_name_txt*', self.ui.text_col_name_txt)
        
        # override some default page functions
        self.ui.DataFilePage.validatePage = self.validate_data_file_page
        self.ui.TopicsModelingPage.initializePage = self.init_modeling_page
        
        # link the signals to the slots
        self.ui.browse_btn.clicked.connect(self.getfile)     
        self.ui.run_btn.clicked.connect(self.run_topics_analyser)
        self.ui.add_col_btn.clicked.connect(self.add_other_col_for_import)
        self.ui.other_col_txt.returnPressed.connect(self.add_other_col_for_import)
        self.ui.remove_col_btn.clicked.connect(self.remove_other_col_for_import)
        
        self.data_reader = TextFileReader()
        
        # set up logger
        self.logger = MyLogging('topicsAnalyserLogger', 'topicsanalyser.log').logger
        # set up the uncaught exceptions handler
        sys.excepthook = self.uncaught_exceptions_hander
                
                
    def run_topics_analyser(self) -> None: 
        if (len(self.ui.output_file_name_txt.text().strip()) == 0):
            self.show_message(['Please enter the output file name.'], icon=QMessageBox.Warning)
            return
            
        get_wordlist = lambda text: [word.strip() for word in text.split(',')] if (len(text) > 0) else []        
        addl_stopwords = get_wordlist(self.ui.addl_stopwords_txt.text())       
        groupby_cols = self.get_groupby_cols()       
        data = self.data_reader.get_dataframe(self.ui.text_col_name_txt.text(), groupby_cols)     
        # create a worker thread for the TopicsAnalyser 
        thread = TopicsAnalyser_Thread(data, self.ui.output_file_name_txt.text(),self.ui.num_topics_spb.value(), groupby_cols, self.ui.num_ngrams_spb.value(), addl_stopwords)
        thread.finished.connect(self.analyser_thread_finished)
        thread.start()
        # show a progress dialog while the TopicsAnalyser is running
        self.analysis_progress = ProgressDialog('Analysis is running, please wait...', self)
        self.analysis_progress.show()
        
        
    def get_groupby_cols(self) -> list:
        return [ self.ui.groupby_cols_lst.item(i).text() for i in range(self.ui.groupby_cols_lst.count()) if self.ui.groupby_cols_lst.item(i).checkState() == Qt.Checked]
    
        
    def getfile(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.ui.data_file_txt.setText(filename)
            # load data
            self.data_reader.data_file_path = filename
            thread = DataLoading_Thread(self.data_reader)
            thread.finished.connect(self.dataloading_thread_finished)
            thread.start()
            self.dataloading_progress = ProgressDialog('Loading data, please wait...', self)
            self.dataloading_progress.show()
            
            
    def validate_data_file_page(self) -> bool:
        isvalid = True
        errors = []
        text_col = self.ui.text_col_name_txt.text()
        cols = [text_col] + [self.ui.other_cols_lst.item(i).text() for i in range(self.ui.other_cols_lst.count())]
        cols_not_exist = self.data_reader.verify_columns_exist(cols)
        if (len(cols_not_exist) > 0):
            errors.extend(['The following column(s) do not exist in the data file: '] + cols_not_exist)
            isvalid = False
        
        if (self.data_reader.is_text_column(text_col) == False):
            errors.extend([f'\n\n"{text_col}" is not a text column.'])
            isvalid = False
        
        if (len(errors) > 0):
            self.show_message(errors)
            
        return isvalid
    
    
    def init_modeling_page(self) -> None:
        # copy the other column names for grouping use
        self.copy_other_col_names()
                   
        
    def show_message(self, msgs: list, buttons_shown: int= QMessageBox.Ok, icon: int= QMessageBox.Critical) -> None:
        self.msg.setIcon(icon)
        self.msg.setText(('').join(msgs))
        self.msg.setStandardButtons(buttons_shown)
        self.msg.exec()
        
        
    def copy_other_col_names(self) -> None:
        self.ui.groupby_cols_lst.clear()
        for i in range(self.ui.other_cols_lst.count()):
            item = self.ui.other_cols_lst.item(i).clone()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.ui.groupby_cols_lst.addItem(item)
        
    
    def add_other_col_for_import(self) -> None:
        other_col = self.ui.other_col_txt.text()
        if (other_col != ''):
            cols_existed = self.ui.other_cols_lst.findItems(other_col, Qt.MatchCaseSensitive)
            if (len(cols_existed) > 0):
                self.show_message([f'Column "{other_col}" was already added.'], icon=QMessageBox.Warning)
                return
            other_cols_limit = 5
            if (self.ui.other_cols_lst.count() == other_cols_limit):
                self.show_message([f'Only up to {other_cols_limit} other columns are allowed.'], icon=QMessageBox.Warning)
                return
                
            self.ui.other_cols_lst.addItem(other_col)
            self.ui.other_col_txt.setText('')
    
    
    def remove_other_col_for_import(self) -> None:
        if (self.ui.other_cols_lst.currentRow() != -1):
            self.ui.other_cols_lst.takeItem(self.ui.other_cols_lst.currentRow())
            
        
    def uncaught_exceptions_hander(self, type, value, traceback) -> None:
        # log error in file with details information
        addl_info = f"Data file: {ntpath.basename(self.ui.data_file_txt.text())}\n" \
            f"File size: {self.data_reader.filesize/(1000*1000):.2f} MB\n" \
            f"No of topics: {self.ui.num_topics_spb.value()}\n" \
            f"No of N-grams: {self.ui.num_ngrams_spb.value()}\n" \
            f"Text column: '{self.ui.text_col_name_txt.text()}'\n" \
            f"Grouping columns: {','.join(self.get_groupby_cols())}"
        log_msg = system_hook_format(type, value, traceback, addl_info)
        self.logger.exception(log_msg)
        
        # show a simplified error message to user
        disp_msg = "An unexpected error occurred below -\n" \
                f"Type: {type}\n" \
                f"Value: {value}\n\n" \
                "The error has been logged for debugging."
        self.show_message(disp_msg)
        
        
    def dataloading_thread_finished(self) -> None:
        self.dataloading_progress.close()
    
    
    def analyser_thread_finished(self, msg: str) -> None:
        self.analysis_progress.close()
        messages = ['Topics analysis is done.\n', msg]    
        self.show_message(messages, icon=QMessageBox.Information)


app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
window.show()
sys.exit(app.exec_())

        