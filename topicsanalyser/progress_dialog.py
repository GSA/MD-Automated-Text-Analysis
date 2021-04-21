from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QRect

class ProgressDialog:
    def __init__(self, title: str = "Task is running, please wait...", parent = None, cancel_button: str = None, minimum: int = 0, maximum: int = 0):
        self.progress = QProgressDialog(title, cancel_button, minimum, maximum, parent) 
        self.progress.setGeometry(QRect(0,0,300,200))
        self.progress.setWindowModality(Qt.WindowModal)

