"""
Visualization panel for the Enmovito application.

This module contains the VisualizationPanel class, which is responsible for
displaying and managing the visualization of engine data.
"""

import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QPushButton, QSizePolicy, QDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


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


class VisualizationPanel(QWidget):
    """
    Panel for visualizing engine data.
    
    This class is responsible for creating and managing the visualization
    of engine data, including time series plots and XY plots.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the visualization panel.
        
        Args:
            parent: The parent widget (Enmovito instance)
        """
        super().__init__(parent)
        self.parent = parent  # Reference to the main Enmovito instance
        
        # Initialize attributes
        self.plot_tabs = None
        self.tab_plot_browsers = {}
        self.tab_figures = {}
        self.tab_x_params = {}
        self.add_tab_button = None
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setup_viz_panel()
    
    def setup_viz_panel(self):
        """Set up the visualization panel with tabs for plots."""
        # Create a tab widget for multiple plot workspaces
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setTabsClosable(True)  # Allow tabs to be closed
        self.plot_tabs.tabCloseRequested.connect(self.close_plot_tab)
        self.layout.addWidget(self.plot_tabs)

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
    
    def extract_unit(self, param_name):
        """
        Extract unit from parameter name, e.g., 'Oil Temp (deg F)' -> 'deg F'
        
        Args:
            param_name (str): Parameter name
            
        Returns:
            str: Unit string or "Unknown" if no unit found
        """
        if '(' in param_name and ')' in param_name:
            unit = param_name.split('(')[1].split(')')[0]
            return unit
        return "Unknown"
    
    def generate_plot(self, df, selected_params, selected_display_names, x_param, x_display, 
                     log_file_path, use_celsius, fahrenheit_to_celsius):
        """
        Generate a plot with the selected parameters.
        
        Args:
            df (pandas.DataFrame): The data frame containing the data
            selected_params (list): List of selected parameter names
            selected_display_names (list): List of display names for selected parameters
            x_param (str): X-axis parameter name
            x_display (str): X-axis display name
            log_file_path (str): Path to the log file
            use_celsius (bool): Whether to use Celsius for temperature values
            fahrenheit_to_celsius (function): Function to convert Fahrenheit to Celsius
            
        Returns:
            bool: True if plot was generated successfully, False otherwise
        """
        if not selected_params:
            return False

        # Get the unit for the X parameter
        x_unit = self.extract_unit(x_display)

        # Check if we need to convert X temperature values
        x_values = df[x_param].copy()
        if use_celsius and "deg F" in x_unit:
            x_values = x_values.apply(fahrenheit_to_celsius)
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
                    y_values = df[param].copy()
                    unit_label = unit

                    # Convert temperature values if needed
                    if use_celsius and "deg F" in unit:
                        y_values = y_values.apply(fahrenheit_to_celsius)
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
                    y_values = df[param].copy()
                    unit_label = unit

                    # Convert temperature values if needed
                    if use_celsius and "deg F" in unit:
                        y_values = y_values.apply(fahrenheit_to_celsius)
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

        # Update layout with responsive sizing, mouse wheel zoom, and hover features
        fig.update_layout(
            autosize=True,  # Enable autosize for responsive behavior
            title_text=f"Engine Data Log: {os.path.basename(log_file_path)}",
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
        with open(temp_file, 'r', encoding='utf-8') as file:
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
        with open(temp_file, 'w', encoding='utf-8') as file:
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

        return True

    def clear_tab_plot(self, tab_index):
        """
        Clear the plot from a specific tab.
        
        Args:
            tab_index (int): Index of the tab to clear
        """
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

    def add_plot_tab(self):
        """
        Add a new plot tab to the workspace.
        
        Returns:
            int: Index of the new tab
        """
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
        """
        Close a plot tab.
        
        Args:
            index (int): Index of the tab to close
        """
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

    def check_x_axis_change(self, current_tab_index, x_param, x_display):
        """
        Check if the X-axis parameter has changed and show a warning dialog if needed.
        
        Args:
            current_tab_index (int): Index of the current tab
            x_param (str): New X-axis parameter
            x_display (str): Display name for the new X-axis parameter
            
        Returns:
            bool: True if the change is accepted, False otherwise
        """
        # Check if there's an existing plot with a different X-axis parameter
        if (current_tab_index in self.tab_figures and
            self.tab_figures[current_tab_index] is not None and
            current_tab_index in self.tab_x_params and
            self.tab_x_params[current_tab_index] != x_param):

            # Get the old X-axis parameter display name
            old_x_param_display = ""
            # This would need to be implemented in the main class
            # or passed as a parameter

            # Show the X-axis change warning dialog
            dialog = XAxisChangeDialog(self, old_x_param_display, x_display)
            result = dialog.exec_()

            if result == QDialog.Rejected:
                # User chose to abort
                return False

            # User chose to replace, so we'll clear the existing plot
            self.clear_tab_plot(current_tab_index)

        return True
