import psycopg2
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Optional
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self):
        self.db_params = self._load_db_params()
        self.conn = None
        self.cursor = None

    def _load_db_params(self) -> Dict[str, str]:
        """Load database parameters from environment variables"""
        load_dotenv()
        
        params = {
            "dbname": os.getenv("DB_NAME", "icmp_db"),
            "user": os.getenv("DB_USER", "icmp_user"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432")
        }
        
        # Validate required parameters
        if not params["password"]:
            log.error("DB_PASSWORD environment variable not set")
            raise ValueError("DB_PASSWORD is required")
            
        return params

    def connect(self) -> None:
        """Establish database connection"""
        try:
            log.info("Connecting to database...")
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            log.info("Database connection established successfully")
        except Exception as e:
            log.error(f"Database connection failed: {str(e)}")
            raise

    def close(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        log.info("Database connection closed")

    def execute_sql_file(self, file_path: str) -> None:
        """Execute SQL commands from a file"""
        try:
            log.info(f"Reading SQL file: {file_path}")
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
            
            log.info("Executing SQL script...")
            self.cursor.execute(sql_script)
            log.info("SQL script executed successfully")
        except Exception as e:
            log.error(f"SQL execution failed: {str(e)}")
            raise

    def create_database(self) -> None:
        """Create the database if it doesn't exist"""
        # Connect to default database first
        default_params = self.db_params.copy()
        default_params['dbname'] = 'postgres'
        
        try:
            log.info("Connecting to default database...")
            conn = psycopg2.connect(**default_params)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_params['dbname'],))
            exists = cursor.fetchone()
            
            if not exists:
                log.info(f"Creating database: {self.db_params['dbname']}")
                cursor.execute(f"CREATE DATABASE {self.db_params['dbname']}")
                log.info("Database created successfully")
            else:
                log.info("Database already exists")
                
        except Exception as e:
            log.error(f"Database creation failed: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def setup_database(self) -> None:
        """Main method to set up the database"""
        try:
            # Create database if it doesn't exist
            self.create_database()
            
            # Connect to the new database
            self.connect()
            
            # Execute setup scripts
            scripts_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            for script in sorted(os.listdir(scripts_dir)):
                if script.endswith('.sql'):
                    script_path = os.path.join(scripts_dir, script)
                    self.execute_sql_file(script_path)
            
            log.info("Database setup completed successfully!")
            
        except Exception as e:
            log.error(f"Database setup failed: {str(e)}")
            raise
        finally:
            self.close()

def main():
    """Main entry point"""
    try:
        db_setup = DatabaseSetup()
        db_setup.setup_database()
    except Exception as e:
        log.error(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 