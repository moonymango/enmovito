import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PyQt5.QtCore import Qt, QUrl, QEvent
from PyQt5.QtGui import QFont, QWheelEvent, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QListWidget, QLabel, QFileDialog, QTabWidget, QSplitter,
    QListWidgetItem, QGroupBox, QGridLayout, QSizePolicy, QRadioButton, QButtonGroup,
    QMessageBox, QDialog
)
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QMouseEvent
# Import QtWebEngineWidgets early
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
import plotly.io as pio
from plotly.offline import plot
# Set Qt attribute before creating QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Set plotly renderer for PyQt
pio.renderers.default = "browser"

# Set plotly dark theme as default
pio.templates.default = "plotly_dark"


# Custom QListWidget with shift-click selection
class ShiftSelectListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_selected_item = None
        self.setSelectionMode(QListWidget.MultiSelection)
        
    def mousePressEvent(self, event):
        """Override mouse press event to handle shift-click selection."""
        if event.modifiers() & Qt.ShiftModifier:
            # Get the item at the clicked position
            item = self.itemAt(event.pos())
            if item and self.last_selected_item:
                # Get the indices of the current and last selected items
                current_index = self.row(item)
                last_index = self.row(self.last_selected_item)
                
                # Determine the range to select
                start_index = min(current_index, last_index)
                end_index = max(current_index, last_index)
                
                # Select all items in the range
                for i in range(start_index, end_index + 1):
                    item_to_select = self.item(i)
                    if not item_to_select.isHidden():
                        item_to_select.setSelected(True)
                
                # Update the last selected item
                self.last_selected_item = item
                return
            
        # Call the parent class implementation for normal click behavior
        super().mousePressEvent(event)
        
        # Update the last selected item
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                self.last_selected_item = item


# Custom dialog for X-axis change warning
class XAxisChangeDialog(QDialog):
    def __init__(self, parent=None, old_x_param="", new_x_param=""):
        super().__init__(parent)
        self.setWindowTitle("X-Axis Change Warning")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add warning message
        message = QLabel(
            f"<b>Warning:</b> Changing the X-axis parameter from '{old_x_param}' to '{new_x_param}' "
            "will make the plot inconsistent.\n\n"
            "What would you like to do?"
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        # Abort button
        self.abort_button = QPushButton("Abort")
        self.abort_button.clicked.connect(self.reject)
        button_layout.addWidget(self.abort_button)
        
        # Replace button
        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.accept)
        button_layout.addWidget(self.replace_button)
        
        layout.addLayout(button_layout)


# Custom QWebEngineView with wheel event handling
class ZoomableWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPage(QWebEnginePage(self))
        
    def wheelEvent(self, event):
        # Pass wheel events to the web page for zooming
        super().wheelEvent(event)
        
        # Execute JavaScript to simulate wheel event on the Plotly graph
        delta = event.angleDelta().y()
        script = f"""
        var evt = new WheelEvent('wheel', {{
            deltaY: {-delta},
            clientX: {event.position().x()},
            clientY: {event.position().y()}
        }});
        document.getElementsByClassName('plotly')[0].dispatchEvent(evt);
        """
        self.page().runJavaScript(script)


class EngineDataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engine Data Log Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Data storage
        self.df = None
        self.log_file_path = None
        self.numeric_columns = []
        self.time_column = "Lcl Time"  # Default time column
        self.use_celsius = False  # Default to Fahrenheit
        
        # Initialize empty lists for backward compatibility
        self.ts_browsers = []
        self.xy_browsers = []
        
        # Placeholders for error handling
        self.plot_placeholder = QLabel("Select a log file and parameters to visualize")
        self.xy_plot_placeholder = QLabel("Select X and Y parameters for XY plot")
        
        # Create the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create a splitter for resizable sections
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Create the control panel (left side)
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout(self.control_panel)
        self.splitter.addWidget(self.control_panel)
        
        # Create the visualization panel (right side)
        self.viz_panel = QWidget()
        self.viz_layout = QVBoxLayout(self.viz_panel)
        self.splitter.addWidget(self.viz_panel)
        
        # Set the initial sizes of the splitter
        self.splitter.setSizes([300, 900])
        
        # Setup the control panel
        self.setup_control_panel()
        
        # Setup the visualization panel
        self.setup_viz_panel()
        
        # Set the default directory to example_logs
        self.default_dir = os.path.join(os.getcwd(), "example_logs")

    def apply_theme(self, theme_name="dark"):
        """Apply a theme to the application using QSS from an external file.
        
        Args:
            theme_name (str): The name of the theme to apply. Default is "dark".
                              Available themes: "dark", "light"
        """
        # Define the path to the theme file
        theme_file = f"themes/{theme_name}_theme.qss"
        
        try:
            # Read the stylesheet from the file
            with open(theme_file, "r") as f:
                stylesheet = f.read()
            
            # Apply the stylesheet
            self.setStyleSheet(stylesheet)
            print(f"Applied {theme_name} theme from {theme_file}")
        except Exception as e:
            print(f"Error loading theme file {theme_file}: {str(e)}")
            # Fallback to default style
            self.setStyleSheet("")
    
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
    
    def setup_control_panel(self):
        # Common parameter categories - using abbreviated names
        # These will be converted to full names when needed
        self.categories = {
            "GPS": ["Latitude", "Longitude", "AltGPS", "GndSpd", "TRK"],
            "Altitude": ["AltP", "AltInd", "VSpd", "AGL"],
            "Attitude": ["Pitch", "Roll", "HDG"],
            "Engine": ["E1 RPM", "E1 MAP", "E1 %Pwr", "E1 FFlow", "E1 OilT", "E1 OilP"],
            "Temperature": [
                "E1 CHT1", "E1 CHT2", "E1 CHT3", "E1 CHT4", "E1 CHT5", "E1 CHT6",
                "E1 EGT1", "E1 EGT2", "E1 EGT3", "E1 EGT4", "E1 EGT5", "E1 EGT6"
            ],
            "Electrical": ["Volts1", "Volts2", "Amps1"]
        }
        
        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # File selection button
        self.file_button = QPushButton("Select Log File")
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_button)
        
        # Display selected file
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        self.control_layout.addWidget(file_group)
        
        # X-axis selection
        x_axis_group = QGroupBox("X-Axis Selection")
        x_axis_layout = QVBoxLayout()
        
        # X-axis parameter list with selection controls
        x_axis_header = QHBoxLayout()
        x_axis_header.addWidget(QLabel("Select X-Axis Parameter:"))
        
        # Add "Show All" button for X-axis
        self.show_all_x_btn = QPushButton("Show All")
        self.show_all_x_btn.clicked.connect(self.show_all_x_parameters)
        self.show_all_x_btn.setEnabled(False)  # Initially disabled until file is loaded
        x_axis_header.addWidget(self.show_all_x_btn)
        
        # Add "Clear Selection" button for X-axis
        self.clear_x_selection_btn = QPushButton("Clear Selection")
        self.clear_x_selection_btn.clicked.connect(self.clear_x_parameter_selection)
        self.clear_x_selection_btn.setEnabled(False)  # Initially disabled until file is loaded
        x_axis_header.addWidget(self.clear_x_selection_btn)
        
        x_axis_layout.addLayout(x_axis_header)
        
        # Use a list widget with single selection mode for X-axis
        self.x_axis_list = QListWidget()
        self.x_axis_list.setSelectionMode(QListWidget.SingleSelection)  # Only one item can be selected
        x_axis_layout.addWidget(self.x_axis_list)
        
        # Quick parameter category selection for X-axis
        x_category_layout = QGridLayout()
        
        # Create a separate set of category buttons for X-axis
        row, col = 0, 0
        self.x_category_buttons = {}
        for category, params in self.categories.items():
            btn = QPushButton(category)
            btn.setProperty("category_params", params)
            btn.clicked.connect(self.select_x_category)
            x_category_layout.addWidget(btn, row, col)
            self.x_category_buttons[category] = btn
            col += 1
            if col > 2:  # 3 buttons per row
                col = 0
                row += 1
        
        x_axis_layout.addLayout(x_category_layout)
        
        x_axis_group.setLayout(x_axis_layout)
        self.control_layout.addWidget(x_axis_group)
        
        # Parameter selection section
        param_group = QGroupBox("Parameter Selection")
        param_layout = QVBoxLayout()
        
        # No separate time column selection needed
        
        # Parameter list with selection controls
        param_list_header = QHBoxLayout()
        param_list_header.addWidget(QLabel("Select Parameters to Plot:"))
        
        # Add "Show All" button
        self.show_all_btn = QPushButton("Show All")
        self.show_all_btn.clicked.connect(self.show_all_parameters)
        self.show_all_btn.setEnabled(False)  # Initially disabled until file is loaded
        param_list_header.addWidget(self.show_all_btn)
        
        # Add "Select All Visible" button
        self.select_all_visible_btn = QPushButton("Select All Visible")
        self.select_all_visible_btn.clicked.connect(self.select_all_visible_parameters)
        self.select_all_visible_btn.setEnabled(False)  # Initially disabled until file is loaded
        param_list_header.addWidget(self.select_all_visible_btn)
        
        # Add "Clear Selection" button
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_parameter_selection)
        self.clear_selection_btn.setEnabled(False)  # Initially disabled until file is loaded
        param_list_header.addWidget(self.clear_selection_btn)
        
        param_layout.addLayout(param_list_header)
        
        # Use our custom list widget with shift-click selection
        self.param_list = ShiftSelectListWidget()
        param_layout.addWidget(self.param_list)
        
        # Quick parameter category selection
        category_layout = QGridLayout()
        
        row, col = 0, 0
        self.category_buttons = {}
        for category, params in self.categories.items():
            btn = QPushButton(category)
            btn.setProperty("category_params", params)
            btn.clicked.connect(self.select_category)
            category_layout.addWidget(btn, row, col)
            self.category_buttons[category] = btn
            col += 1
            if col > 2:  # 3 buttons per row
                col = 0
                row += 1
        
        param_layout.addLayout(category_layout)
        
        # Plot button
        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.clicked.connect(self.generate_plot)
        self.plot_button.setEnabled(False)
        param_layout.addWidget(self.plot_button)
        
        param_group.setLayout(param_layout)
        self.control_layout.addWidget(param_group)
        
        # Add stretch to push everything to the top and leave space at the bottom
        self.control_layout.addStretch()
        
        # Add theme selection section at the bottom of the control pane
        self.setup_theme_selection()

    def setup_theme_selection(self):
        """Setup theme selection radio buttons."""
        # Create a group box for temperature unit selection
        temp_unit_group = QGroupBox("Temperature Unit")
        temp_unit_layout = QHBoxLayout()
        
        # Create radio buttons for temperature unit selection
        self.temp_unit_button_group = QButtonGroup(self)
        
        # Fahrenheit radio button
        self.fahrenheit_radio = QRadioButton("Fahrenheit (°F)")
        self.fahrenheit_radio.setChecked(True)  # Default to Fahrenheit
        self.fahrenheit_radio.clicked.connect(self.set_fahrenheit)
        self.temp_unit_button_group.addButton(self.fahrenheit_radio)
        temp_unit_layout.addWidget(self.fahrenheit_radio)
        
        # Celsius radio button
        self.celsius_radio = QRadioButton("Celsius (°C)")
        self.celsius_radio.clicked.connect(self.set_celsius)
        self.temp_unit_button_group.addButton(self.celsius_radio)
        temp_unit_layout.addWidget(self.celsius_radio)
        
        temp_unit_group.setLayout(temp_unit_layout)
        self.control_layout.addWidget(temp_unit_group)
        
        # Create a group box for theme selection
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QHBoxLayout()
        
        # Create radio buttons for theme selection
        self.theme_button_group = QButtonGroup(self)
        
        # Dark theme radio button
        self.dark_theme_radio = QRadioButton("Dark")
        self.dark_theme_radio.setChecked(True)  # Default to dark theme
        self.dark_theme_radio.clicked.connect(self.apply_dark_theme)
        self.theme_button_group.addButton(self.dark_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        
        # Light theme radio button
        self.light_theme_radio = QRadioButton("Light")
        self.light_theme_radio.clicked.connect(self.apply_light_theme)
        self.theme_button_group.addButton(self.light_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)
        
        theme_group.setLayout(theme_layout)
        self.control_layout.addWidget(theme_group)
    
    def set_fahrenheit(self):
        """Set temperature unit to Fahrenheit."""
        self.use_celsius = False
        # Regenerate any existing plots with the new unit
        self.regenerate_plots_with_new_unit()
    
    def set_celsius(self):
        """Set temperature unit to Celsius."""
        self.use_celsius = True
        # Regenerate any existing plots with the new unit
        self.regenerate_plots_with_new_unit()
    
    def regenerate_plots_with_new_unit(self):
        """Regenerate all existing plots with the new temperature unit."""
        # Initialize tab_plot_browsers if it doesn't exist
        if not hasattr(self, 'tab_plot_browsers'):
            self.tab_plot_browsers = {}
            
        # Clear all plots from all tabs
        for tab_index in list(self.tab_plot_browsers.keys()):
            # Get the tab
            tab = self.plot_tabs.widget(tab_index)
            if tab:
                # Clear the plot from this tab
                if tab_index in self.tab_plot_browsers and self.tab_plot_browsers[tab_index] is not None:
                    # Clear the tab layout
                    tab_layout = tab.layout()
                    while tab_layout.count():
                        item = tab_layout.takeAt(0)
                        widget = item.widget()
                        if widget:
                            widget.setParent(None)
                    
                    # Reset the browser reference
                    self.tab_plot_browsers[tab_index] = None
                    self.tab_figures[tab_index] = None
                    
                    # Add a placeholder
                    placeholder = QLabel(
                        f"Temperature unit changed to {self.get_temp_unit_name()}.\n"
                        "Please generate new plots."
                    )
                    placeholder.setAlignment(Qt.AlignCenter)
                    placeholder.setFont(QFont("Arial", 14))
                    tab_layout.addWidget(placeholder)
    
    def get_temp_unit_name(self):
        """Get the name of the current temperature unit."""
        return "Celsius (°C)" if self.use_celsius else "Fahrenheit (°F)"
    
    def fahrenheit_to_celsius(self, f_value):
        """Convert Fahrenheit to Celsius."""
        return (f_value - 32) * 5/9
    
    def setup_viz_panel(self):
        # Create a tab widget for multiple plot workspaces
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setTabsClosable(True)  # Allow tabs to be closed
        self.plot_tabs.tabCloseRequested.connect(self.close_plot_tab)
        self.viz_layout.addWidget(self.plot_tabs)
        
        # Add a "+" tab for creating new tabs
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFixedSize(30, 24)
        self.add_tab_button.clicked.connect(self.add_plot_tab)
        self.plot_tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)
        
        # Dictionary to store plot references for each tab
        self.tab_plot_browsers = {}
        
        # Dictionary to store Plotly figure data for each tab
        self.tab_figures = {}
        
        # Dictionary to store the X-axis parameter for each tab
        self.tab_x_params = {}
        
        # Create the first tab
        self.add_plot_tab()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Log File", self.default_dir, "CSV Files (*.csv)"
        )
        
        if file_path:
            self.log_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.load_data(file_path)

    def load_data(self, file_path):
        try:
            # Read the header lines to understand the structure
            with open(file_path, 'r') as f:
                # Skip the first line (airframe info)
                next(f)
                # Read the second line (full parameter names with units)
                full_names = next(f).strip().split(',')
                # Read the third line (abbreviated parameter names)
                abbr_names = next(f).strip().split(',')
            
            # Identify columns with data in the third row (abbreviated names)
            valid_columns = []
            for i, abbr in enumerate(abbr_names):
                if abbr.strip():  # Only include columns with non-empty abbreviated names
                    valid_columns.append(i)
            
            # Create mappings between abbreviated names and full names
            # Only for columns with data in the third row
            self.abbr_to_full = {}
            self.full_to_abbr = {}
            
            for i in valid_columns:
                abbr = abbr_names[i]
                full = full_names[i] if i < len(full_names) else ""
                
                # Handle empty full names - use abbreviated name
                if not full.strip():
                    full = abbr
                
                # Store mappings
                self.abbr_to_full[abbr] = full
                self.full_to_abbr[full] = abbr
                
                # Debug print
                print(f"Column {i}: abbr='{abbr}', full='{full}'")
            
            # Read the CSV file, skipping the first 2 lines and using the 3rd line as header
            self.df = pd.read_csv(file_path, skiprows=2, header=0)
            
            # Filter the DataFrame to include only columns with data in the third row
            valid_df_columns = []
            for col in self.df.columns:
                # Check if this column has a non-empty name in the third row
                # or if it's a renamed column that we want to keep
                if col.strip() and not col.startswith('Unnamed:'):
                    valid_df_columns.append(col)
            
            # Keep only the valid columns
            self.df = self.df[valid_df_columns]
            
            # Get filtered column names
            all_columns = self.df.columns.tolist()
            
            # Get numeric columns for plotting
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Create display names (full names) for all columns
            display_columns = []
            for col in all_columns:
                # Get the full name from the mapping
                display_name = self.abbr_to_full.get(col, col)
                display_columns.append(display_name)
            
            # Update parameter list with full names
            self.param_list.clear()
            for i, col in enumerate(all_columns):
                display_name = display_columns[i]
                item = QListWidgetItem(display_name)
                # Store the actual column name as item data
                item.setData(Qt.UserRole, col)
                # Mark non-numeric columns with a different style
                if col not in self.numeric_columns:
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)
                self.param_list.addItem(item)
            
            # Update X-axis list with ALL columns (using full names)
            self.x_axis_list.clear()
            for i, col in enumerate(all_columns):
                display_name = display_columns[i]
                item = QListWidgetItem(display_name)
                # Store the actual column name as item data
                item.setData(Qt.UserRole, col)
                # Mark non-numeric columns with a different style
                if col not in self.numeric_columns:
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)
                self.x_axis_list.addItem(item)
            
            # Set default X-axis to "Lcl Time" if it exists
            lcl_time_index = -1
            for i, col in enumerate(all_columns):
                if col.lower() == "lcl time":
                    lcl_time_index = i
                    break
            
            if lcl_time_index >= 0:
                self.x_axis_list.setCurrentRow(lcl_time_index)
                
            # Enable the X-axis buttons
            self.clear_x_selection_btn.setEnabled(True)
            self.show_all_x_btn.setEnabled(True)
            
            # We no longer need to update the Y parameter list as it's been removed
            
            # Enable plot button and selection buttons
            self.plot_button.setEnabled(True)
            self.select_all_visible_btn.setEnabled(True)
            self.clear_selection_btn.setEnabled(True)
            self.show_all_btn.setEnabled(True)
            
            # Show a message
            self.plot_placeholder.setText(
                f"Data loaded from {os.path.basename(file_path)}\n"
                f"Select parameters and click 'Generate Plot'"
            )
            self.xy_plot_placeholder.setText("Select X and Y parameters for XY plot")
            
        except Exception as e:
            self.file_label.setText(f"Error loading file: {str(e)}")
            self.plot_placeholder.setText(f"Error loading file: {str(e)}")

    def select_category(self):
        """Filter the Y parameter list based on the selected category."""
        sender = self.sender()
        abbr_params = sender.property("category_params")
        category_name = sender.text()
        
        # Convert abbreviated parameter names to full names
        full_params = []
        for abbr in abbr_params:
            if abbr in self.abbr_to_full:
                full_params.append(self.abbr_to_full[abbr])
            else:
                full_params.append(abbr)  # Keep as is if not found
        
        # Debug print
        print(f"Category: {category_name}")
        print(f"Category params: {abbr_params}")
        print(f"Full params: {full_params}")
        
        # Check if we're already filtering for this category
        if hasattr(self, 'current_y_filter') and self.current_y_filter == category_name:
            # If clicking the same category again, show all parameters
            self.show_all_parameters()
            return
        
        # Store the current filter
        self.current_y_filter = category_name
        
        # Hide all parameters not in this category in the Y parameter list
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            if item.text() in full_params:
                item.setHidden(False)
            else:
                item.setHidden(True)
        
        # Update the category button text to indicate it's active
        for cat, btn in self.category_buttons.items():
            if cat == category_name:
                btn.setText(f"[{cat}]")
            else:
                btn.setText(cat)
    
    def select_x_category(self):
        """Filter the X-axis list based on the selected category."""
        sender = self.sender()
        abbr_params = sender.property("category_params")
        category_name = sender.text()
        
        # Convert abbreviated parameter names to full names
        full_params = []
        for abbr in abbr_params:
            if abbr in self.abbr_to_full:
                full_params.append(self.abbr_to_full[abbr])
            else:
                full_params.append(abbr)  # Keep as is if not found
        
        # Debug print
        print(f"X Category: {category_name}")
        print(f"X Category params: {abbr_params}")
        print(f"X Full params: {full_params}")
        
        # Check if we're already filtering for this category
        if hasattr(self, 'current_x_filter') and self.current_x_filter == category_name:
            # If clicking the same category again, show all parameters
            self.show_all_x_parameters()
            return
        
        # Store the current filter
        self.current_x_filter = category_name
        
        # Hide all parameters not in this category in the X-axis list
        for i in range(self.x_axis_list.count()):
            item = self.x_axis_list.item(i)
            if item.text() in full_params:
                item.setHidden(False)
            else:
                item.setHidden(True)
        
        # Update the category button text to indicate it's active
        for cat, btn in self.x_category_buttons.items():
            if cat == category_name:
                btn.setText(f"[{cat}]")
            else:
                btn.setText(cat)

    def extract_unit(self, param_name):
        """Extract unit from parameter name, e.g., 'Oil Temp (deg F)' -> 'deg F'"""
        if '(' in param_name and ')' in param_name:
            unit = param_name.split('(')[1].split(')')[0]
            return unit
        return "Unknown"
    
    def generate_plot(self):
        selected_items = self.param_list.selectedItems()
        # Get the actual column names from item data
        selected_params = [item.data(Qt.UserRole) for item in selected_items]
        selected_display_names = [item.text() for item in selected_items]
        
        if not selected_params:
            self.plot_placeholder.setText("Please select at least one parameter to plot")
            return
            
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
            
        # Use only numeric parameters for plotting
        selected_params = numeric_params
        selected_display_names = numeric_display_names
        
        # Get the selected X parameter from the X-axis list
        selected_x_items = self.x_axis_list.selectedItems()
        if not selected_x_items:
            self.plot_placeholder.setText("Please select an X-axis parameter")
            return
            
        # Get the actual column name for the selected X-axis parameter
        x_display = selected_x_items[0].text()
        x_param = selected_x_items[0].data(Qt.UserRole)
        
        # Get the current tab index
        current_tab_index = self.plot_tabs.currentIndex()
        
        # Check if there's an existing plot with a different X-axis parameter
        if (current_tab_index in self.tab_figures and 
            self.tab_figures[current_tab_index] is not None and 
            current_tab_index in self.tab_x_params and 
            self.tab_x_params[current_tab_index] != x_param):
            
            # Get the old X-axis parameter display name
            old_x_param_display = ""
            for i in range(self.x_axis_list.count()):
                item = self.x_axis_list.item(i)
                if item.data(Qt.UserRole) == self.tab_x_params[current_tab_index]:
                    old_x_param_display = item.text()
                    break
            
            # Show the X-axis change warning dialog
            dialog = XAxisChangeDialog(self, old_x_param_display, x_display)
            result = dialog.exec_()
            
            if result == QDialog.Rejected:
                # User chose to abort
                return
            
            # User chose to replace, so we'll clear the existing plot
            self.clear_tab_plot(current_tab_index)
        
        # Get the unit for the X parameter
        x_unit = self.extract_unit(x_display)
        
        # Check if we need to convert X temperature values
        x_values = self.df[x_param].copy()
        if self.use_celsius and "deg F" in x_unit:
            x_values = x_values.apply(self.fahrenheit_to_celsius)
            x_display = x_display.replace("deg F", "deg C")
        
        # Group parameters by units
        param_units = {}
        for i, display_name in enumerate(selected_display_names):
            unit = self.extract_unit(display_name)
            if unit not in param_units:
                param_units[unit] = []
            param_units[unit].append((selected_params[i], display_name))
        
        # Check if there's an existing figure in the current tab
        current_tab_index = self.plot_tabs.currentIndex()
        existing_fig = self.tab_figures.get(current_tab_index)
        
        unit_groups = list(param_units.keys())
        
        if existing_fig is not None and len(existing_fig.data) > 0:
            # Get existing unit groups from the figure
            existing_units = []
            for annotation in existing_fig.layout.annotations:
                if annotation.text.startswith("Unit: "):
                    unit = annotation.text[6:]  # Extract unit from "Unit: X"
                    existing_units.append(unit)
            
            # Create a new figure with both existing and new unit groups
            all_units = existing_units + unit_groups
            
            # Create a new figure with all subplots
            fig = make_subplots(
                rows=len(all_units), 
                cols=1, 
                shared_xaxes=True,  # Share x-axes between subplots
                vertical_spacing=0.02,
                subplot_titles=[f"Unit: {unit}" for unit in all_units]
            )
            
            # Copy existing traces to the new figure
            for i, trace in enumerate(existing_fig.data):
                # Find which unit group this trace belongs to
                unit_index = 0
                if hasattr(trace, 'yaxis'):
                    # Extract row number from yaxis (e.g., 'y2' -> 2)
                    if trace.yaxis == 'y':
                        unit_index = 0
                    else:
                        unit_index = int(trace.yaxis[1:]) - 1
                
                # Add the trace to the new figure in the same unit group
                fig.add_trace(
                    trace,
                    row=unit_index+1, 
                    col=1
                )
            
            # Now add the new traces
            for i, unit in enumerate(unit_groups):
                # Find the row index for this unit in the combined figure
                row_index = len(existing_units) + i + 1
                
                for param, display_name in param_units[unit]:
                    # Check if this is a temperature parameter and if we need to convert to Celsius
                    y_values = self.df[param].copy()
                    unit_label = unit
                    
                    # Convert temperature values if needed
                    if self.use_celsius and "deg F" in unit:
                        y_values = y_values.apply(self.fahrenheit_to_celsius)
                        unit_label = unit.replace("deg F", "deg C")
                        # Update subplot title
                        fig.layout.annotations[len(existing_units) + i].text = f"Unit: {unit_label}"
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_values, 
                            y=y_values, 
                            name=display_name
                        ),
                        row=row_index, 
                        col=1
                    )
        else:
            # Create a new figure with subplots
            fig = make_subplots(
                rows=len(unit_groups), 
                cols=1, 
                shared_xaxes=True,  # Share x-axes between subplots
                vertical_spacing=0.02,
                subplot_titles=[f"Unit: {unit}" for unit in unit_groups]
            )
            
            # Add traces to the appropriate subplot based on unit
            for i, unit in enumerate(unit_groups):
                for param, display_name in param_units[unit]:
                    # Check if this is a temperature parameter and if we need to convert to Celsius
                    y_values = self.df[param].copy()
                    unit_label = unit
                    
                    # Convert temperature values if needed
                    if self.use_celsius and "deg F" in unit:
                        y_values = y_values.apply(self.fahrenheit_to_celsius)
                        unit_label = unit.replace("deg F", "deg C")
                        # Update subplot title
                        fig.layout.annotations[i].text = f"Unit: {unit_label}"
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_values, 
                            y=y_values, 
                            name=display_name
                        ),
                        row=i+1, col=1
                    )
        
        # No need to add traces here as they are already added in the conditional blocks above
        
        # Update layout with responsive sizing, mouse wheel zoom, and hover features
        fig.update_layout(
            autosize=True,  # Enable autosize for responsive behavior
            title_text=f"Engine Data Log: {os.path.basename(self.log_file_path)}",
            showlegend=True,  # Show legend to distinguish multiple traces in the same subplot
            margin=dict(l=50, r=50, t=100, b=50),  # Add some margin for better appearance
            # Enable mouse wheel zoom
            modebar_add=['scrollZoom'],
            dragmode='zoom',  # Default drag mode is zoom
            # Enable hover mode with vertical line
            hovermode='x unified',  # Show a single vertical line at x position
            hoverdistance=100,  # Increase hover distance for better usability
            # Add cursor (spike) settings for all axes
            spikedistance=1000,  # Distance to show spikes regardless of data points
            hoverlabel=dict(
                bgcolor="#2D2D30",
                font_size=12,
                font_family="Arial",
                font_color="#E0E0E0"
            ),
            paper_bgcolor="#1E1E1E",  # Background color of the plot
            plot_bgcolor="#252526",    # Background color of the plotting area
            # Remove the bright frame around the plot area
            xaxis=dict(
                showline=False, 
                linewidth=0, 
                linecolor="#252526", 
                mirror=False,
                showgrid=True,
                gridcolor="#333333",
                zeroline=False
            ),
            yaxis=dict(
                showline=False, 
                linewidth=0, 
                linecolor="#252526", 
                mirror=False,
                showgrid=True,
                gridcolor="#333333",
                zeroline=False
            ),
        )
        
        # Add spikes (cursor lines) to all x-axes and y-axes
        for i in range(1, len(unit_groups) + 1):
            # Update x-axes with spikes
            fig.update_xaxes(
                showspikes=True,  # Show spike line for x-axis
                spikethickness=2,  # Line width
                spikedash='solid',  # Line dash style
                spikecolor='rgba(150, 150, 150, 0.8)',  # Line color
                spikesnap='cursor',  # Snap to cursor
                spikemode='across',  # Draw spike line across the plot
                showline=True,
                showgrid=True,
                row=i, col=1  # Specify the subplot
            )
            
            # Update y-axes with spikes
            fig.update_yaxes(
                showspikes=True,  # Show spike line for y-axis
                spikethickness=2,  # Line width
                spikedash='solid',  # Line dash style
                spikecolor='rgba(150, 150, 150, 0.8)',  # Line color
                spikesnap='cursor',  # Snap to cursor
                spikemode='across',  # Draw spike line across the plot
                showline=True,
                showgrid=True,
                row=i, col=1  # Specify the subplot
            )
        
        # Configure subplot linking for synchronized x-axis zooming only
        # This allows independent y-axis scales for each subplot
        if len(unit_groups) > 1:
            # Create a list of all subplot references
            subplot_refs = [f"xy{i+1}" for i in range(len(unit_groups))]
            
            # Link only the x-axes between subplots
            # The first subplot's x-axis will be the reference
            for i in range(1, len(subplot_refs)):
                # Link each subplot's x-axis to the first subplot's x-axis
                fig._layout_obj['xaxis' + subplot_refs[i][-1]]['matches'] = 'x' + subplot_refs[0][-1]
        
        # Set config to enable scrollZoom and hover features
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['scrollZoom'],
            'displaylogo': False,  # Hide Plotly logo
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'plot',
                'height': 800,
                'width': 1200,
                'scale': 1
            },
            'responsive': True,
            'frameMargins': 0,  # Remove frame margins
        }
        
        # Add custom CSS to the figure's layout
        fig.layout.template.layout.margin = dict(t=50, b=50, l=50, r=50, pad=0)
        fig.layout.template.layout.paper_bgcolor = "#1E1E1E"
        fig.layout.template.layout.plot_bgcolor = "#252526"
        fig.layout.margin = dict(t=50, b=50, l=50, r=50, pad=0)
        
        # Create a temporary HTML file and display it
        temp_file = os.path.join(os.getcwd(), "temp-plot.html")
        plot_path = plot(fig, output_type='file', filename=temp_file, auto_open=False, config=config)
        
        # Add custom CSS to remove the frame around the entire plot
        with open(plot_path, 'r') as file:
            html_content = file.read()
        
        # Insert custom CSS to remove the frame and set body background
        custom_css = """
        <style>
        body {
            background-color: #1E1E1E !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .plotly, .plot-container, .svg-container {
            border: none !important;
            box-shadow: none !important;
            background: #1E1E1E !important;
        }
        .js-plotly-plot, .plotly, .plotly div {
            background-color: #1E1E1E !important;
        }
        </style>
        """
        
        # Insert the custom CSS right before the </head> tag
        html_content = html_content.replace('</head>', f'{custom_css}</head>')
        
        # Write the modified HTML back to the file
        with open(plot_path, 'w') as file:
            file.write(html_content)
            
        print(f"Plot saved to: {plot_path}")
        
        # Get the current tab
        current_tab_index = self.plot_tabs.currentIndex()
        current_tab = self.plot_tabs.widget(current_tab_index)
        
        # Check if there's already a plot in this tab
        if current_tab_index in self.tab_plot_browsers and self.tab_plot_browsers[current_tab_index] is not None:
            # There's already a plot in this tab, so we'll update it
            # Get the existing browser
            browser = self.tab_plot_browsers[current_tab_index]
            
            # Load the new plot
            browser.load(QUrl.fromLocalFile(plot_path))
            
            # Store the figure data for future reference
            self.tab_figures[current_tab_index] = fig
        else:
            # This is the first plot in the tab, so we need to create a new browser
            # Clear the tab layout
            tab_layout = current_tab.layout()
            while tab_layout.count():
                item = tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Create a browser widget to display the plot
            browser = ZoomableWebEngineView()
            browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            browser.load(QUrl.fromLocalFile(plot_path))
            
            # Add the browser to the tab layout
            tab_layout.addWidget(browser)
            
            # Store references to the browser, figure, and X-axis parameter for the current tab
            self.tab_plot_browsers[current_tab_index] = browser
            self.tab_figures[current_tab_index] = fig
            self.tab_x_params[current_tab_index] = x_param
        
        # No need to enable the main clear button as it's been removed
        
        # Clear the parameter selection
        self.param_list.clearSelection()

    def generate_xy_plot(self):
        # Get the selected X parameter from the X-axis list
        selected_x_items = self.x_axis_list.selectedItems()
        if not selected_x_items:
            # Show a message in the current tab
            current_tab_index = self.plot_tabs.currentIndex()
            current_tab = self.plot_tabs.widget(current_tab_index)
            current_tab_layout = current_tab.layout()
            
            # Clear the tab layout
            while current_tab_layout.count():
                item = current_tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Add a placeholder
            placeholder = QLabel("Please select an X parameter")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Arial", 14))
            current_tab_layout.addWidget(placeholder)
            return
            
        # Get the actual column name for the selected X-axis parameter
        x_display = selected_x_items[0].text()
        x_param = selected_x_items[0].data(Qt.UserRole)
        
        # Get the selected Y parameters from the parameter list
        selected_items = self.param_list.selectedItems()
        selected_params = [item.data(Qt.UserRole) for item in selected_items]
        selected_display_names = [item.text() for item in selected_items]
        
        if not x_param:
            # Show a message in the current tab
            current_tab_index = self.plot_tabs.currentIndex()
            current_tab = self.plot_tabs.widget(current_tab_index)
            current_tab_layout = current_tab.layout()
            
            # Clear the tab layout
            while current_tab_layout.count():
                item = current_tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Add a placeholder
            placeholder = QLabel("Please select an X parameter")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Arial", 14))
            current_tab_layout.addWidget(placeholder)
            return
        
        if not selected_params:
            # Show a message in the current tab
            current_tab_index = self.plot_tabs.currentIndex()
            current_tab = self.plot_tabs.widget(current_tab_index)
            current_tab_layout = current_tab.layout()
            
            # Clear the tab layout
            while current_tab_layout.count():
                item = current_tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Add a placeholder
            placeholder = QLabel("Please select at least one Y parameter")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Arial", 14))
            current_tab_layout.addWidget(placeholder)
            return
        
        # Filter out non-numeric parameters
        numeric_params = []
        numeric_display_names = []
        for i, param in enumerate(selected_params):
            if param in self.numeric_columns:
                numeric_params.append(param)
                numeric_display_names.append(selected_display_names[i])
        
        if not numeric_params:
            # Show a message in the current tab
            current_tab_index = self.plot_tabs.currentIndex()
            current_tab = self.plot_tabs.widget(current_tab_index)
            current_tab_layout = current_tab.layout()
            
            # Clear the tab layout
            while current_tab_layout.count():
                item = current_tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Add a placeholder
            placeholder = QLabel("Please select at least one numeric Y parameter")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Arial", 14))
            current_tab_layout.addWidget(placeholder)
            return
        
        # Use only numeric parameters for plotting
        selected_y_params = numeric_params
        selected_y_display_names = numeric_display_names
        
        # Get the unit for the X parameter
        x_unit = self.extract_unit(x_display)
        
        # Check if we need to convert X temperature values
        x_values = self.df[x_param].copy()
        if self.use_celsius and "deg F" in x_unit:
            x_values = x_values.apply(self.fahrenheit_to_celsius)
            x_display = x_display.replace("deg F", "deg C")
        
        # Group Y parameters by units
        param_units = {}
        for i, display_name in enumerate(selected_y_display_names):
            unit = self.extract_unit(display_name)
            if unit not in param_units:
                param_units[unit] = []
            param_units[unit].append((selected_y_params[i], display_name))
        
        # Create a subplot for each unit group
        unit_groups = list(param_units.keys())
        
        if len(unit_groups) == 1:
            # If there's only one unit group, create a single plot
            fig = go.Figure()
            
            # Add traces for each Y parameter
            for param, display_name in param_units[unit_groups[0]]:
                # Check if this is a temperature parameter and if we need to convert to Celsius
                y_values = self.df[param].copy()
                y_display = display_name
                
                # Convert Y temperature values if needed
                if self.use_celsius and "deg F" in unit_groups[0]:
                    y_values = y_values.apply(self.fahrenheit_to_celsius)
                    y_display = y_display.replace("deg F", "deg C")
                
                fig.add_trace(
                    go.Scatter(
                        x=x_values, 
                        y=y_values, 
                        mode='markers', 
                        name=y_display
                    )
                )
            
            # Set the title and axis labels
            fig.update_layout(
                title_text=f"XY Plot: Multiple Parameters vs {x_display}",
                xaxis_title=x_display,
                yaxis_title=unit_groups[0] if unit_groups[0] != "Unknown" else ""
            )
        else:
            # If there are multiple unit groups, create subplots
            fig = make_subplots(
                rows=len(unit_groups), 
                cols=1, 
                shared_xaxes=True,  # Share x-axes between subplots
                vertical_spacing=0.02,
                subplot_titles=[f"Unit: {unit}" for unit in unit_groups]
            )
            
            # Add traces to the appropriate subplot based on unit
            for i, unit in enumerate(unit_groups):
                for param, display_name in param_units[unit]:
                    # Check if this is a temperature parameter and if we need to convert to Celsius
                    y_values = self.df[param].copy()
                    unit_label = unit
                    
                    # Convert temperature values if needed
                    if self.use_celsius and "deg F" in unit:
                        y_values = y_values.apply(self.fahrenheit_to_celsius)
                        unit_label = unit.replace("deg F", "deg C")
                        # Update subplot title
                        fig.layout.annotations[i].text = f"Unit: {unit_label}"
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_values, 
                            y=y_values, 
                            mode='markers', 
                            name=display_name
                        ),
                        row=i+1, col=1
                    )
            
            # Configure subplot linking for synchronized x-axis zooming only
            # This allows independent y-axis scales for each subplot
            if len(unit_groups) > 1:
                # Create a list of all subplot references
                subplot_refs = [f"xy{i+1}" for i in range(len(unit_groups))]
                
                # Link only the x-axes between subplots
                # The first subplot's x-axis will be the reference
                for i in range(1, len(subplot_refs)):
                    # Link each subplot's x-axis to the first subplot's x-axis
                    fig._layout_obj['xaxis' + subplot_refs[i][-1]]['matches'] = 'x' + subplot_refs[0][-1]
            
            # Set the title
            fig.update_layout(
                title_text=f"XY Plot: Multiple Parameters vs {x_display}"
            )
        
        # Update layout with responsive sizing, mouse wheel zoom, and hover features
        fig.update_layout(
            autosize=True,  # Enable autosize for responsive behavior
            # Title is already set above based on the number of unit groups
            xaxis_title=x_display,
            margin=dict(l=50, r=50, t=100, b=50),  # Add some margin for better appearance
            # Enable mouse wheel zoom
            modebar_add=['scrollZoom'],
            dragmode='zoom',  # Default drag mode is zoom
            # Enable hover mode with closest point
            hovermode='closest',  # Show hover info for closest point
            hoverdistance=100,  # Increase hover distance for better usability,
            hoverlabel=dict(
                bgcolor="#2D2D30",
                font_size=12,
                font_family="Arial",
                font_color="#E0E0E0"
            ),
            paper_bgcolor="#1E1E1E",  # Background color of the plot
            plot_bgcolor="#252526",    # Background color of the plotting area
            # Remove the bright frame around the plot area
            xaxis=dict(
                showline=False, 
                linewidth=0, 
                linecolor="#252526", 
                mirror=False,
                showgrid=True,
                gridcolor="#333333",
                zeroline=False
            ),
            yaxis=dict(
                showline=False, 
                linewidth=0, 
                linecolor="#252526", 
                mirror=False,
                showgrid=True,
                gridcolor="#333333",
                zeroline=False
            ),
        )
        
        # Set config to enable scrollZoom and hover features
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['scrollZoom'],
            'displaylogo': False,  # Hide Plotly logo
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'plot',
                'height': 800,
                'width': 1200,
                'scale': 1
            },
            'responsive': True,
            'frameMargins': 0,  # Remove frame margins
        }
        
        # Add custom CSS to the figure's layout
        fig.layout.template.layout.margin = dict(t=50, b=50, l=50, r=50, pad=0)
        fig.layout.template.layout.paper_bgcolor = "#1E1E1E"
        fig.layout.template.layout.plot_bgcolor = "#252526"
        fig.layout.margin = dict(t=50, b=50, l=50, r=50, pad=0)
        
        # Create a temporary HTML file and display it
        temp_file = os.path.join(os.getcwd(), "temp-plot.html")
        plot_path = plot(fig, output_type='file', filename=temp_file, auto_open=False, config=config)
        
        # Add custom CSS to remove the frame around the entire plot
        with open(plot_path, 'r') as file:
            html_content = file.read()
        
        # Insert custom CSS to remove the frame and set body background
        custom_css = """
        <style>
        body {
            background-color: #1E1E1E !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .plotly, .plot-container, .svg-container {
            border: none !important;
            box-shadow: none !important;
            background: #1E1E1E !important;
        }
        .js-plotly-plot, .plotly, .plotly div {
            background-color: #1E1E1E !important;
        }
        </style>
        """
        
        # Insert the custom CSS right before the </head> tag
        html_content = html_content.replace('</head>', f'{custom_css}</head>')
        
        # Write the modified HTML back to the file
        with open(plot_path, 'w') as file:
            file.write(html_content)
            
        print(f"Plot saved to: {plot_path}")
        
        # Get the current tab
        current_tab_index = self.plot_tabs.currentIndex()
        current_tab = self.plot_tabs.widget(current_tab_index)
        
        # Check if there's already a plot in this tab
        if current_tab_index in self.tab_plot_browsers and self.tab_plot_browsers[current_tab_index] is not None:
            # There's already a plot in this tab, so we'll update it
            # Get the existing browser
            browser = self.tab_plot_browsers[current_tab_index]
            
            # Load the new plot
            browser.load(QUrl.fromLocalFile(plot_path))
            
            # Store the figure data for future reference
            self.tab_figures[current_tab_index] = fig
        else:
            # This is the first plot in the tab, so we need to create a new browser
            # Clear the tab layout
            tab_layout = current_tab.layout()
            while tab_layout.count():
                item = tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Create a browser widget to display the plot
            browser = ZoomableWebEngineView()
            browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            browser.load(QUrl.fromLocalFile(plot_path))
            
            # Add the browser to the tab layout
            tab_layout.addWidget(browser)
            
            # Store references to the browser and figure for the current tab
            self.tab_plot_browsers[current_tab_index] = browser
            self.tab_figures[current_tab_index] = fig
        
        # No need to enable the main clear button as it's been removed
        
        # No need to clear parameter selection for XY plot as it uses combo boxes

    def clear_tab_plot(self, tab_index):
        """Clear the plot from a specific tab."""
        # Get the tab
        tab = self.plot_tabs.widget(tab_index)
        if tab:
            # Clear the tab layout
            tab_layout = tab.layout()
            while tab_layout.count():
                item = tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            # Reset the browser reference
            self.tab_plot_browsers[tab_index] = None
            self.tab_figures[tab_index] = None
            
            # Add a placeholder
            placeholder = QLabel("Select parameters and click 'Generate Plot' to create visualizations")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Arial", 14))
            tab_layout.addWidget(placeholder)
    
    def clear_time_series_plot(self):
        """Clear all time series plots and restore the placeholder."""
        # Remove all browser widgets and containers
        for browser, container in self.ts_browsers:
            container.setParent(None)
        
        # Clear the list
        self.ts_browsers = []
        
        # Show the placeholder again
        self.plot_placeholder.setVisible(True)
    
    def clear_xy_plot(self):
        """Clear all XY plots and restore the placeholder."""
        # Remove all browser widgets and containers
        for browser, container in self.xy_browsers:
            container.setParent(None)
        
        # Clear the list
        self.xy_browsers = []
        
        # Show the placeholder again
        self.xy_plot_placeholder.setVisible(True)
    
    def select_all_visible_parameters(self):
        """Select all parameters that are currently visible in the list."""
        # First, clear current selection
        self.param_list.clearSelection()
        
        # Then select all visible items
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            if not item.isHidden():
                item.setSelected(True)
    
    def show_all_parameters(self):
        """Show all parameters in the Y parameter list."""
        # Show all parameters in the Y parameter list
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            item.setHidden(False)
        
        # Reset all Y category button texts
        for cat, btn in self.category_buttons.items():
            btn.setText(cat)
        
        # Clear the current Y filter
        self.current_y_filter = None
    
    def show_all_x_parameters(self):
        """Show all parameters in the X-axis list."""
        # Show all parameters in the X-axis list
        for i in range(self.x_axis_list.count()):
            item = self.x_axis_list.item(i)
            item.setHidden(False)
        
        # Reset all X category button texts
        for cat, btn in self.x_category_buttons.items():
            btn.setText(cat)
        
        # Clear the current X filter
        self.current_x_filter = None
    
    def clear_parameter_selection(self):
        """Clear all selected parameters in the list."""
        self.param_list.clearSelection()
    
    def clear_x_parameter_selection(self):
        """Clear the X-axis parameter selection."""
        self.x_axis_list.clearSelection()
    
    def select_all_visible_y_parameters(self):
        """Select all Y parameters that are currently visible in the list."""
        # First, clear current selection
        self.y_param_list.clearSelection()
        
        # Then select all visible items
        for i in range(self.y_param_list.count()):
            item = self.y_param_list.item(i)
            if not item.isHidden():
                item.setSelected(True)
    
    def clear_y_parameter_selection(self):
        """Clear all selected Y parameters in the list."""
        self.y_param_list.clearSelection()
    
    def add_plot_tab(self):
        """Add a new plot tab to the workspace."""
        # Create a new tab with a simple layout
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for maximum space
        
        # Add a placeholder for the tab
        placeholder = QLabel("Select parameters and click 'Generate Plot' to create visualizations")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setFont(QFont("Arial", 14))
        tab_layout.addWidget(placeholder)
        
        # Add the tab to the tab widget
        tab_index = self.plot_tabs.addTab(tab, f"Plot {self.plot_tabs.count() + 1}")
        
        # Select the new tab
        self.plot_tabs.setCurrentIndex(tab_index)
        
        # Initialize the plot browser for this tab (will hold a single browser)
        self.tab_plot_browsers[tab_index] = None
        
        # Initialize the figure data for this tab
        self.tab_figures[tab_index] = None
        
        return tab_index
    
    def close_plot_tab(self, index):
        """Close a plot tab."""
        # Don't close if it's the last tab
        if self.plot_tabs.count() <= 1:
            return
        
        # Remove the tab's plot browsers from our tracking
        if index in self.tab_plot_browsers:
            del self.tab_plot_browsers[index]
        
        # Remove the tab
        self.plot_tabs.removeTab(index)
        
        # Renumber the remaining tabs
        for i in range(self.plot_tabs.count()):
            self.plot_tabs.setTabText(i, f"Plot {i + 1}")
            
            # Update the keys in the tab_plot_browsers dictionary
            if i + 1 in self.tab_plot_browsers and i != i + 1:
                self.tab_plot_browsers[i] = self.tab_plot_browsers.pop(i + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EngineDataVisualizer()
    window.showMaximized()  # Start in maximized (full screen) mode
    sys.exit(app.exec_())
