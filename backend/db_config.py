import os
from urllib.parse import urlparse
import logging

log = logging.getLogger(__name__)

def get_db_config():
    """Get database configuration from environment variables."""
    
    # If DATABASE_URL is provided, parse it
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        try:
            # Parse the URL
            parsed = urlparse(database_url)
            
            # Ensure we're using the full hostname for Render
            hostname = parsed.hostname
            if not hostname.endswith('.render.com') and 'dpg-' in hostname:
                hostname = f"{hostname}.oregon-postgres.render.com"
            
            config = {
                "dbname": parsed.path[1:],  # Remove leading slash
                "user": parsed.username,
                "password": parsed.password,
                "host": hostname,
                "port": str(parsed.port or 5432),
                "sslmode": "require" if 'render.com' in hostname else "disable",  # Only require SSL for Render
                "client_encoding": "utf8"
            }
            log.info(f"Using database configuration from DATABASE_URL with host: {config['host']}")
            return config
        except Exception as e:
            log.error(f"Error parsing DATABASE_URL: {e}")
    
    # Otherwise use individual environment variables
    host = os.environ.get("DB_HOST", "localhost")
    # Ensure we're using the full hostname for Render
    if not host.endswith('.render.com') and 'dpg-' in host:
        host = f"{host}.oregon-postgres.render.com"
    
    config = {
        "dbname": os.environ.get("DB_NAME", "icmp_db"),
        "user": os.environ.get("DB_USER", "icmp_user"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": host,
        "port": os.environ.get("DB_PORT", "5432"),
        "sslmode": "require" if 'render.com' in host else "disable",  # Only require SSL for Render
        "client_encoding": "utf8"
    }
    
    log.info(f"Using database configuration from individual variables with host: {config['host']}")
    return config 