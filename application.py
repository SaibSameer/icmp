from backend.app import app as application
import os

# Set environment variables if they're not already set
if 'DATABASE_URL' in os.environ and 'DB_HOST' not in os.environ:
    # Parse DATABASE_URL into individual components
    db_url = os.environ['DATABASE_URL']
    # Format: postgresql://username:password@host:port/dbname
    parts = db_url.replace('postgresql://', '').split('@')
    credentials = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    os.environ['DB_USER'] = credentials[0]
    os.environ['DB_PASSWORD'] = credentials[1]
    os.environ['DB_HOST'] = host_port[0]
    os.environ['DB_PORT'] = host_port[1] if len(host_port) > 1 else '5432'
    os.environ['DB_NAME'] = host_port_db[1]

if __name__ == '__main__':
    application.run()