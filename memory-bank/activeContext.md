# Active Context: Enmovito

## Current Work Focus

The Enmovito project is now in a fully functional state with core visualization capabilities implemented and recent bugs fixed. The application can:

1. Load engine data logs from CSV files
3. Create XY plots to analyze relationships between parameters
4. Organize parameters into categories for easier selection
5. Filter parameters by category for improved usability
6. Clear individual plots with dedicated clear buttons
7. Select all visible parameters with a single click
8. Synchronize x-axis zooming while maintaining independent y-axis scales
9. Support dark theme for improved visual comfort
10. Clear all selected parameters with a single click
11. Resize plots within tabs using splitters
12. Use any parameter (including time) as X-axis for plots

The current focus is on:

- **Code refactoring and modularization** to improve maintainability and extensibility
- Optimizing the application for different platforms
- Ensuring robust handling of different CSV file formats
- Improving visualization performance with large datasets
- Adding more advanced analysis capabilities
- Enhancing the user experience with additional UI improvements

## Recent Changes

### Code Refactoring and Modularization

- Continued refactoring the application into a more modular structure:
  - Removed the `extract_unit` function from enmovito.py as it has been moved to the DataHandler class
  - Removed the `fahrenheit_to_celsius` function from enmovito.py as it has been moved to the DataHandler class
  - Removed the `setup_viz_panel` function from enmovito.py as it has been moved to the VisualizationPanel class
  - Refactored the `on_plot_requested` method to use the VisualizationPanel's generate_plot method
  - Extracted the main window functionality from enmovito.py to a dedicated MainWindow class in gui/main_window.py
  - Simplified enmovito.py to serve only as the application entry point
  - Cleaned up imports that were no longer needed after the refactoring
  - Updated references to use the DataHandler and VisualizationPanel methods instead of local implementations
  - Improved code organization with better separation of concerns
  - Reduced code duplication by delegating functionality to appropriate classes

### UI Improvements

- Moved the theme and temperature unit selection widgets to the bottom of the control pane
  - Provides better organization of the UI elements
  - Keeps the most frequently used controls at the top
- Reordered the widgets to place temperature unit selection above theme selection
  - More logical grouping of related settings
  - Improves user workflow when changing settings
- Added a "Select All Visible" button to quickly select all parameters currently visible in the list
  - Particularly useful when a category filter is applied
  - Makes it easy to select all parameters in a specific category with just two clicks
- Removed the global "Clear Plot" buttons that clear all plots at once
  - Kept the individual clear buttons for each plot
  - This provides more granular control over which plots to keep or remove
- Improved subplot visualization with independent y-axis scales
  - Modified the subplot linking code to only link x-axes between subplots
  - Each subplot now maintains its own y-axis scale when using the autoscale button
  - This allows proper visualization of parameters with vastly different value ranges

### Bug Fixes and Improvements

- Fixed QtWebEngineWidgets initialization issues that were causing crashes
  - Added early import of QtWebEngineWidgets
  - Set Qt.AA_ShareOpenGLContexts attribute before creating QApplication
- Resolved file access errors with temporary plot files
  - Used specific paths for temporary HTML files
  - Ensured file paths are absolute
- Fixed theme loading in PyInstaller-packaged executable
  - Added resource_path helper function to correctly locate theme files
  - Modified apply_theme method to use the helper function
  - Added fallback theme styling for cases where theme files can't be loaded
  - Added detailed logging for theme file loading
- Improved parameter handling from CSV files
  - Correctly parsed the complex three-line header structure
  - Used full parameter names from the second row for display
  - Filtered out columns with empty names in the third row
- Enhanced the user interface
  - Added individual clear buttons for each graph
  - Modified category buttons to filter the parameter list instead of selecting parameters
  - Added automatic deselection of parameters after generating a graph
- Fixed X-axis selection and temperature unit issues
  - Replaced X-axis dropdown with a list widget for consistent UI experience
  - Added separate category filter buttons for X-axis parameter selection
  - Fixed temperature conversion when Celsius is selected as the temperature unit
  - Ensured generate button works correctly with both Fahrenheit and Celsius units

### Core Application Development

- Implemented the main application structure using PyQt5
- Created the split-panel interface with control and visualization areas
- Added file selection functionality with default directory set to example_logs
- Implemented parameter selection with both individual and category-based options
- Added build configuration for PyInstaller packaging
  - Created spec file with example logs for complete package
  - Created optimized spec file without example logs for smaller executable size

### Visualization Implementation

- Integrated Plotly for interactive visualizations
- Embedded Plotly visualizations in PyQt using QWebEngineView
- Implemented synchronized x-axis zooming with independent y-axis scales

### Data Handling

- Implemented CSV parsing with special handling for complex header structure
  - Skip the first line (airframe info)
  - Use the second line for full parameter names with units
  - Use the third line for abbreviated parameter names
- Added automatic detection of numeric columns for plotting
- Implemented time column detection and selection
- Created parameter categorization system

## Next Steps

### Short-term Tasks

1. **Performance Optimization**
   - Implement data decimation for large datasets
   - Optimize Plotly rendering for multiple parameters
   - Improve loading time for large CSV files

2. **UI Enhancements**
   - Add parameter search functionality
   - Implement parameter favorites or recent selections
   - Improve visual feedback for filtered parameters

3. **Analysis Features**
   - Add basic statistical analysis display
   - Implement data filtering options
   - Add annotation capabilities for plots

### Medium-term Goals

1. **Advanced Visualization**
   - Add multi-parameter overlay option for time series
   - Implement heat map visualization for parameter correlations
   - Add custom plot templates for common analysis scenarios

2. **Data Export**
   - Add functionality to export visualizations as images
   - Implement report generation with multiple visualizations
   - Add data export for filtered or processed data

3. **User Experience**
   - Create user preferences for default settings
   - Implement session saving and loading
   - Add keyboard shortcuts for common actions

## Active Decisions and Considerations

### UI Design Decisions

- **Split Panel Layout**: The application uses a resizable split panel to balance control options and visualization space
- **Tab-based Visualization**: Different visualization types are organized in tabs for easy switching
- **Category-based Parameter Filtering**: Parameters are grouped by function for easier selection, with filtering capability
- **Individual Clear Buttons**: Each plot has its own clear button for more granular control
- **Parameter Deselection**: Parameters are automatically deselected after generating a plot for better workflow
- **Select All Visible Button**: Allows quick selection of all visible parameters, especially useful with category filtering
- **Independent Y-axis Scaling**: Each subplot maintains its own y-axis scale while sharing x-axis zoom level

### Technical Decisions

- **Plotly vs. Alternatives**: Plotly was chosen over alternatives for its interactive features and integration capabilities
- **Data Structure**: Using pandas DataFrame as the central data structure for flexibility and performance
- **Visualization Embedding**: Using QWebEngineView to embed Plotly visualizations within PyQt
- **Complex Header Handling**: Special parsing for the three-line header structure in CSV files
- **Subplot Linking**: Using Plotly's 'matches' property to link only x-axes between subplots
- **Resource Path Handling**: Using a helper function to locate resources correctly whether running from source or as a packaged executable
- **Fallback Theme Styling**: Implementing inline CSS as a fallback when theme files can't be loaded
- **Modular Architecture**: Moving functionality to dedicated classes to improve maintainability and extensibility
  - DataHandler for data loading and processing
  - VisualizationPanel for plot generation and management
  - ControlPanel for user interface elements

### Open Questions

- How to best handle very large datasets without performance degradation?
- What additional visualization types would be most valuable for engine data analysis?
- How to structure parameter categories for optimal usability?
- Should the application support real-time data visualization in the future?
- How to improve the visual design of the parameter list when filtering is active?

## Important Patterns and Preferences

### Code Organization

- Main application logic in `enmovito.py`
- Data handling functionality in `data_handler.py`
- Control panel in `gui/control_panel.py`
- Visualization panel in `gui/visualization.py`
- Clear separation between UI setup, data handling, and visualization logic
- Modular methods for specific functionality (e.g., `show_all_parameters`, `clear_specific_ts_plot`, `select_all_visible_parameters`)

### Visualization Style

- Interactive plots with zoom, pan, and tooltip capabilities
- Clear labeling of axes and parameters
- Consistent color schemes for parameter types
- Shared x-axis for time series plots for easy comparison
- Independent y-axis scales for optimal visualization of different value ranges

### User Interaction Patterns

- File selection → Parameter selection → Visualization generation
- Category buttons for filtering parameters by type
- "Select All Visible" button for quick selection of filtered parameters
- Tab-based navigation between visualization types
- Direct interaction with plots for exploration

## Project Insights

### Strengths

- Intuitive interface for parameter selection and visualization
- Flexible visualization options
- Good organization of parameters into functional categories with filtering
- Interactive plots that allow detailed data exploration
- Individual plot management for focused analysis
- Synchronized x-axis zooming with independent y-axis scales
- Quick parameter selection with "Select All Visible" button
- Modular code structure with clear separation of concerns

### Areas for Improvement

- Performance with very large datasets
- More advanced analysis capabilities
- Additional visualization types for specific analysis scenarios
- Visual design of the filtered parameter list

### Learnings

- PyQt and Plotly integration requires careful initialization of QtWebEngineWidgets
- Parameter categorization with filtering significantly improves usability for complex datasets
- Interactive visualization is essential for effective data exploration
- CSV parsing needs to be robust to handle complex header structures
- Individual plot management improves the user experience for comparative analysis
- Synchronized x-axis zooming with independent y-axis scales is crucial for comparing parameters with different value ranges
- Quick selection tools like "Select All Visible" significantly improve workflow efficiency
- Modular code organization improves maintainability and extensibility
- Delegating functionality to specialized classes reduces code duplication and improves code quality
