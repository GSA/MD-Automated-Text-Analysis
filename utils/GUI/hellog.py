import sys 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDialog




class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('LDA Text Analysis')
        layout = QFormLayout()
        layout.addRow('File Path *', QLineEdit())
        layout.addRow('Number of Topics', QLineEdit())
        layout.addRow ('Number of N Grams', QLineEdit())
        layout.addRow ('Enter Additional Stop Words', QLineEdit())
        layout.addRow(QLabel('<p> * denotes a required field'))
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
