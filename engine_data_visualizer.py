import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PyQt5.QtCore import Qt, QUrl, QEvent
from PyQt5.QtGui import QFont, QWheelEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QListWidget, QLabel, QFileDialog, QTabWidget, QSplitter,
    QListWidgetItem, QGroupBox, QGridLayout, QSizePolicy
)
# Import QtWebEngineWidgets early
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
import plotly.io as pio
from plotly.offline import plot
# Set Qt attribute before creating QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Set plotly renderer for PyQt
pio.renderers.default = "browser"


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
        
        # Data storage
        self.df = None
        self.log_file_path = None
        self.numeric_columns = []
        self.time_column = "Lcl Time"  # Default time column
        
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

    def setup_control_panel(self):
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
        
        # Parameter selection section
        param_group = QGroupBox("Parameter Selection")
        param_layout = QVBoxLayout()
        
        # Time column selection
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time Column:"))
        self.time_combo = QComboBox()
        time_layout.addWidget(self.time_combo)
        param_layout.addLayout(time_layout)
        
        # Parameter list with selection controls
        param_list_header = QHBoxLayout()
        param_list_header.addWidget(QLabel("Select Parameters to Plot:"))
        
        # Add "Select All Visible" button
        self.select_all_visible_btn = QPushButton("Select All Visible")
        self.select_all_visible_btn.clicked.connect(self.select_all_visible_parameters)
        self.select_all_visible_btn.setEnabled(False)  # Initially disabled until file is loaded
        param_list_header.addWidget(self.select_all_visible_btn)
        
        param_layout.addLayout(param_list_header)
        
        self.param_list = QListWidget()
        self.param_list.setSelectionMode(QListWidget.MultiSelection)
        param_layout.addWidget(self.param_list)
        
        # Quick parameter category selection
        category_layout = QGridLayout()
        
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
        
        # Add stretch to push everything to the top
        self.control_layout.addStretch()

    def setup_viz_panel(self):
        # Create tabs for different visualization types
        self.viz_tabs = QTabWidget()
        self.viz_layout.addWidget(self.viz_tabs)
        
        # Time Series tab
        self.time_series_tab = QWidget()
        self.time_series_layout = QVBoxLayout(self.time_series_tab)
        self.viz_tabs.addTab(self.time_series_tab, "Time Series")
        
        # Add a spacer at the top for consistent layout
        self.time_series_layout.addSpacing(10)
        
        # Placeholder for the plot
        self.plot_placeholder = QLabel(
            "Select a log file and parameters to visualize"
        )
        self.plot_placeholder.setAlignment(Qt.AlignCenter)
        self.plot_placeholder.setFont(QFont("Arial", 14))
        self.time_series_layout.addWidget(self.plot_placeholder)
        
        # Store references to browser widgets and their containers
        self.ts_browsers = []
        
        # XY Plot tab
        self.xy_plot_tab = QWidget()
        self.xy_plot_layout = QVBoxLayout(self.xy_plot_tab)
        self.viz_tabs.addTab(self.xy_plot_tab, "XY Plot")
        
        # Add a spacer at the top for consistent layout
        self.xy_plot_layout.addSpacing(10)
        
        # Store references to browser widgets and their containers
        self.xy_browsers = []
        
        # XY Plot controls
        xy_controls = QWidget()
        xy_controls_layout = QHBoxLayout(xy_controls)
        
        xy_controls_layout.addWidget(QLabel("X Axis:"))
        self.x_axis_combo = QComboBox()
        xy_controls_layout.addWidget(self.x_axis_combo)
        
        xy_controls_layout.addWidget(QLabel("Y Axis:"))
        self.y_axis_combo = QComboBox()
        xy_controls_layout.addWidget(self.y_axis_combo)
        
        self.xy_plot_button = QPushButton("Generate XY Plot")
        self.xy_plot_button.clicked.connect(self.generate_xy_plot)
        self.xy_plot_button.setEnabled(False)
        xy_controls_layout.addWidget(self.xy_plot_button)
        
        self.xy_plot_layout.addWidget(xy_controls)
        
        # Placeholder for the XY plot
        self.xy_plot_placeholder = QLabel(
            "Select X and Y parameters for XY plot"
        )
        self.xy_plot_placeholder.setAlignment(Qt.AlignCenter)
        self.xy_plot_placeholder.setFont(QFont("Arial", 14))
        self.xy_plot_layout.addWidget(self.xy_plot_placeholder)

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
            
            # Update time column combo box with full names
            self.time_combo.clear()
            time_columns = [
                col for col in all_columns 
                if 'time' in col.lower() or 'date' in col.lower()
            ]
            time_column_full_names = [self.abbr_to_full.get(col, col) for col in time_columns]
            self.time_combo.addItems(time_column_full_names)
            
            # Find the index of "Lcl Time" if it exists
            lcl_time_index = (
                [col.lower() for col in time_columns].index("lcl time") 
                if "lcl time" in [col.lower() for col in time_columns] else 0
            )
            self.time_combo.setCurrentIndex(lcl_time_index)
            
            # Get numeric columns for plotting
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Create display names (full names) for all columns
            display_columns = []
            for col in all_columns:
                # Get the full name from the mapping
                display_name = self.abbr_to_full.get(col, col)
                display_columns.append(display_name)
            
            # Create display names for numeric columns
            numeric_display_columns = []
            for col in self.numeric_columns:
                display_name = self.abbr_to_full.get(col, col)
                numeric_display_columns.append(display_name)
            
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
            
            # Update XY plot combo boxes with numeric columns only (using full names)
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.x_axis_combo.addItems(numeric_display_columns)
            self.y_axis_combo.addItems(numeric_display_columns)
            
            # Enable plot buttons and select all button
            self.plot_button.setEnabled(True)
            self.xy_plot_button.setEnabled(True)
            self.select_all_visible_btn.setEnabled(True)
            
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
        if hasattr(self, 'current_filter') and self.current_filter == category_name:
            # If clicking the same category again, show all parameters
            self.show_all_parameters()
            return
        
        # Store the current filter
        self.current_filter = category_name
        
        # Hide all parameters not in this category
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
        
        # Get the actual column name for the selected time column
        time_display = self.time_combo.currentText()
        time_column = self.full_to_abbr.get(time_display, time_display)
        
        # Group parameters by units
        param_units = {}
        for i, display_name in enumerate(selected_display_names):
            unit = self.extract_unit(display_name)
            if unit not in param_units:
                param_units[unit] = []
            param_units[unit].append((selected_params[i], display_name))
        
        # Create a subplot for each unit group
        unit_groups = list(param_units.keys())
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
                fig.add_trace(
                    go.Scatter(
                        x=self.df[time_column], 
                        y=self.df[param], 
                        name=display_name
                    ),
                    row=i+1, col=1
                )
        
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
                bgcolor="white",
                font_size=12,
                font_family="Arial"
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
        }
        
        # Create a temporary HTML file and display it
        temp_file = os.path.join(os.getcwd(), "temp-plot.html")
        plot_path = plot(fig, output_type='file', filename=temp_file, auto_open=False, config=config)
        print(f"Plot saved to: {plot_path}")
        
        # If this is the first plot, hide the placeholder
        if not self.ts_browsers:
            self.plot_placeholder.setVisible(False)
        
        # Create a container for the plot and its clear button
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        
        # Add a clear button for this specific plot
        button_layout = QHBoxLayout()
        clear_button = QPushButton(f"Clear: {', '.join(selected_display_names)}")
        clear_button.clicked.connect(lambda: self.clear_specific_ts_plot(plot_container))
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        plot_layout.addLayout(button_layout)
        
        # Create a browser widget to display the plot with size policy for expansion
        browser = ZoomableWebEngineView()
        browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        browser.load(QUrl.fromLocalFile(plot_path))
        plot_layout.addWidget(browser, 1)  # Add with stretch factor of 1
        
        # Add the container to the layout
        self.time_series_layout.addWidget(plot_container)
        
        # Store references to the browser and container
        self.ts_browsers.append((browser, plot_container))
        
        # No need to enable the main clear button as it's been removed
        
        # Clear the parameter selection
        self.param_list.clearSelection()

    def generate_xy_plot(self):
        x_display = self.x_axis_combo.currentText()
        y_display = self.y_axis_combo.currentText()
        
        # Convert display names to actual column names
        x_param = self.full_to_abbr.get(x_display, x_display)
        y_param = self.full_to_abbr.get(y_display, y_display)
        
        if not x_param or not y_param:
            self.xy_plot_placeholder.setText("Please select X and Y parameters")
            return
        
        # Create the XY plot
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=self.df[x_param], 
                y=self.df[y_param], 
                mode='markers', 
                name=f'{y_param} vs {x_param}'
            )
        )
        
        # Update layout with responsive sizing, mouse wheel zoom, and hover features
        fig.update_layout(
            autosize=True,  # Enable autosize for responsive behavior
            title_text=f"{y_display} vs {x_display}",
            xaxis_title=x_display,
            yaxis_title=y_display,
            margin=dict(l=50, r=50, t=100, b=50),  # Add some margin for better appearance
            # Enable mouse wheel zoom
            modebar_add=['scrollZoom'],
            dragmode='zoom',  # Default drag mode is zoom
            # Enable hover mode with closest point
            hovermode='closest',  # Show hover info for closest point
            hoverdistance=100,  # Increase hover distance for better usability
        )
        
        # Set config to enable scrollZoom and hover features
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['scrollZoom'],
            'displaylogo': False,  # Hide Plotly logo
        }
        
        # Create a temporary HTML file and display it
        temp_file = os.path.join(os.getcwd(), "temp-plot.html")
        plot_path = plot(fig, output_type='file', filename=temp_file, auto_open=False, config=config)
        print(f"Plot saved to: {plot_path}")
        
        # If this is the first plot, hide the placeholder
        if not self.xy_browsers:
            self.xy_plot_placeholder.setVisible(False)
        
        # Create a container for the plot and its clear button
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        
        # Add a clear button for this specific plot
        button_layout = QHBoxLayout()
        clear_button = QPushButton(f"Clear: {y_display} vs {x_display}")
        clear_button.clicked.connect(lambda: self.clear_specific_xy_plot(plot_container))
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        plot_layout.addLayout(button_layout)
        
        # Create a browser widget to display the plot with size policy for expansion
        browser = ZoomableWebEngineView()
        browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        browser.load(QUrl.fromLocalFile(plot_path))
        plot_layout.addWidget(browser)
        
        # Add the container to the layout
        self.xy_plot_layout.addWidget(plot_container)
        
        # Store references to the browser and container
        self.xy_browsers.append((browser, plot_container))
        
        # No need to enable the main clear button as it's been removed
        
        # No need to clear parameter selection for XY plot as it uses combo boxes

    def clear_specific_ts_plot(self, container):
        """Clear a specific time series plot."""
        # Find and remove the browser and container from our list
        for i, (browser, cont) in enumerate(self.ts_browsers):
            if cont == container:
                self.ts_browsers.pop(i)
                break
        
        # Remove the container from the layout
        container.setParent(None)
        
        # If no more plots, show the placeholder
        if not self.ts_browsers:
            self.plot_placeholder.setVisible(True)
    
    def clear_specific_xy_plot(self, container):
        """Clear a specific XY plot."""
        # Find and remove the browser and container from our list
        for i, (browser, cont) in enumerate(self.xy_browsers):
            if cont == container:
                self.xy_browsers.pop(i)
                break
        
        # Remove the container from the layout
        container.setParent(None)
        
        # If no more plots, show the placeholder
        if not self.xy_browsers:
            self.xy_plot_placeholder.setVisible(True)
    
    def clear_time_series_plot(self):
        """Clear all time series plots and restore the placeholder."""
        # Remove all browser widgets and containers
        for browser, container in self.ts_browsers:
            container.setParent(None)
        
        # Clear the list
        self.ts_browsers = []
        
        # Show the placeholder again
        self.plot_placeholder.setVisible(True)
        
        # Disable the clear button
        self.clear_ts_button.setEnabled(False)
    
    def clear_xy_plot(self):
        """Clear all XY plots and restore the placeholder."""
        # Remove all browser widgets and containers
        for browser, container in self.xy_browsers:
            container.setParent(None)
        
        # Clear the list
        self.xy_browsers = []
        
        # Show the placeholder again
        self.xy_plot_placeholder.setVisible(True)
        
        # Disable the clear button
        self.clear_xy_button.setEnabled(False)
    
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
        """Show all parameters in the list."""
        # Show all parameters
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            item.setHidden(False)
        
        # Reset all category button texts
        for cat, btn in self.category_buttons.items():
            btn.setText(cat)
        
        # Clear the current filter
        self.current_filter = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EngineDataVisualizer()
    window.show()
    sys.exit(app.exec_())
