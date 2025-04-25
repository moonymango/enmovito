# System Patterns: Enmovito

## System Architecture

Enmovito follows a straightforward desktop application architecture with clear separation of concerns:

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

### Key Components

1. **Data Layer**
   - CSV file parsing (pandas)
   - Data storage and management (pandas DataFrame)
   - Data filtering and preprocessing

2. **Application Layer**
   - Parameter categorization and management
   - Visualization logic and configuration
   - Data analysis functions

3. **Presentation Layer**
   - PyQt5-based GUI components
   - Plotly visualization integration
   - User interaction handling

## Design Patterns

### Model-View-Controller (MVC)

The application loosely follows the MVC pattern:

- **Model**: Pandas DataFrame storing the engine log data
- **View**: PyQt5 GUI components and Plotly visualizations
- **Controller**: Main application class (EngineDataVisualizer) handling user interactions and coordinating between model and view

### Composite Pattern

The GUI is structured using a composite pattern through PyQt's widget hierarchy:

- Main window contains splitter
- Splitter contains control panel and visualization panel
- Each panel contains various widgets (buttons, lists, tabs)

### Observer Pattern

The application implements an implicit observer pattern through PyQt's signals and slots mechanism:

- UI elements emit signals when user interactions occur
- Slots (methods) are connected to these signals to respond to user actions

### Factory Method

While not explicitly implemented as a separate class, the application uses factory-like methods to create visualizations:

- `generate_plot()` creates time series visualizations
- `generate_xy_plot()` creates XY scatter plot visualizations

## Component Relationships

### Data Flow

```
┌──────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────┐
│  CSV     │────▶│  Pandas   │────▶│ Parameter   │────▶│  Plotly  │
│  File    │     │  DataFrame│     │ Selection   │     │  Plots   │
└──────────┘     └───────────┘     └─────────────┘     └──────────┘
```

### Control Flow

```
┌──────────┐     ┌───────────────┐     ┌─────────────┐
│  User    │────▶│  PyQt GUI     │────▶│ Application │
│  Action  │     │  Components   │     │ Logic       │
└──────────┘     └───────────────┘     └─────────────┘
                         │                    │
                         │                    ▼
                         │              ┌─────────────┐
                         └──────────────│  Update     │
                                        │  Display    │
                                        └─────────────┘
```

## Key Technical Decisions

### GUI Framework: PyQt5

PyQt5 was chosen for its:
- Cross-platform compatibility
- Comprehensive widget set
- Integration with Python
- Support for complex layouts
- Ability to embed web content (for Plotly visualizations)

### Visualization Library: Plotly

Plotly was selected over alternatives like Matplotlib or PyQtGraph because it offers:
- Rich interactive features (zoom, pan, tooltips)
- Modern, attractive visualizations
- Good performance with time series data
- Easy integration with PyQt through HTML embedding
- Support for both time series and XY plots

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

## Critical Implementation Paths

### Data Loading Path

1. User selects CSV file
2. Application reads header lines to understand the structure:
   - First line contains airframe information (skipped)
   - Second line contains full parameter names with units
   - Third line contains abbreviated parameter names
3. Application creates mappings between abbreviated and full parameter names
4. CSV data is loaded using pandas, skipping the first two lines
5. Numeric columns are identified for plotting
6. Time columns are identified for x-axis options
7. UI is updated with available parameters using full names for display

### Visualization Path

1. User selects parameters (possibly after filtering by category)
2. Application retrieves selected data from DataFrame using the actual column names
3. Plotly figure is created with appropriate configuration
4. Figure is rendered to HTML at a specific file path
5. HTML is displayed in PyQt WebEngineView
6. Individual clear button is created for the plot

### Parameter Selection Path

1. User filters parameters by category or selects them directly
2. When a category button is clicked:
   - If it's a new category, parameters are filtered to show only that category
   - If it's the same category again, all parameters are shown
3. When plot is generated, selected parameters are used to create visualization
4. Parameters are automatically deselected after plot generation

## Extension Points

The system is designed with several extension points:

1. **Additional Visualization Types**
   - New tab widgets can be added to the visualization panel
   - New plot generation methods can be implemented
   - Individual plot management can be extended to new visualization types

2. **Parameter Categories**
   - The category dictionary can be extended with new parameter groupings
   - The filtering mechanism can be enhanced with search functionality

3. **Data Analysis Functions**
   - Additional analysis methods can be added to process and visualize data
   - Statistical analysis can be integrated into the visualization

4. **Data Sources**
   - The data loading mechanism can be extended to support different file formats
   - The header parsing logic can be adapted for different CSV structures
