import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def main():
    conn = None
    cursor = None
    try:
        print("Connecting to PostgreSQL database...")
        print(f"Using database: {DB_CONFIG['dbname']}")
        print(f"Using user: {DB_CONFIG['user']}")
        print(f"Using host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Create the llm_calls table
        print("\nCreating llm_calls table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                call_id UUID PRIMARY KEY,
                business_id UUID NOT NULL,
                input_text TEXT NOT NULL,
                response TEXT NOT NULL,
                system_prompt TEXT,
                call_type VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_llm_calls_business_id 
            ON llm_calls (business_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_llm_calls_timestamp 
            ON llm_calls (timestamp);
        """)
        
        conn.commit()
        print("Table and indexes created successfully!")
        
    except psycopg2.OperationalError as e:
        print("\nError: Could not connect to the database.")
        print("Please ensure:")
        print("1. PostgreSQL is running")
        print("2. The user 'icmp_user' exists in PostgreSQL")
        print("3. The password in .env file matches the user's password")
        print("\nTo create the user and set the password, run these commands in psql:")
        print("CREATE USER icmp_user WITH PASSWORD 'icmp_password';")
        print("ALTER USER icmp_user WITH SUPERUSER;")
        print("CREATE DATABASE icmp_db OWNER icmp_user;")
        print("\nDetailed error:", str(e))
    except Exception as e:
        print(f"\nError: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()