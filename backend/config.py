# backend/config.py
import os
import json
import logging
import openai
from dotenv import load_dotenv

log = logging.getLogger(__name__)

load_dotenv()

class Config:
    """Configuration class for the ICMP backend."""

    # Database Configuration
    DB_NAME = os.environ.get("DB_NAME", "icmp_db")
    DB_USER = os.environ.get("DB_USER", "icmp_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")

    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    ICMP_API_KEY = os.environ.get("ICMP_API_KEY", "YOUR_FALLBACK_ICMP_KEY")
    
    # Create OpenAI client or use mock
    if OPENAI_API_KEY:
        # Initialize the real OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        log.info("OpenAI client initialized with API key")
    else:
        # Use mock client for development
        log.warning("OPENAI_API_KEY not set - using mock client")
        client = None  # The call_openai function will handle this

    # Update path HERE:
    schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')

    # Other Configurations (Add as needed)

    @staticmethod
    def load_schemas(schemas_dir):
        """Loads JSON schemas from the specified directory."""
        schemas = {}
        for filename in os.listdir(schemas_dir):
            if filename.endswith('.json'):
                with open(os.path.join(schemas_dir, filename), 'r') as f:
                    schema_name = os.path.splitext(filename)[0]
                    schemas[schema_name] = json.load(f)
        return schemas

# Update the path to the schemas directory
schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
schemas = Config.load_schemas(schemas_dir)

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        logging.error(f"Failed to start app: {str(e)}")
        raise