import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def create_database():
    """Create the database and user if they don't exist."""
    try:
        # Connect to PostgreSQL with superuser privileges
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create user if not exists
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (os.environ.get('DB_USER'),))
        if not cur.fetchone():
            cur.execute(f"CREATE USER {os.environ.get('DB_USER')} WITH PASSWORD %s", (os.environ.get('DB_PASSWORD'),))
            print(f"Created user {os.environ.get('DB_USER')}")

        # Create database if not exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.environ.get('DB_NAME'),))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {os.environ.get('DB_NAME')} OWNER {os.environ.get('DB_USER')}")
            print(f"Created database {os.environ.get('DB_NAME')}")

        cur.close()
        conn.close()
        print("Database and user setup completed successfully")
        return True

    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

def setup_schema():
    """Set up the database schema."""
    try:
        from backend.db import setup_database
        setup_database()
        print("Schema setup completed successfully")
        return True
    except Exception as e:
        print(f"Error setting up schema: {str(e)}")
        return False

if __name__ == '__main__':
    if create_database():
        setup_schema()