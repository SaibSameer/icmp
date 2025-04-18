from db import get_db_connection, release_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    conn = None
    try:
        logger.info("Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check the stages table structure
        logger.info("Checking stages table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'stages'
            ORDER BY ordinal_position;
        """)
        
        print("\n=== STAGES TABLE STRUCTURE ===")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Column: {row[0]}, Type: {row[1]}, Nullable: {row[2]}")
        
        # Check the default_templates table structure
        logger.info("Checking default_templates table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'default_templates'
            ORDER BY ordinal_position;
        """)
        
        print("\n=== DEFAULT_TEMPLATES TABLE STRUCTURE ===")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Column: {row[0]}, Type: {row[1]}, Nullable: {row[2]}")
        
        # Count the number of records in stages
        logger.info("Counting stages records...")
        cursor.execute("SELECT COUNT(*) FROM stages;")
        count = cursor.fetchone()[0]
        print(f"\nNumber of records in stages: {count}")
        
        # Count the number of records in default_templates
        logger.info("Counting default_templates records...")
        cursor.execute("SELECT COUNT(*) FROM default_templates;")
        count = cursor.fetchone()[0]
        print(f"Number of records in default_templates: {count}")
        
        # Try to diagnose the 500 error
        print("\n=== CHECKING FOR NULL TEMPLATE IDS IN STAGES ===")
        cursor.execute("""
            SELECT stage_id, 
                   stage_selection_template_id IS NULL AS selection_null, 
                   data_extraction_template_id IS NULL AS extraction_null, 
                   response_generation_template_id IS NULL AS response_null
            FROM stages 
            WHERE stage_selection_template_id IS NULL 
               OR data_extraction_template_id IS NULL 
               OR response_generation_template_id IS NULL;
        """)
        rows = cursor.fetchall()
        if rows:
            print("Found stages with NULL template IDs:")
            for row in rows:
                print(f"Stage ID: {row[0]}, Selection null: {row[1]}, Extraction null: {row[2]}, Response null: {row[3]}")
        else:
            print("No stages with NULL template IDs")
        
    except Exception as e:
        logger.error(f"Error checking database: {e}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    check_database()