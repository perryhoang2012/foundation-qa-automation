import yaml
import os

def load_config(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Error decoding file {file_path}: {e}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error loading config file {file_path}: {e}")
