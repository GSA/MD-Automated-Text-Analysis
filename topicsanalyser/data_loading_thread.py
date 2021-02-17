from textfilereader import TextFileReader
from PyQt5.QtCore import QThread, pyqtSignal

class DataLoading_Thread(QThread):
    finished = pyqtSignal()
    
    def __init__(self, data_reader: TextFileReader):
        QThread.__init__(self)
        self.data_reader = data_reader
        
    def run(self) -> None:
        self.data_reader.read_data()
        self.finished.emit()