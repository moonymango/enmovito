import os
import pandas as pd
import numpy as np

class DataHandler:
    """
    Handles data loading, processing, and management for the Enmovito application.
    Responsible for CSV parsing, parameter categorization, and data access.
    """
    def __init__(self):
        # Initialize data storage
        self.df = None
        self.log_file_path = None
        self.numeric_columns = []
        self.abbr_to_full = {}
        self.full_to_abbr = {}
        self.use_celsius = False  # Default to Fahrenheit
        
        # Define parameter categories - using abbreviated names
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

    def load_data(self, file_path):
        """
        Load and parse CSV file with engine data.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            bool: True if loading was successful, False otherwise
            str: Error message if loading failed, empty string otherwise
        """
        try:
            self.log_file_path = file_path
            
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

            # Get numeric columns for plotting
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            return True, ""
            
        except Exception as e:
            return False, str(e)

    def get_all_columns(self):
        """
        Get all column names from the DataFrame.
        
        Returns:
            list: List of all column names
        """
        if self.df is None:
            return []
        return self.df.columns.tolist()

    def get_display_names(self):
        """
        Get display names (full names) for all columns.
        
        Returns:
            list: List of tuples (display_name, column_name)
        """
        if self.df is None:
            return []
            
        all_columns = self.get_all_columns()
        display_columns = []
        
        for col in all_columns:
            # Get the full name from the mapping
            display_name = self.abbr_to_full.get(col, col)
            display_columns.append((display_name, col))
            
        return display_columns

    def get_numeric_columns(self):
        """
        Get all numeric column names.
        
        Returns:
            list: List of numeric column names
        """
        return self.numeric_columns

    def is_numeric_column(self, column_name):
        """
        Check if a column is numeric.
        
        Args:
            column_name (str): Column name to check
            
        Returns:
            bool: True if the column is numeric, False otherwise
        """
        return column_name in self.numeric_columns

    def get_column_data(self, column_name):
        """
        Get data for a specific column.
        
        Args:
            column_name (str): Column name
            
        Returns:
            pandas.Series: Column data
        """
        if self.df is None or column_name not in self.df.columns:
            return None
        return self.df[column_name]

    def set_temperature_unit(self, use_celsius):
        """
        Set temperature unit preference.
        
        Args:
            use_celsius (bool): True to use Celsius, False to use Fahrenheit
        """
        self.use_celsius = use_celsius

    def get_temperature_unit(self):
        """
        Get current temperature unit.
        
        Returns:
            bool: True if using Celsius, False if using Fahrenheit
        """
        return self.use_celsius

    def get_temperature_unit_name(self):
        """
        Get the name of the current temperature unit.
        
        Returns:
            str: Name of the current temperature unit
        """
        return "Celsius (°C)" if self.use_celsius else "Fahrenheit (°F)"

    def fahrenheit_to_celsius(self, f_value):
        """
        Convert Fahrenheit to Celsius.
        
        Args:
            f_value (float): Temperature in Fahrenheit
            
        Returns:
            float: Temperature in Celsius
        """
        return (f_value - 32) * 5/9

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

    def get_parameter_categories(self):
        """
        Get parameter categories.
        
        Returns:
            dict: Dictionary of parameter categories
        """
        return self.categories

    def get_category_full_names(self, category):
        """
        Get full names for parameters in a category.
        
        Args:
            category (str): Category name
            
        Returns:
            list: List of full parameter names
        """
        if category not in self.categories:
            return []
            
        abbr_params = self.categories[category]
        full_params = []
        
        for abbr in abbr_params:
            if abbr in self.abbr_to_full:
                full_params.append(self.abbr_to_full[abbr])
            else:
                full_params.append(abbr)  # Keep as is if not found
                
        return full_params

    def get_file_name(self):
        """
        Get the name of the loaded file.
        
        Returns:
            str: File name or empty string if no file loaded
        """
        if self.log_file_path:
            return os.path.basename(self.log_file_path)
        return ""
