import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

# Connect to the database
conn = psycopg2.connect(**db_config)
conn.autocommit = True
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'prompt_templates' AND column_name = 'template_type'
    """)
    
    if cursor.fetchone():
        print("Column 'template_type' already exists in prompt_templates table")
    else:
        # Add the column
        cursor.execute("""
            ALTER TABLE prompt_templates 
            ADD COLUMN template_type VARCHAR(50) DEFAULT 'stage_selection'
        """)
        print("Successfully added 'template_type' column to prompt_templates table")
        
    print("Migration completed successfully")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    cursor.close()
    conn.close()