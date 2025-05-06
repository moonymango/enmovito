"""
Enmovito - Engine Monitoring Visualization Tool

This is the main entry point for the Enmovito application.
It initializes the application and creates the main window.
"""

import sys
import plotly.io as pio
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from enmovito.gui.main_window import MainWindow

# Set Qt attribute before creating QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Set plotly renderer for PyQt
pio.renderers.default = "browser"

# Set plotly dark theme as default
pio.templates.default = "plotly_dark"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()  # Start in maximized (full screen) mode
    sys.exit(app.exec_())
