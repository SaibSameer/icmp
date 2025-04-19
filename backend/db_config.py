import os
from urllib.parse import urlparse

def get_db_config():
    """Get database configuration from environment variables."""
    
    # If DATABASE_URL is provided, parse it
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Parse the URL
        parsed = urlparse(database_url)
        return {
            "dbname": parsed.path[1:],  # Remove leading slash
            "user": parsed.username,
            "password": parsed.password,
            "host": parsed.hostname,
            "port": str(parsed.port or 5432)
        }
    
    # Otherwise use individual environment variables
    return {
        "dbname": os.environ.get("DB_NAME", "icmp_db"),
        "user": os.environ.get("DB_USER", "icmp_user"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432")
    } 