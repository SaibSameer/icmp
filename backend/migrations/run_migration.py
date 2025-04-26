import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from backend.db import get_db_connection, release_db_connection

def run_migration():
    """Run the conversations table migration."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Read the SQL file
        migration_file = current_dir / 'create_conversations_table.sql'
        with open(migration_file, 'r') as f:
            sql = f.read()

        # Execute the SQL
        cursor.execute(sql)
        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error running migration: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == '__main__':
    run_migration() 