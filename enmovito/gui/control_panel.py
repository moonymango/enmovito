"""
Control panel for the Enmovito application.

This module contains the ControlPanel class, which is responsible for
providing the user interface for parameter selection and control.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QPushButton, QGroupBox, QGridLayout, QRadioButton, QButtonGroup,
    QListWidgetItem
)


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


class ControlPanel(QWidget):
    """
    Panel for parameter selection and control.
    
    This class is responsible for providing the user interface for
    parameter selection, filtering, and control.
    """
    
    # Define signals for communication with the main class
    plot_requested = pyqtSignal(list, list, str, str)  # selected_params, selected_display_names, x_param, x_display
    temperature_unit_changed = pyqtSignal(bool)  # use_celsius
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self, parent=None, data_handler=None):
        """
        Initialize the control panel.
        
        Args:
            parent: The parent widget (Enmovito instance)
            data_handler: The data handler instance
        """
        super().__init__(parent)
        self.parent = parent  # Reference to the main Enmovito instance
        self.data_handler = data_handler
        
        # Initialize attributes
        self.param_list = None
        self.x_axis_list = None
        self.category_buttons = {}
        self.x_category_buttons = {}
        self.current_y_filter = None
        self.current_x_filter = None
        self.plot_button = None
        self.file_button = None
        self.file_label = None
        self.show_all_btn = None
        self.select_all_visible_btn = None
        self.clear_selection_btn = None
        self.show_all_x_btn = None
        self.clear_x_selection_btn = None
        self.fahrenheit_radio = None
        self.celsius_radio = None
        self.dark_theme_radio = None
        self.light_theme_radio = None
        self.temp_unit_button_group = None
        self.theme_button_group = None
        
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
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Set up the control panel with parameter selection and controls."""
        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()

        # File selection button
        self.file_button = QPushButton("Select Log File")
        self.file_button.clicked.connect(self.on_file_button_clicked)
        file_layout.addWidget(self.file_button)

        # Display selected file
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)

        file_group.setLayout(file_layout)
        self.layout.addWidget(file_group)

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
        self.layout.addWidget(x_axis_group)

        # Parameter selection section
        param_group = QGroupBox("Parameter Selection")
        param_layout = QVBoxLayout()

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
        self.plot_button.clicked.connect(self.on_plot_button_clicked)
        self.plot_button.setEnabled(False)
        param_layout.addWidget(self.plot_button)

        param_group.setLayout(param_layout)
        self.layout.addWidget(param_group)

        # Add stretch to push everything to the top and leave space at the bottom
        self.layout.addStretch()

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
        self.layout.addWidget(temp_unit_group)

        # Create a group box for theme selection
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QHBoxLayout()

        # Create radio buttons for theme selection
        self.theme_button_group = QButtonGroup(self)

        # Dark theme radio button
        self.dark_theme_radio = QRadioButton("Dark")
        self.dark_theme_radio.setChecked(True)  # Default to dark theme
        self.dark_theme_radio.clicked.connect(lambda: self.theme_changed.emit("dark"))
        self.theme_button_group.addButton(self.dark_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)

        # Light theme radio button
        self.light_theme_radio = QRadioButton("Light")
        self.light_theme_radio.clicked.connect(lambda: self.theme_changed.emit("light"))
        self.theme_button_group.addButton(self.light_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)

        theme_group.setLayout(theme_layout)
        self.layout.addWidget(theme_group)
        
    def set_fahrenheit(self):
        """Set temperature unit to Fahrenheit."""
        self.temperature_unit_changed.emit(False)
        
    def set_celsius(self):
        """Set temperature unit to Celsius."""
        self.temperature_unit_changed.emit(True)
        
    def on_file_button_clicked(self):
        """Handle file button click event."""
        # This will be connected to a method in the main class
        pass
        
    def on_plot_button_clicked(self):
        """Handle plot button click event."""
        selected_items = self.param_list.selectedItems()
        # Get the actual column names from item data
        selected_params = [item.data(Qt.UserRole) for item in selected_items]
        selected_display_names = [item.text() for item in selected_items]
        
        # Get the selected X parameter from the X-axis list
        selected_x_items = self.x_axis_list.selectedItems()
        if not selected_x_items:
            # No X-axis parameter selected
            return
            
        # Get the actual column name for the selected X-axis parameter
        x_display = selected_x_items[0].text()
        x_param = selected_x_items[0].data(Qt.UserRole)
        
        # Emit the plot_requested signal
        self.plot_requested.emit(selected_params, selected_display_names, x_param, x_display)
        
        # Clear the parameter selection
        self.param_list.clearSelection()
        
    def select_category(self):
        """Filter the Y parameter list based on the selected category."""
        sender = self.sender()
        abbr_params = sender.property("category_params")
        category_name = sender.text()
        
        # Check if we're already filtering for this category
        if hasattr(self, 'current_y_filter') and self.current_y_filter == category_name:
            # If clicking the same category again, show all parameters
            self.show_all_parameters()
            return
            
        # Store the current filter
        self.current_y_filter = category_name
        
        # Convert abbreviated parameter names to full names
        full_params = []
        for abbr in abbr_params:
            if self.data_handler and abbr in self.data_handler.abbr_to_full:
                full_params.append(self.data_handler.abbr_to_full[abbr])
            else:
                full_params.append(abbr)  # Keep as is if not found
                
        # Debug print
        print(f"Category: {category_name}")
        print(f"Category params: {abbr_params}")
        print(f"Full params: {full_params}")
        
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
        
        # Check if we're already filtering for this category
        if hasattr(self, 'current_x_filter') and self.current_x_filter == category_name:
            # If clicking the same category again, show all parameters
            self.show_all_x_parameters()
            return
            
        # Store the current filter
        self.current_x_filter = category_name
        
        # Convert abbreviated parameter names to full names
        full_params = []
        for abbr in abbr_params:
            if self.data_handler and abbr in self.data_handler.abbr_to_full:
                full_params.append(self.data_handler.abbr_to_full[abbr])
            else:
                full_params.append(abbr)  # Keep as is if not found
                
        # Debug print
        print(f"X Category: {category_name}")
        print(f"X Category params: {abbr_params}")
        print(f"X Full params: {full_params}")
        
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
        
    def update_file_label(self, file_name):
        """Update the file label with the selected file name."""
        self.file_label.setText(file_name)
        
    def enable_controls(self, enable=True):
        """Enable or disable controls based on whether a file is loaded."""
        self.plot_button.setEnabled(enable)
        self.select_all_visible_btn.setEnabled(enable)
        self.clear_selection_btn.setEnabled(enable)
        self.show_all_btn.setEnabled(enable)
        self.clear_x_selection_btn.setEnabled(enable)
        self.show_all_x_btn.setEnabled(enable)
        
    def update_parameter_list(self, all_columns, display_columns, numeric_columns, abbr_to_full):
        """Update the parameter list with the loaded data."""
        # Store the mappings
        self.data_handler.abbr_to_full = abbr_to_full
        
        # Update parameter list with full names
        self.param_list.clear()
        for i, col in enumerate(all_columns):
            display_name = display_columns[i]
            item = QListWidgetItem(display_name)
            # Store the actual column name as item data
            item.setData(Qt.UserRole, col)
            # Mark non-numeric columns with a different style
            if col not in numeric_columns:
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
            if col not in numeric_columns:
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
            
        # Enable controls
        self.enable_controls(True)
