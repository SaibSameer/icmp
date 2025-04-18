# schemas_loader.py
import os  # Add this import
import json
import logging
from pythonjsonlogger import jsonlogger

log = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
log.addHandler(log_handler)

def load_schemas(schemas_dir):
    """Loads JSON schemas from the specified directory using schema titles as keys."""
    schemas = {}
    for filename in os.listdir(schemas_dir):
        if filename.endswith(".json"):
            schema_name = filename[:-5]  # Fallback to filename without .json
            filepath = os.path.join(schemas_dir, filename)
            try:
                with open(filepath, "r") as f:
                    schema = json.load(f)
                # Use schema title if present, otherwise fallback to filename
                schema_key = schema.get("title", schema_name).lower().replace(" ", "_")
                schemas[schema_key] = schema
                log.info({"message": f"Schema loaded: {schema_key}"})
            except (FileNotFoundError, json.JSONDecodeError) as e:
                log.error({"message": f"Failed to load schema {filename}", "error": str(e)})
                continue  # Skip this schema and move to the next
    return schemas