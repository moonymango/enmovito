"""
Example script demonstrating how to use the engine data visualization functionality programmatically.
This can be useful for automated analysis or integration into other Python applications.
"""

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_engine_data(file_path):
    """
    Load engine data from a CSV file, skipping the first line (airframe info).
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: The loaded data
    """
    # Skip the first line (airframe info) and use the second line as header
    df = pd.read_csv(file_path, skiprows=1)
    return df

def create_time_series_plot(df, time_column, parameters):
    """
    Create a time series plot for the specified parameters.
    
    Args:
        df (pandas.DataFrame): The data frame containing the data
        time_column (str): The column to use for the x-axis (time)
        parameters (list): List of parameter names to plot
        
    Returns:
        plotly.graph_objects.Figure: The created figure
    """
    # Create a subplot for each parameter
    fig = make_subplots(
        rows=len(parameters), 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02,
        subplot_titles=parameters
    )
    
    # Add a trace for each parameter
    for i, param in enumerate(parameters):
        fig.add_trace(
            go.Scatter(x=df[time_column], y=df[param], name=param),
            row=i+1, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=200 * len(parameters),
        width=900,
        title_text=f"Engine Data Time Series",
        showlegend=False,
    )
    
    return fig

def create_xy_plot(df, x_param, y_param):
    """
    Create an XY scatter plot between two parameters.
    
    Args:
        df (pandas.DataFrame): The data frame containing the data
        x_param (str): The parameter to use for the x-axis
        y_param (str): The parameter to use for the y-axis
        
    Returns:
        plotly.graph_objects.Figure: The created figure
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df[x_param], 
            y=df[y_param], 
            mode='markers', 
            name=f'{y_param} vs {x_param}'
        )
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        width=900,
        title_text=f"{y_param} vs {x_param}",
        xaxis_title=x_param,
        yaxis_title=y_param,
    )
    
    return fig

def analyze_engine_parameters(df, engine_params):
    """
    Perform basic statistical analysis on engine parameters.
    
    Args:
        df (pandas.DataFrame): The data frame containing the data
        engine_params (list): List of engine parameter names to analyze
        
    Returns:
        dict: Dictionary containing analysis results
    """
    results = {}
    
    for param in engine_params:
        if param in df.columns:
            param_data = df[param].dropna()
            
            results[param] = {
                'mean': param_data.mean(),
                'min': param_data.min(),
                'max': param_data.max(),
                'std': param_data.std()
            }
    
    return results

def main():
    # Example usage
    log_dir = os.path.join(os.getcwd(), "example_logs")
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.csv')]
    
    if not log_files:
        print("No log files found in the example_logs directory.")
        return
    
    # Use the first log file as an example
    example_file = os.path.join(log_dir, log_files[0])
    print(f"Loading data from: {example_file}")
    
    # Load the data
    df = load_engine_data(example_file)
    
    # Display basic information about the data
    print(f"Data shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns[:10])}...")
    
    # Example: Create a time series plot for engine RPM, MAP, and oil temperature
    engine_params = ["E1 RPM", "E1 MAP", "E1 OilT"]
    time_column = "Lcl Time"
    
    # Check if the parameters exist in the data
    available_params = [p for p in engine_params if p in df.columns]
    
    if available_params:
        print(f"Creating time series plot for: {', '.join(available_params)}")
        fig = create_time_series_plot(df, time_column, available_params)
        
        # Save the plot to an HTML file
        output_file = "engine_time_series.html"
        fig.write_html(output_file)
        print(f"Time series plot saved to: {output_file}")
        
        # Optionally show the plot in a browser
        # fig.show()
    
    # Example: Create an XY plot for RPM vs. Manifold Pressure
    if "E1 RPM" in df.columns and "E1 MAP" in df.columns:
        print("Creating XY plot for RPM vs. MAP")
        xy_fig = create_xy_plot(df, "E1 RPM", "E1 MAP")
        
        # Save the plot to an HTML file
        output_file = "rpm_vs_map.html"
        xy_fig.write_html(output_file)
        print(f"XY plot saved to: {output_file}")
        
        # Optionally show the plot in a browser
        # xy_fig.show()
    
    # Example: Analyze engine parameters
    analysis_results = analyze_engine_parameters(df, engine_params)
    print("\nEngine Parameter Analysis:")
    for param, stats in analysis_results.items():
        print(f"\n{param}:")
        for stat_name, value in stats.items():
            print(f"  {stat_name}: {value:.2f}")

if __name__ == "__main__":
    main()
