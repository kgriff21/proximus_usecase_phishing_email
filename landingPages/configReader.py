import json
import os

class JsonReader:
    def __init__(self, filename):
        self.filename = filename  # provide file name when you instatnte object

    def get_value_from_config(self, key):
        
        # Load the JSON file
        config_file = self.filename
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                config = json.load(file)
                API_KEY = config.get(key)
                return API_KEY
        else:
            print(f"Configuration file '{config_file}' not found.")
            return None

    def get_explanation_from_email(self, key):
        
        # Load the JSON file
        email_file = self.filename
        try:
            with open(email_file, "r") as file:
                details = json.load(file)
                for employee in details:
                    if key == employee["FirstName"]: #TODO: Now using firstaname, change it to anu employeeID
                        explanataion = employee["explanation"]
                        return explanataion
        except Exception as e:
            print(f"Error in reading Configuration file '{email_file}' as {e}")
            return None
        