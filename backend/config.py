# backend/config.py
import os
import json
import logging
import openai
from dotenv import load_dotenv

log = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'dbname': os.environ.get("DB_NAME", "icmp_db"),
        'user': os.environ.get("DB_USER", "icmp_user"),
        'password': os.environ.get("DB_PASSWORD"),
        'host': os.environ.get("DB_HOST", "localhost"),
        'port': os.environ.get("DB_PORT", "5432")
    }

class Config:
    """Configuration class for the ICMP backend."""

    # Database Configuration
    DB_NAME = os.environ.get("DB_NAME", "icmp_db")
    DB_USER = os.environ.get("DB_USER", "icmp_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")

    # Redis Configuration
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
    REDIS_SSL = os.environ.get("REDIS_SSL", "false").lower() == "true"

    # API Configuration
    ICMP_API_KEY = os.environ.get("ICMP_API_KEY")
    if not ICMP_API_KEY:
        log.error("ICMP_API_KEY is not set in environment variables")
        raise ValueError("ICMP_API_KEY environment variable is required")

    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set - some features may be limited")
    
    # Create OpenAI client or use mock
    if OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            log.info("OpenAI client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize OpenAI client: {str(e)}")
            client = None
    else:
        client = None
        log.warning("Using mock OpenAI client due to missing API key")

    # Update path HERE:
    schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')

    @staticmethod
    def load_schemas(schemas_dir):
        """Loads JSON schemas from the specified directory."""
        schemas = {}
        try:
            for filename in os.listdir(schemas_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(schemas_dir, filename), 'r') as f:
                        schema_name = os.path.splitext(filename)[0]
                        schemas[schema_name] = json.load(f)
            return schemas
        except Exception as e:
            log.error(f"Error loading schemas: {str(e)}")
            return {}

# Update the path to the schemas directory
schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
schemas = Config.load_schemas(schemas_dir)

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        logging.error(f"Failed to start app: {str(e)}")
        raise