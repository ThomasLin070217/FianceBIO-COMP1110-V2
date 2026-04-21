"""
Handles persistent data storage, including loading and saving JSON files 
with comprehensive error handling for missing or malformed data.
"""
import json
import os
import re

class FileIO:
    @staticmethod
    def _strip_json_comments(raw_text):
        """Allow case-study files that include // or /* */ comments."""
        no_block_comments = re.sub(r"/\*.*?\*/", "", raw_text, flags=re.DOTALL)
        return re.sub(r"^\s*//.*$", "", no_block_comments, flags=re.MULTILINE)

    @staticmethod
    def _normalize_category(record):
        """
        Normalize legacy/alternate category names to app categories.
        Example: Food -> Dining.
        """
        if not isinstance(record, dict):
            return record

        normalized = dict(record)
        category = normalized.get("category")
        if category == "Food":
            normalized["category"] = "Dining"
        return normalized

    @staticmethod
    def save_to_json(data, filename):
        """Save a list of objects (converted to dicts) to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([obj if isinstance(obj, dict) else obj.to_dict() for obj in data], 
                          f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    @staticmethod
    def load_from_json(filename, object_type):
        """Load data from JSON and return a list of objects or dicts."""
        if not os.path.exists(filename):
            return []  # Handle missing file gracefully 
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                clean_text = FileIO._strip_json_comments(raw_text)
                raw_data = json.loads(clean_text)

                if isinstance(raw_data, list):
                    return [FileIO._normalize_category(item) for item in raw_data]
                return raw_data
        except (json.JSONDecodeError, ValueError):
            print(f"Warning: {filename} is malformed or empty.")
            return []
