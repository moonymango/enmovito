from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from window import Ui_MainWindow


class App(Ui_MainWindow):
    def __init__(self, win):
        super().__init__()
        self.setupUi(win)
        self.pushButton.clicked.connect(self.on_click)

    def on_click(self):
        print('PyQt5 button click')


def window():
    app = QApplication(sys.argv)

    #with open('SyNet.qss', 'r') as f:
    #    app.setStyleSheet(f.read())

    
    win = QMainWindow()
    
    myapp = App(win)

    win.showMaximized()
    sys.exit(app.exec_())
     
window() 