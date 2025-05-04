# Technical Context: Enmovito

## Technologies Used

### Core Technologies

1. **Python 3.6+**
   - Primary programming language
   - Chosen for its simplicity, readability, and extensive library ecosystem

2. **PyQt5**
   - GUI framework for desktop application
   - Provides cross-platform compatibility (Windows, macOS, Linux)
   - Includes QtWebEngine for embedding web content

3. **Pandas**
   - Data manipulation and analysis library
   - Handles CSV parsing and data storage
   - Provides efficient data structures for large datasets

4. **NumPy**
   - Numerical computing library
   - Supports efficient array operations
   - Used by Pandas and Plotly for data processing

5. **Plotly**
   - Interactive visualization library
   - Generates HTML/JavaScript-based plots
   - Provides rich interactive features (zoom, pan, tooltips)
   - Supports advanced subplot configuration

### File Formats

1. **CSV (Comma-Separated Values)**
   - Primary data source format
   - Specific format with airframe information header
   - Contains time series data with multiple parameters

## Development Setup

### Environment Management

The project uses a dedicated virtual environment for development and execution. The specific virtual environment to use is:

```
/home/moonymango/venv/qt
```

This virtual environment contains all the necessary dependencies:

- Python 3.12
- PyQt5 with QtWebEngine support
- Pandas
- NumPy
- Plotly
- PyInstaller for packaging

To run the application using this virtual environment:

```bash
/home/moonymango/venv/qt/bin/python engine_data_visualizer.py
```

To create a standalone executable using PyInstaller:

```bash
/home/moonymango/venv/qt/bin/pyinstaller --onefile --windowed --add-data "themes:themes" --add-data "example_logs:example_logs" engine_data_visualizer.py
```

### Dependencies

As specified in `requirements.txt`:
```
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0
pandas>=1.0.0
numpy>=1.18.0
plotly>=4.14.0
```

### Development Tools

1. **PyQt UI Tools**
   - The `generate_ui` script uses `pyuic5` to convert UI files to Python code
   - Command: `pyuic5 -x src/window.ui -o src/window.py`

2. **Version Control**
   - Git is used for version control
   - Standard Python `.gitignore` file is included

3. **Packaging Tools**
   - PyInstaller is used to create standalone executables
   - Creates self-contained packages for Linux and Windows
   - Includes all necessary dependencies and resources
   - Command: `pyinstaller --onefile --windowed --add-data "themes:themes" --add-data "example_logs:example_logs" engine_data_visualizer.py`

## Technical Constraints

### Performance Considerations

1. **Large File Handling**
   - CSV log files can be large (multiple MB)
   - Pandas is used for efficient data loading and manipulation
   - Data visualization must remain responsive with large datasets

2. **Visualization Performance**
   - Plotly generates interactive HTML/JavaScript visualizations
   - Multiple parameters can be plotted simultaneously
   - Performance may degrade with very large datasets or many parameters

### Cross-Platform Compatibility

1. **GUI Consistency**
   - PyQt5 provides consistent UI across platforms
   - Some platform-specific behaviors may need to be handled

2. **File System Access**
   - File dialogs use PyQt's cross-platform implementation
   - Default directory is set to "example_logs" relative to the current working directory

### Embedding Web Content

1. **PyQtWebEngine**
   - Required for displaying Plotly visualizations
   - Adds significant dependency weight
   - May have platform-specific installation requirements

## Data Structure

### CSV File Format

The application is designed to work with CSV files that have:
1. A header line with airframe information (skipped during parsing)
2. A second line with column names
3. Subsequent lines with data records

Example header:
```
#airframe_info,log_version="1.00",log_content_version="1.02",product="GDU 460",aircraft_ident="NG054",unit_software_part_number="006-B1727-2W",software_version="9.14",system_id="60002CBC443E8",unit="PFD1",airframe_hours="20.3",engine_hours="14.7",engine_cycles="4"
```

### Parameter Categories

The application organizes parameters into predefined categories:
- GPS: Latitude, Longitude, AltGPS, GndSpd, TRK
- Altitude: AltP, AltInd, VSpd, AGL
- Attitude: Pitch, Roll, HDG
- Engine: E1 RPM, E1 MAP, E1 %Pwr, E1 FFlow, E1 OilT, E1 OilP
- Temperature: E1 CHT1-6, E1 EGT1-6
- Electrical: Volts1, Volts2, Amps1

## Tool Usage Patterns

### Data Loading

```python
# Read the header lines to understand the structure
with open(file_path, 'r') as f:
    # Skip the first line (airframe info)
    next(f)
    # Read the second line (full parameter names with units)
    full_names = next(f).strip().split(',')
    # Read the third line (abbreviated parameter names)
    abbr_names = next(f).strip().split(',')

# Create mappings between abbreviated names and full names
abbr_to_full = {}
full_to_abbr = {}
for i, (abbr, full) in enumerate(zip(abbr_names, full_names)):
    if abbr.strip():  # Only include columns with non-empty abbreviated names
        abbr_to_full[abbr] = full
        full_to_abbr[full] = abbr

# Read the CSV file, skipping the first 2 lines and using the 3rd line as header
df = pd.read_csv(file_path, skiprows=2, header=0)

# Get numeric columns for plotting
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
```

### Parameter Selection

```python
# Select all visible parameters
def select_all_visible_parameters(self):
    """Select all parameters that are currently visible in the list."""
    # First, clear current selection
    self.param_list.clearSelection()
    
    # Then select all visible items
    for i in range(self.param_list.count()):
        item = self.param_list.item(i)
        if not item.isHidden():
            item.setSelected(True)
```

### Visualization Creation

#### Time Series Plot with Independent Y-axis Scales

```python
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
```

#### XY Plot

```python
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df[x_param], 
        y=df[y_param], 
        mode='markers', 
        name=f'{y_param} vs {x_param}'
    )
)

# Create a temporary HTML file and display it
temp_file = os.path.join(os.getcwd(), "temp-plot.html")
plot_path = plot(fig, output_type='file', filename=temp_file, auto_open=False)
```

### Plot Display and Management

```python
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
```

### Parameter Filtering

```python
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
```

## Integration Points

### PyQt and Plotly Integration

The application integrates PyQt with Plotly using PyQtWebEngine:
1. QtWebEngineWidgets must be imported early in the file
2. Qt.AA_ShareOpenGLContexts attribute must be set before creating QApplication
3. Plotly generates HTML/JavaScript visualizations
4. These are saved to specific temporary files with absolute paths
5. QWebEngineView loads and displays these files within the PyQt application

### User Interaction Flow

1. User interacts with PyQt GUI components (parameter filtering, selection)
2. PyQt signals trigger application logic
3. Application logic updates data model and generates visualizations
4. Visualizations are displayed in embedded web views with individual clear buttons
5. User can interact with both PyQt components and embedded visualizations
6. User can clear individual plots using dedicated clear buttons

### Parameter Selection Flow

1. User clicks a category button to filter parameters
2. User clicks "Select All Visible" to select all filtered parameters
3. User clicks "Generate Plot" to create visualization
4. Parameters are automatically deselected after plot generation

### Subplot Synchronization

1. Subplots are created with shared x-axes
2. X-axes are linked using Plotly's 'matches' property
3. Y-axes remain independent for optimal scaling
4. When user zooms on one subplot, all x-axes zoom together
5. Y-axes maintain their own scales based on the data range
