# Progress: Enmovito

## Current Status

Enmovito is now in a fully functional state with core features implemented and recent bugs fixed. The application successfully loads engine data logs, visualizes parameters in both time series and XY plots, and provides an intuitive interface for data exploration with improved parameter filtering, plot management, and visualization capabilities. Recent additions include dark theme support, resizable plots, unified X-axis parameter selection, and a standalone executable package.

### Development Status: Beta

The application is stable for its core functionality but still has areas for improvement and feature additions before reaching a production-ready state. Recent bug fixes and UI enhancements have significantly improved stability and usability. The application has been successfully packaged into a self-contained executable for Linux, making it easier to distribute and use.

## What Works

### Core Functionality

✅ **Data Loading**
- CSV file loading with special handling for complex header structure
- Proper parsing of the three-line header format
- Automatic detection of numeric columns for plotting
- Time column identification and selection

✅ **User Interface**
- Split-panel layout with control and visualization areas
- Parameter selection list with multi-select capability
- Category-based parameter filtering
- "Select All Visible" button for quick selection of filtered parameters
- "Clear Selection" button to deselect all parameters at once
- Dark theme support for improved visual comfort
- Tab-based visualization switching
- Individual clear buttons for each plot
- Automatic parameter deselection after plot generation
- Resizable plots within tabs using splitters
- Unified X-axis parameter selection for all plot types

✅ **Time Series Visualization**
- Multi-parameter time series plots
- Synchronized x-axis zooming with independent y-axis scales
- Interactive features (zoom, pan, tooltips)
- Dynamic subplot creation based on selected parameters
- Individual plot management

✅ **XY Plot Visualization**
- Scatter plot creation for any two parameters
- Interactive exploration of parameter relationships
- Proper axis labeling and plot configuration
- Individual plot management

✅ **Parameter Organization**
- Predefined categories for common parameter groups
- Parameter filtering by category
- Visual indication of active category filter
- Quick selection of all visible parameters

## What's Left to Build

### High Priority

🔲 **Performance Optimization**
- Data decimation for large datasets
- Improved loading time for large CSV files
- Memory usage optimization

🔲 **Enhanced Analysis Features**
- Basic statistical analysis display
- Data filtering options
- Trend line and curve fitting for XY plots

🔲 **UI Improvements**
- Parameter search functionality
- Improved parameter list organization
- Better visual feedback during data loading

### Medium Priority

🔲 **Advanced Visualization Options**
- Multi-parameter overlay for time series
- Heat map visualization for parameter correlations
- Custom plot templates for common analysis scenarios

🔲 **Data Export**
- Export visualizations as images
- Report generation with multiple visualizations
- Data export for filtered or processed data

🔲 **User Experience Enhancements**
- User preferences for default settings
- Session saving and loading
- Keyboard shortcuts for common actions

### Low Priority

🔲 **Additional Data Sources**
- Support for different log file formats
- Direct connection to data acquisition systems
- Real-time data visualization

🔲 **Advanced Analysis**
- Anomaly detection algorithms
- Comparative analysis between multiple logs
- Custom formula creation for derived parameters

## Known Issues

### Performance Issues

1. **Large File Handling**
   - Loading very large CSV files can be slow
   - Memory usage increases significantly with file size
   - Plotting many parameters simultaneously can reduce responsiveness

2. **Visualization Rendering**
   - Initial rendering of Plotly visualizations can be slow with many data points
   - Multiple plots in time series view can lead to performance degradation

### UI Issues

1. **Parameter Selection**
   - Long parameter lists can be difficult to navigate
   - No search capability for parameters
   - Visual design of filtered parameter list could be improved

2. **Plot Interaction**
   - No way to save or export visualizations directly from the UI
   - Limited customization options for plot appearance
   - No annotations or markers for important events

### Technical Issues

1. **PyQt and Plotly Integration**
   - Memory leaks possible with multiple plot generations
   - Limited communication between Plotly interactions and PyQt application

## Evolution of Project Decisions

### Initial Approach

The project initially focused on creating a simple visualization tool for engine data logs with basic plotting capabilities. Key decisions included:

- Using PyQt for the GUI framework due to its cross-platform capabilities
- Implementing a basic file loading mechanism for CSV files
- Creating simple static plots for parameter visualization

### Current Approach

As the project evolved, several key decisions shaped its current state:

1. **Visualization Library Selection**
   - Moved from considering Matplotlib to using Plotly for better interactivity
   - This decision significantly enhanced the user experience but added complexity to the integration with PyQt

2. **UI Design Evolution**
   - Started with a simple single-panel design
   - Evolved to a split-panel approach with resizable areas
   - Added tab-based organization for different visualization types
   - Implemented individual plot management with dedicated clear buttons
   - Added "Select All Visible" button for improved workflow
   - Removed global "Clear Plot" buttons in favor of individual plot management

3. **Parameter Organization**
   - Initially listed all parameters alphabetically
   - Added category-based organization to improve usability
   - Evolved from category-based selection to category-based filtering
   - Added visual indication of active category filters
   - Implemented "Select All Visible" functionality for quick selection of filtered parameters

4. **Data Handling**
   - Started with basic CSV parsing
   - Developed robust handling for the complex three-line header structure
   - Implemented proper mapping between abbreviated and full parameter names
   - Improved filtering of valid columns for display and analysis

5. **Visualization Capabilities**
   - Initially implemented basic time series plots
   - Added XY plot functionality for parameter correlation analysis
   - Implemented synchronized x-axis zooming with independent y-axis scales
   - Enhanced subplot configuration for better visualization of parameters with different value ranges

### Future Direction

Based on experience and user feedback, the project is evolving toward:

1. **Performance-Focused Improvements**
   - Implementing data decimation and sampling techniques
   - Optimizing memory usage for large datasets
   - Improving rendering performance for multiple plots

2. **Enhanced Analysis Capabilities**
   - Adding statistical analysis features
   - Implementing data filtering and processing
   - Adding more advanced visualization types

3. **User Experience Refinement**
   - Improving parameter filtering and search capabilities
   - Adding customization options for visualizations
   - Implementing session management and preferences
   - Enhancing visual design of filtered parameter lists

## Milestones and Achievements

### Completed Milestones

1. **Core Application Framework** - *Completed*
   - Basic PyQt application structure
   - File loading and data parsing
   - Parameter selection interface

2. **Basic Visualization** - *Completed*
   - Time series plotting functionality
   - XY plot capability
   - Interactive plot features

3. **Parameter Organization** - *Completed*
   - Category-based parameter grouping
   - Category filtering functionality
   - Multi-parameter selection
   - Quick selection of filtered parameters

4. **Bug Fixes and Stability** - *Completed*
   - Fixed QtWebEngineWidgets initialization issues
   - Resolved file access errors
   - Improved parameter handling from CSV files
   - Enhanced user interface with individual plot management

5. **UI Enhancements** - *Completed*
   - Moved theme and temperature unit selection widgets to the bottom of the control pane
   - Reordered widgets to place temperature unit selection above theme selection
   - Added "Select All Visible" button for quick parameter selection
   - Added "Clear Selection" button to deselect all parameters at once
   - Implemented dark theme support for improved visual comfort
   - Removed global "Clear Plot" buttons in favor of individual plot management
   - Implemented synchronized x-axis zooming with independent y-axis scales
   - Improved plot appearance by removing bright frames around plots
   - Added resizable plots within tabs using splitters
   - Replaced X-axis dropdown with a list widget for consistent UI experience
   - Added separate category filter buttons for X-axis parameter selection
   - Fixed temperature conversion when Celsius is selected as the temperature unit
   - Ensured generate button works correctly with both Fahrenheit and Celsius units
   - Created standalone executable for easier distribution

### Upcoming Milestones

1. **Application Packaging** - *Partially Completed*
   - ✅ Create self-contained executable for Linux
   - 🔲 Create self-contained executable for Windows
   - ✅ Include all necessary dependencies and resources (themes only, example logs excluded)
   - ✅ Fixed theme loading in PyInstaller-packaged executable
     - Added resource_path helper function to correctly locate theme files
     - Added fallback theme styling for cases where theme files can't be loaded
     - Created optimized spec file without example logs for smaller executable size

2. **Performance Optimization** - *In Progress*
   - Data decimation implementation
   - Memory usage optimization
   - Rendering performance improvements

3. **Enhanced Analysis** - *Planned*
   - Statistical analysis features
   - Data filtering capabilities
   - Advanced visualization options

4. **User Experience Refinement** - *Planned*
   - Parameter search functionality
   - Improved visual design for filtered parameters
   - Customization options
   - Session management
