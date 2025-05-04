import psycopg2
import os
from dotenv import load_dotenv

def setup_database():
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    db_params = {
        "dbname": os.getenv("DB_NAME", "icmp_db"),
        "user": os.getenv("DB_USER", "icmp_user"),
        "password": os.getenv("DB_PASSWORD", "your_password"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432")
    }
    
    # Add check for password as it's often not defaulted
    if not db_params["password"] and not os.getenv("PGPASSWORD"): 
        print("ERROR: DB_PASSWORD environment variable not set and no default provided in script.")
        print("Please set DB_PASSWORD in your .env file.")
        return # Exit if password is truly missing

    try:
        # Connect to the database
        print("Connecting to the database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute the SQL script
        print("Reading SQL script...")
        with open('database_setup.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            
        print("Executing SQL script...")
        cursor.execute(sql_script)
        
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()