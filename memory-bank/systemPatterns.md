# System Patterns: Enmovito

## System Architecture

Enmovito has evolved from a monolithic application to a more modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Enmovito Application                  │
├─────────────┬─────────────────────────┬─────────────────┤
│ Data Layer  │     Application Layer    │ Presentation    │
│             │                         │ Layer           │
├─────────────┼─────────────────────────┼─────────────────┤
│ - CSV       │ - Data Processing       │ - PyQt5 GUI     │
│   Parsing   │ - Parameter Management  │ - Plotly        │
│ - Data      │ - Visualization Logic   │   Visualization │
│   Storage   │ - Analysis Functions    │ - User          │
│             │                         │   Interaction   │
└─────────────┴─────────────────────────┴─────────────────┘
```

The application is now organized into a modular package structure:

```
enmovito/
├── __init__.py
├── data_handler.py       # Data loading and management
├── gui/
│   ├── __init__.py
│   ├── control_panel.py  # User interface for parameter selection
│   ├── main_window.py    # Main application window (in progress)
│   └── visualization.py  # Visualization components and plot generation
├── utils.py              # Utility functions
└── main.py               # Main application entry point (in progress)
```

### Key Components

1. **Data Layer (data_handler.py)**
   - CSV file parsing (pandas)
   - Data storage and management (pandas DataFrame)
   - Data filtering and preprocessing
   - Unit extraction and conversion functions

2. **Application Layer (enmovito.py)**
   - Main application logic
   - Coordination between components
   - Event handling and signal connections
   - Resource management

3. **Presentation Layer**
   - **Control Panel (gui/control_panel.py)**
     - Parameter selection and filtering
     - Category-based organization
     - User interface controls
   - **Visualization Panel (gui/visualization.py)**
     - Plot generation and management
     - Tab-based organization
     - Interactive visualization display

## Design Patterns

### Model-View-Controller (MVC)

The application follows the MVC pattern more closely after refactoring:

- **Model**: DataHandler class managing data loading and processing
- **View**: ControlPanel and VisualizationPanel classes handling UI presentation
- **Controller**: Main Enmovito class coordinating between model and views

### Composite Pattern

The GUI is structured using a composite pattern through PyQt's widget hierarchy:

- Main window contains splitter
- Splitter contains control panel and visualization panel
- Each panel contains various widgets (buttons, lists, tabs)
- Plot containers include both the plot and its control buttons

### Observer Pattern

The application implements an observer pattern through PyQt's signals and slots mechanism:

- UI elements emit signals when user interactions occur
- Slots (methods) are connected to these signals to respond to user actions
- Custom signals like plot_requested, temperature_unit_changed, and theme_changed facilitate communication between components

### Factory Method

The application uses factory-like methods to create visualizations:

- VisualizationPanel.generate_plot() creates time series visualizations
- VisualizationPanel.generate_xy_plot() creates XY scatter plot visualizations

### Command Pattern

The application implements a simplified command pattern for plot management:

- Each plot has its own clear button with a specific command
- The command is connected to a method that removes only that specific plot
- This allows for granular control over individual plots

## Component Relationships

### Data Flow

```
┌──────────┐     ┌───────────────┐     ┌─────────────────┐     ┌──────────────┐
│  CSV     │────▶│  DataHandler  │────▶│  ControlPanel   │────▶│ Visualization│
│  File    │     │  Class        │     │  (Parameter     │     │ Panel        │
└──────────┘     └───────────────┘     │  Selection)     │     └──────────────┘
                        │              └─────────────────┘             │
                        │                       │                      │
                        │                       ▼                      ▼
                        │              ┌─────────────────┐     ┌──────────────┐
                        └──────────────│  Main Enmovito  │────▶│  Plotly      │
                                       │  Application    │     │  Plots       │
                                       └─────────────────┘     └──────────────┘
```

### Control Flow

```
┌──────────┐     ┌───────────────┐     ┌─────────────────┐
│  User    │────▶│  ControlPanel │────▶│ Main Enmovito   │
│  Action  │     │  Components   │     │ Application     │
└──────────┘     └───────────────┘     └─────────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Display     │◀────│ Visualization │◀────│ DataHandler     │
│  Results     │     │ Panel         │     │ Processing      │
└──────────────┘     └───────────────┘     └─────────────────┘
```

### Parameter Selection Flow

```
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Category    │────▶│  Filter       │────▶│ Select All      │
│  Selection   │     │  Parameters   │     │ Visible Button  │
└──────────────┘     └───────────────┘     └─────────────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Generate    │◀────│  Parameter    │◀────│ Select All      │
│  Plot        │     │  Selection    │     │ Visible Action  │
└──────────────┘     └───────────────┘     └─────────────────┘
```

### Visualization Generation Flow

```
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Parameter   │────▶│  Main Enmovito│────▶│ Visualization   │
│  Selection   │     │  Application  │     │ Panel           │
└──────────────┘     └───────────────┘     └─────────────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│  Display     │◀────│  Create HTML  │◀────│ Generate Plotly │
│  in Browser  │     │  File         │     │ Figure          │
└──────────────┘     └───────────────┘     └─────────────────┘
```

## Key Technical Decisions

### GUI Framework: PyQt5

PyQt5 was chosen for its:
- Cross-platform compatibility
- Comprehensive widget set
- Integration with Python
- Support for complex layouts
- Ability to embed web content (for Plotly visualizations)
- Theming capabilities through QSS (Qt Style Sheets)

### Visualization Library: Plotly

Plotly was selected over alternatives like Matplotlib or PyQtGraph because it offers:
- Rich interactive features (zoom, pan, tooltips)
- Modern, attractive visualizations
- Good performance with time series data
- Easy integration with PyQt through HTML embedding
- Support for both time series and XY plots
- Advanced subplot configuration options

### Data Processing: Pandas

Pandas provides:
- Efficient CSV parsing
- Powerful data manipulation capabilities
- Good integration with Plotly
- Support for handling large datasets
- Built-in statistical functions

### QtWebEngineWidgets Integration

Proper integration of QtWebEngineWidgets is critical:
- Must be imported early in the file
- Qt.AA_ShareOpenGLContexts attribute must be set before creating QApplication
- QUrl must be imported from PyQt5.QtCore for file loading

### Subplot Configuration

The subplot configuration is designed to:
- Share x-axes between subplots for synchronized zooming
- Maintain independent y-axes for optimal visualization of different value ranges
- Group parameters by unit type for logical organization
- Use Plotly's 'matches' property to link only x-axes between subplots

### Modular Architecture

The modular architecture provides several benefits:
- Clear separation of concerns
- Improved maintainability
- Better code organization
- Reduced code duplication
- Easier testing and debugging
- More flexible extension points

## Critical Implementation Paths

### Data Loading Path

1. User selects CSV file via the ControlPanel
2. Main application passes the file path to the DataHandler
3. DataHandler reads header lines to understand the structure:
   - First line contains airframe information (skipped)
   - Second line contains full parameter names with units
   - Third line contains abbreviated parameter names
4. DataHandler creates mappings between abbreviated and full parameter names
5. CSV data is loaded using pandas, skipping the first two lines
6. Numeric columns are identified for plotting
7. Time columns are identified for x-axis options
8. ControlPanel is updated with available parameters using full names for display

### Visualization Path

1. User selects parameters in the ControlPanel (possibly after filtering by category)
2. User can click "Select All Visible" to select all currently visible parameters
3. User clicks "Generate Plot" button, triggering the plot_requested signal
4. Main application receives the signal and calls the VisualizationPanel's generate_plot method
5. VisualizationPanel retrieves selected data from DataFrame using the actual column names
6. Parameters are grouped by unit type using DataHandler's extract_unit method
7. Plotly figure is created with appropriate configuration
   - Subplots are created for each unit group
   - X-axes are linked for synchronized zooming
   - Y-axes remain independent for optimal scaling
8. Figure is rendered to HTML at a specific file path
9. HTML is displayed in PyQt WebEngineView within the VisualizationPanel
10. Individual clear button is created for the plot

### Parameter Selection Path

1. User filters parameters by category or selects them directly in the ControlPanel
2. When a category button is clicked:
   - If it's a new category, parameters are filtered to show only that category
   - If it's the same category again, all parameters are shown
3. User can click "Select All Visible" to quickly select all filtered parameters
4. User can click "Clear Selection" to deselect all parameters at once
5. When plot is generated, selected parameters are used to create visualization
6. Parameters are automatically deselected after plot generation

### Theming Path

1. User selects theme (Dark or Light) using radio buttons in the ControlPanel
2. ControlPanel emits the theme_changed signal
3. Main application receives the signal and calls the appropriate theme method
4. Application loads the appropriate QSS file from the themes directory
5. QSS is applied to the application using setStyleSheet
6. QPalette is updated with appropriate colors for the selected theme
7. Plotly visualizations are configured with matching colors for consistency

### Plot Management Path

1. Each plot is created with its own container and clear button in the VisualizationPanel
2. Clear button is connected to a specific method for that plot
3. When clear button is clicked, only that specific plot is removed
4. If all plots are removed, the placeholder is shown again

## Extension Points

The system is designed with several extension points:

1. **Additional Visualization Types**
   - New tab widgets can be added to the VisualizationPanel
   - New plot generation methods can be implemented in the VisualizationPanel
   - Individual plot management can be extended to new visualization types

2. **Parameter Categories**
   - The category dictionary can be extended with new parameter groupings
   - The filtering mechanism can be enhanced with search functionality
   - The "Select All Visible" functionality can be extended with additional selection options

3. **Data Analysis Functions**
   - Additional analysis methods can be added to the DataHandler
   - Statistical analysis can be integrated into the visualization
   - Trend line and curve fitting can be added to XY plots

4. **Data Sources**
   - The DataHandler can be extended to support different file formats
   - The header parsing logic can be adapted for different CSV structures
   - Real-time data visualization could be implemented in the future

5. **User Interface Enhancements**
   - Parameter search functionality can be added to the ControlPanel
   - Custom plot templates can be implemented in the VisualizationPanel
   - Additional theme options beyond dark and light
   - User preferences for default settings can be added
   - Session management for saving and loading visualization states
   - Keyboard shortcuts for common actions like parameter selection and clearing

6. **Application Packaging**
   - PyInstaller configuration for different platforms
   - Customized installers with platform-specific features
   - Auto-update functionality for new versions
