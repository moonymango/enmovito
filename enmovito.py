import sys
import os
import plotly.io as pio
from enmovito.data_handler import DataHandler
from enmovito.gui.visualization import VisualizationPanel
from enmovito.gui.control_panel import ControlPanel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QFileDialog, QSplitter
)
# Set Qt attribute before creating QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Set plotly renderer for PyQt
pio.renderers.default = "browser"


# Set plotly dark theme as default
pio.templates.default = "plotly_dark"


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(f"Running from PyInstaller bundle. MEIPASS: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        print(f"Running from source. Base path: {base_path}")

    return os.path.join(base_path, relative_path)


class Enmovito(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enmovito")
        self.setGeometry(100, 100, 1200, 800)

        # Apply dark theme
        self.apply_dark_theme()

        # Initialize data handler
        self.data_handler = DataHandler()
        self.time_column = "Lcl Time"  # Default time column

        # Initialize empty lists for backward compatibility
        self.ts_browsers = []
        self.xy_browsers = []

        # Placeholders for error handling
        self.plot_placeholder = QLabel("Select a log file and parameters to visualize")

        # Create the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create a splitter for resizable sections
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Create the control panel (left side)
        self.control_panel = ControlPanel(self, self.data_handler)
        self.splitter.addWidget(self.control_panel)
        
        # Connect signals from the control panel
        self.control_panel.plot_requested.connect(self.on_plot_requested)
        self.control_panel.temperature_unit_changed.connect(self.on_temperature_unit_changed)
        self.control_panel.theme_changed.connect(self.on_theme_changed)
        
        # Connect the file button to the select_file method
        self.control_panel.file_button.clicked.connect(self.select_file)
        
        # Create the visualization panel (right side)
        self.viz_panel = VisualizationPanel(self)
        self.splitter.addWidget(self.viz_panel)

        # Set the initial sizes of the splitter
        self.splitter.setSizes([300, 900])
        
        # Get references to visualization panel components
        self.plot_tabs = self.viz_panel.plot_tabs
        self.tab_plot_browsers = self.viz_panel.tab_plot_browsers
        self.tab_figures = self.viz_panel.tab_figures
        self.tab_x_params = self.viz_panel.tab_x_params

        # Set the default directory to example_logs
        self.default_dir = os.path.join(os.getcwd(), "example_logs")
        
    def on_plot_requested(self, selected_params, selected_display_names, x_param, x_display):
        """Handle plot requested signal from the control panel."""
        # Filter out non-numeric parameters
        numeric_params = []
        numeric_display_names = []
        for i, param in enumerate(selected_params):
            if param in self.numeric_columns:
                numeric_params.append(param)
                numeric_display_names.append(selected_display_names[i])

        if not numeric_params:
            self.plot_placeholder.setText("Please select at least one numeric parameter to plot")
            return
            
        # Generate the plot using the visualization panel
        success = self.viz_panel.generate_plot(
            self.df, 
            numeric_params, 
            numeric_display_names, 
            x_param, 
            x_display, 
            self.log_file_path,
            self.data_handler.get_temperature_unit(),
            self.data_handler.fahrenheit_to_celsius
        )
        
        if not success:
            self.plot_placeholder.setText("Failed to generate plot")
        
    def on_temperature_unit_changed(self, use_celsius):
        """Handle temperature unit changed signal from the control panel."""
        self.data_handler.set_temperature_unit(use_celsius)
        self.regenerate_plots_with_new_unit()
        
    def on_theme_changed(self, theme_name):
        """Handle theme changed signal from the control panel."""
        if theme_name == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_theme(self, theme_name="dark"):
        """Apply a theme to the application using QSS from an external file.

        Args:
            theme_name (str): The name of the theme to apply. Default is "dark".
                              Available themes: "dark", "light"
        """
        # Define the path to the theme file using resource_path
        theme_file = resource_path(f"themes/{theme_name}_theme.qss")
        
        print(f"Looking for theme file at: {theme_file}")
        print(f"Current working directory: {os.getcwd()}")
        
        try:
            # Read the stylesheet from the file
            with open(theme_file, "r", encoding='utf-8') as f:
                stylesheet = f.read()

            # Apply the stylesheet
            self.setStyleSheet(stylesheet)
            print(f"Applied {theme_name} theme from {theme_file}")
        except Exception as e:
            print(f"Error loading theme file {theme_file}: {str(e)}")
            # Fallback to default style
            self.setStyleSheet("")
            
            # Apply a minimal fallback theme directly in code
            fallback_style = """
            QWidget { background-color: #2D2D30; color: #E0E0E0; }
            QPushButton { background-color: #444444; color: white; border: none; border-radius: 3px; padding: 5px 10px; }
            QListWidget, QComboBox { background-color: #252526; border: 1px solid #3E3E40; }
            QListWidget::item:selected { background-color: #0E639C; color: white; }
            """
            if theme_name == "dark":
                self.setStyleSheet(fallback_style)
                print("Applied minimal fallback dark theme")

    def apply_dark_theme(self):
        """Apply dark theme to the application using QSS."""
        self.apply_theme("dark")

        # Set dark palette for application
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.Base, QColor(37, 37, 38))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.Text, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 48))
        dark_palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(68, 68, 68))
        dark_palette.setColor(QPalette.Highlight, QColor(68, 68, 68))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        QApplication.setPalette(dark_palette)

    def apply_light_theme(self):
        """Apply light theme to the application using QSS."""
        self.apply_theme("light")

        # Set light palette for application
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, QColor(245, 245, 245))
        light_palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
        light_palette.setColor(QPalette.Text, QColor(51, 51, 51))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(0, 120, 215))
        light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        QApplication.setPalette(light_palette)

    def regenerate_plots_with_new_unit(self):
        """Regenerate all existing plots with the new temperature unit."""
        # Clear all plots from all tabs
        for tab_index in list(self.tab_plot_browsers.keys()):
            # Clear the plot from this tab
            if tab_index in self.tab_plot_browsers and self.tab_plot_browsers[tab_index] is not None:
                # Clear the tab using the visualization panel's method
                self.viz_panel.clear_tab_plot(tab_index)
                
                # Add a placeholder with temperature unit information
                tab = self.plot_tabs.widget(tab_index)
                if tab:
                    tab_layout = tab.layout()
                    placeholder = QLabel(
                        f"Temperature unit changed to {self.get_temp_unit_name()}.\n"
                        "Please generate new plots."
                    )
                    placeholder.setAlignment(Qt.AlignCenter)
                    placeholder.setFont(QFont("Arial", 14))
                    tab_layout.addWidget(placeholder)

    def get_temp_unit_name(self):
        """Get the name of the current temperature unit."""
        return self.data_handler.get_temperature_unit_name()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Log File", self.default_dir, "CSV Files (*.csv)"
        )

        if file_path:
            self.log_file_path = file_path
            self.control_panel.update_file_label(os.path.basename(file_path))
            self.load_data(file_path)

    def load_data(self, file_path):
        """Load data from a CSV file using the data handler."""
        success, error_message = self.data_handler.load_data(file_path)
        
        if success:
            # Get data from the data handler
            self.df = self.data_handler.df
            self.numeric_columns = self.data_handler.get_numeric_columns()
            self.abbr_to_full = self.data_handler.abbr_to_full
            self.full_to_abbr = self.data_handler.full_to_abbr
            
            # Get all columns and their display names
            all_columns = self.data_handler.get_all_columns()
            display_names = self.data_handler.get_display_names()
            
            # Extract display names for the control panel
            display_columns = [name for name, _ in display_names]
            
            # Update the control panel with the loaded data
            self.control_panel.update_parameter_list(
                all_columns, display_columns, self.numeric_columns, self.abbr_to_full
            )
            
            # Show a message
            self.plot_placeholder.setText(
                f"Data loaded from {os.path.basename(file_path)}\n"
                f"Select parameters and click 'Generate Plot'"
            )
        else:
            print(f"Error loading file: {error_message}")
            self.plot_placeholder.setText(f"Error loading file: {error_message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Enmovito()
    window.showMaximized()  # Start in maximized (full screen) mode
    sys.exit(app.exec_())
