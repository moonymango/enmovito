from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from window import Ui_MainWindow
import pyqtgraph as pg
import numpy as np

class App(Ui_MainWindow):
    def __init__(self, win):
        super().__init__()
        self.setupUi(win)
        self.pushButton.clicked.connect(self.on_click)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        
        # Add the plot widget to the central widget layout
        self.centralwidget.layout().addWidget(self.plot_widget)
        
        # Plot some data
        self.plot_data()

    def on_click(self):
        print('PyQt5 button click')

    def plot_data(self):
        # Generate some data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        # Plot the data
        self.plot_widget.plot(x, y)


def window():
    app = QApplication(sys.argv)

    #with open('SyNet.qss', 'r') as f:
    #    app.setStyleSheet(f.read())

    
    win = QMainWindow()
    
    myapp = App(win)

    win.showMaximized()
    sys.exit(app.exec_())
     
window() 