from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
 
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(400, 400, 500, 300)
        self.setWindowTitle("CodersLegacy")
        self.initUI()
 
    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText('hello window')
 
        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText('hello button')
        self.btn.move(100, 100)
        self.btn.clicked.connect(self.onClick)
 
    def onClick(self):
        self.label.setText('hello button clicked')
        self.update()
 
    def update(self):
        self.label.adjustSize()


    

def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
     
window() 