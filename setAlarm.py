from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('setAlarm.ui', self)

        self.show()
app = QApplication(sys.argv)
window = MainWindow()
app.exec_()