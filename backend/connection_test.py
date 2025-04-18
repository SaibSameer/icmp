# connection_test.py

import os
from db import get_db_connection, release_db_connection
from dotenv import load_dotenv # Import load_dotenv

load_dotenv()  # Load environment variables from .env file

conn = None
try:
    conn = get_db_connection()
    cursor = conn.cursor()  # Get a cursor from the connection
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print(f"Query Result: {result}")
except Exception as e:
    print(f"Test Failed: {e}")
finally:
    if conn:
        release_db_connection(conn)