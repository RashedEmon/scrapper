import os
import json

class Utils: 
    def load_json_data(file_path):
        """Load XPath expressions from a JSON file."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from file {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while loading the file {file_path}: {e}")
