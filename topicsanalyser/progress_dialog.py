from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QRect

class ProgressDialog:
    def __init__(self, title: str = "Task is running, please wait...", parent = None):
        self.progress = QProgressDialog(title, None, 0, 0, parent) 
        self.progress.setGeometry(QRect(0,0,300,200))
        self.progress.setWindowModality(Qt.WindowModal)

    def show(self):
        self.progress.setValue(1)
        self.progress.show()
        
    def close(self):
        self.progress.close()
        