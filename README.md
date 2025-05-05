# Enmovito

A Python desktop application for visualizing and analyzing engine data logs from CSV files. Enmovito stands for Engine Monitoring Visualization Tool.

## Features

- **Interactive Time Series Visualization**: Plot multiple engine parameters over time with interactive zooming, panning, and tooltips.
- **XY Plot Capability**: Create scatter plots to analyze relationships between different parameters.
- **Parameter Categories**: Quickly select related parameters using predefined categories (GPS, Altitude, Engine, etc.).
- **Customizable Time Axis**: Select different time columns for the x-axis.
- **User-Friendly Interface**: Simple GUI with intuitive controls for data exploration.
- **Dark and Light Themes**: Choose between dark and light themes for visual comfort.
- **Temperature Unit Conversion**: Switch between Fahrenheit and Celsius for temperature parameters.

## Requirements

- Python 3.6+
- PyQt5
- PyQtWebEngine
- pandas
- numpy
- plotly

## Installation

### Option 1: Run from Source

1. Ensure you have Python installed on your system.
2. Install the required dependencies:

```bash
pip install PyQt5 PyQtWebEngine pandas numpy plotly pyinstaller
```

### Option 2: Use Pre-built Executable

Download the pre-built executable from the releases page (if available).

## Usage

### Running from Source

```bash
python enmovito.py
```

### Building an Executable

You can build a standalone executable using PyInstaller with one of the spec files:

```bash
# Build with example logs
pyinstaller enmovito.spec

# Build without example logs
pyinstaller enmovito_no_examples.spec
```

The executable will be created in the `dist` folder.

### Running the Application

2. Click "Select Log File" to choose a CSV file from the example_logs directory.
3. The application will load the data and display available parameters.
4. Select parameters to visualize:
   - Choose individual parameters from the list
   - Or use the category buttons to select groups of related parameters
5. Click "Generate Plot" to create time series visualizations.
6. Use the "XY Plot" tab to create scatter plots between any two parameters.

## Interacting with Plots

- **Zoom**: Click and drag to zoom into a specific area
- **Pan**: Click and drag in plot area after zooming
- **Reset View**: Double-click to reset to original view
- **Tooltips**: Hover over data points to see exact values
- **Save Image**: Use the plot toolbar to save visualizations as PNG files

## Data Format

The application is designed to work with CSV files that have:
- A header line with airframe information
- A second line with column names
- Subsequent lines with data records

The example logs in the `example_logs` directory follow this format.

## Themes

The application supports two themes:
- **Dark Theme**: Default theme with dark background for reduced eye strain
- **Light Theme**: Bright theme for high-contrast environments

You can switch between themes using the radio buttons in the "Theme Selection" section at the bottom of the control panel.

## Building Notes

When building with PyInstaller, the themes directory is included in the package to ensure proper theme application in the standalone executable. The application uses a resource path helper function to locate theme files correctly whether running from source or as a packaged executable.
