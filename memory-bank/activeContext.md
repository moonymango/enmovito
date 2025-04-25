# Active Context: Enmovito

## Current Work Focus

The Enmovito project is now in a fully functional state with core visualization capabilities implemented and recent bugs fixed. The application can:

1. Load engine data logs from CSV files
2. Display time series visualizations of multiple parameters
3. Create XY plots to analyze relationships between parameters
4. Organize parameters into categories for easier selection
5. Filter parameters by category for improved usability
6. Clear individual plots with dedicated clear buttons

The current focus is on:

- Ensuring robust handling of different CSV file formats
- Improving visualization performance with large datasets
- Adding more advanced analysis capabilities
- Enhancing the user experience with additional UI improvements

## Recent Changes

### Bug Fixes and Improvements

- Fixed QtWebEngineWidgets initialization issues that were causing crashes
  - Added early import of QtWebEngineWidgets
  - Set Qt.AA_ShareOpenGLContexts attribute before creating QApplication
- Resolved file access errors with temporary plot files
  - Used specific paths for temporary HTML files
  - Ensured file paths are absolute
- Improved parameter handling from CSV files
  - Correctly parsed the complex three-line header structure
  - Used full parameter names from the second row for display
  - Filtered out columns with empty names in the third row
- Enhanced the user interface
  - Added individual clear buttons for each graph
  - Modified category buttons to filter the parameter list instead of selecting parameters
  - Added automatic deselection of parameters after generating a graph

### Core Application Development

- Implemented the main application structure using PyQt5
- Created the split-panel interface with control and visualization areas
- Added file selection functionality with default directory set to example_logs
- Implemented parameter selection with both individual and category-based options

### Visualization Implementation

- Integrated Plotly for interactive visualizations
- Implemented time series plotting with multiple parameters
- Added XY plot functionality for parameter correlation analysis
- Embedded Plotly visualizations in PyQt using QWebEngineView

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
   - Add a "Show All" button to reset category filters
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

### Technical Decisions

- **Plotly vs. Alternatives**: Plotly was chosen over alternatives for its interactive features and integration capabilities
- **Data Structure**: Using pandas DataFrame as the central data structure for flexibility and performance
- **Visualization Embedding**: Using QWebEngineView to embed Plotly visualizations within PyQt
- **Complex Header Handling**: Special parsing for the three-line header structure in CSV files

### Open Questions

- How to best handle very large datasets without performance degradation?
- What additional visualization types would be most valuable for engine data analysis?
- How to structure parameter categories for optimal usability?
- Should the application support real-time data visualization in the future?
- How to improve the visual design of the parameter list when filtering is active?

## Important Patterns and Preferences

### Code Organization

- Main application logic in `engine_data_visualizer.py`
- Example usage patterns in `example_usage.py`
- Clear separation between UI setup, data handling, and visualization logic
- Modular methods for specific functionality (e.g., `show_all_parameters`, `clear_specific_ts_plot`)

### Visualization Style

- Interactive plots with zoom, pan, and tooltip capabilities
- Clear labeling of axes and parameters
- Consistent color schemes for parameter types
- Shared x-axis for time series plots for easy comparison
- Individual clear buttons for each plot with descriptive labels

### User Interaction Patterns

- File selection → Parameter selection → Visualization generation
- Category buttons for filtering parameters by type
- Tab-based navigation between visualization types
- Direct interaction with plots for exploration
- Individual plot clearing for focused analysis

## Project Insights

### Strengths

- Intuitive interface for parameter selection and visualization
- Flexible visualization options with both time series and XY plots
- Good organization of parameters into functional categories with filtering
- Interactive plots that allow detailed data exploration
- Individual plot management for focused analysis

### Areas for Improvement

- Performance with very large datasets
- More advanced analysis capabilities
- Better integration between time series and XY plot views
- Additional visualization types for specific analysis scenarios
- Visual design of the filtered parameter list

### Learnings

- PyQt and Plotly integration requires careful initialization of QtWebEngineWidgets
- Parameter categorization with filtering significantly improves usability for complex datasets
- Interactive visualization is essential for effective data exploration
- CSV parsing needs to be robust to handle complex header structures
- Individual plot management improves the user experience for comparative analysis
