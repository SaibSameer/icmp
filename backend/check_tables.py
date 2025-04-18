from db import get_db_connection, release_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables():
    conn = None
    try:
        logger.info("Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # List all tables in the database
        logger.info("Listing all tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        print("\n=== ALL TABLES IN DATABASE ===")
        tables = cursor.fetchall()
        for table in tables:
            print(f"Table: {table[0]}")
        
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    check_tables()