import sys
from mylogging import MyLogging
import ntpath, re
from textfilereader import TextFileReader
from topicsanalyser import TopicsAnalyser
from progress_dialog import ProgressDialog
from topics_modeling_wizard import Ui_TopicsModelingWizard
from utils.exception_formats import system_hook_format
from worker import Worker
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import (
    QWizard,
    QApplication, 
    QFileDialog, 
    QMessageBox,
    QStyle
)

class TopicsAnalyser_UI(QWizard):
    def __init__(self, parent=None):
        super(TopicsAnalyser_UI, self).__init__(parent)
        self.ui = Ui_TopicsModelingWizard()
        self.ui.setupUi(self)
        self.msg = QMessageBox(parent=self)
        
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
        self.ui.DataFilePage.validatePage = self._validate_data_file_page
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
        sys.excepthook = self.uncaught_exception_handler
        
        # instantiate the thread pool
        self.threadpool = QThreadPool() 
        # set the maximum number of tuning trials     
        self.n_trials = 100
           
                
    def run_topics_analyser(self) -> None: 
        if (len(self.ui.output_file_name_txt.text().strip()) == 0):
            self._show_message(['Please enter the output file name.'], icon=QMessageBox.Warning)
            return
            
        get_wordlist = lambda text: [word.strip() for word in text.split(',')] if (len(text) > 0) else []        
        self.addl_stopwords = get_wordlist(self.ui.addl_stopwords_txt.text())       
        self.groupby_cols = self._get_groupby_cols()       
        self.data = self.data_reader.get_dataframe(self.ui.text_col_name_txt.text(), self.groupby_cols) 
        self.output_filename=self.ui.output_file_name_txt.text()
        self.num_ngrams=self.ui.num_ngrams_spb.value()
        self.num_topics=self.ui.num_topics_spb.value()
        # use the input file name as the Optuna study name
        self.studyname = re.sub(r'[.]\w+','', ntpath.basename(self.ui.data_file_txt.text()))  
        # log the analysis  
        self.logger.info(f'Start Topics Analysis:\n{self._get_analysis_inputs_summary()}')
        # create a worker thread for the TopicsAnalyser 
        worker = Worker(self.execute_analysis)
        # connect the signals to the slots (callback functions)
        worker.signals.progress.connect(self.on_analysis_progress)
        worker.signals.result.connect(self.on_analysis_success)
        worker.signals.error.connect(self.on_thread_error)
        # Execute the worker thread
        self.threadpool.start(worker)
        # show a progress dialog while the TopicsAnalyser is running
        self.analysis_progress = ProgressDialog('Analysis is running, please wait...', self).progress
        self.analysis_progress.setValue(1)
        self.analysis_progress.show()
        
        
    def _get_groupby_cols(self) -> list:
        return [ self.ui.groupby_cols_lst.item(i).text() for i in range(self.ui.groupby_cols_lst.count()) if self.ui.groupby_cols_lst.item(i).checkState() == Qt.Checked]
    
        
    def getfile(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel files (*.xlsx)", options=options) 
        if (filename):
            self.ui.data_file_txt.setText(filename)
            # create a worker thread for data loading 
            worker = Worker(self.execute_dataloading, filename)
            # connect the signals to the slots (callback functions)
            worker.signals.finished.connect(self.on_dataloading_success)
            worker.signals.error.connect(self.on_thread_error)
            # Execute the worker thread
            self.threadpool.start(worker)
            self.dataloading_progress = ProgressDialog('Loading data, please wait...', self).progress
            self.dataloading_progress.setValue(1)
            self.dataloading_progress.show()
            
            
    def _validate_data_file_page(self) -> bool:
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
            self._show_message(errors)
            
        return isvalid
    
    
    def init_modeling_page(self) -> None:
        # copy the other column names for grouping use
        self._copy_other_col_names()
                   
        
    def _show_message(self, msgs: list, buttons_shown: int= QMessageBox.Ok, icon: int= QMessageBox.Critical) -> None:
        self.msg.setIcon(icon)
        self.msg.setText(('').join(msgs))
        self.msg.setStandardButtons(buttons_shown)
        self.msg.exec()
        
        
    def _copy_other_col_names(self) -> None:
        self.ui.groupby_cols_lst.clear()
        for i in range(self.ui.other_cols_lst.count()):
            item = self.ui.other_cols_lst.item(i).clone()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.ui.groupby_cols_lst.addItem(item)
        
    
    def add_other_col_for_import(self) -> None:
        other_col = self.ui.other_col_txt.text()
        if (other_col != ''):
            cols_existed = self.ui.other_cols_lst.findItems(other_col, Qt.MatchCaseSensitive)
            if (len(cols_existed) > 0):
                self._show_message([f'Column "{other_col}" was already added.'], icon=QMessageBox.Warning)
                return
            other_cols_limit = 5
            if (self.ui.other_cols_lst.count() == other_cols_limit):
                self._show_message([f'Only up to {other_cols_limit} other columns are allowed.'], icon=QMessageBox.Warning)
                return
                
            self.ui.other_cols_lst.addItem(other_col)
            self.ui.other_col_txt.setText('')
    
    
    def remove_other_col_for_import(self) -> None:
        if (self.ui.other_cols_lst.currentRow() != -1):
            self.ui.other_cols_lst.takeItem(self.ui.other_cols_lst.currentRow())
            
        
    def uncaught_exception_handler(self, type, value, traceback) -> None:
        log_msg = system_hook_format(type, value, traceback, self._get_analysis_inputs_summary())
        self.logger.exception(log_msg)
        
        # show a simplified error message to user
        disp_msg = "An unexpected error occurred below -\n" \
                f"Type: {type}\n" \
                f"Value: {value}\n\n" \
                "The error has been logged for debugging."
        self._show_message(disp_msg)
        
        # close all progress dialogs if open
        if self.dataloading_progress is not None:
            self.dataloading_progress.close()
        if self.analysis_progress is not None:
            self.analysis_progress.close()


    def _get_analysis_inputs_summary(self):
        na = 'N/A'
        datafile = na if self.ui.data_file_txt.text() is None else ntpath.basename(self.ui.data_file_txt.text()) 
        filesize = na if self.data_reader.filesize is None else f'{self.data_reader.filesize/(1000*1000):.2f} MB'
        max_nums_topics = self.ui.num_topics_spb.value()
        nums_ngrams = self.ui.num_ngrams_spb.value()
        txt_col = self.ui.text_col_name_txt.text()
        grp_cols = na if len(self._get_groupby_cols()) == 0 else ','.join(self._get_groupby_cols())
        
        return f"Data file: {datafile}\n" \
            f"File size: {filesize}\n" \
            f"Max. # of topics: {max_nums_topics}\n" \
            f"# of N-grams: {nums_ngrams}\n" \
            f"Text column: '{txt_col}'\n" \
            f"Grouping columns: {grp_cols}"

    # progess_signal is expected to pass to the worker function even though it may not be used
    def execute_dataloading(self, filename, progress_signal) -> None:
        self.data_reader.data_file_path = filename
        self.data_reader.read_data()

            
    def on_dataloading_success(self) -> None:
        self.dataloading_progress.close()
    
    
    def execute_analysis(self, progress_signal) -> str:
        analyser = TopicsAnalyser(self.data, self.output_filename, studyname=self.studyname, n_trials=self.n_trials, progress_signal=progress_signal)
        mod_msg = analyser.get_topics(self.num_topics, self.groupby_cols, self.num_ngrams, self.addl_stopwords)
        return mod_msg


    def on_analysis_progress(self, status: object) -> None:
        # update the status on the progress dialog
        msg = f"Tuning for:\n{status['study']}\nTrial #: {status['num_trial']}\n"
        self.analysis_progress.setLabelText(msg)


    def on_analysis_success(self, msg: str) -> None:
        self.analysis_progress.close()
        messages = ['Topics analysis is done.\n', msg]    
        self._show_message(messages, icon=QMessageBox.Information)
        
        
    def on_thread_error(self, error_info : tuple) -> None:
        self.uncaught_exception_handler(*error_info)
        
        
app = QApplication(sys.argv)
window = TopicsAnalyser_UI()
window.show()
sys.exit(app.exec_())

        