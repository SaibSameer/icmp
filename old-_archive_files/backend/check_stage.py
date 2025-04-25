from db import get_db_connection, release_db_connection
import uuid
import logging
import json
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_stage(stage_id=None):
    """Check a specific stage or list all stages"""
    conn = None
    try:
        logger.info("Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if stage_id:
            # Check a specific stage
            logger.info(f"Checking stage with ID: {stage_id}")
            cursor.execute("""
                SELECT * FROM stages WHERE stage_id = %s;
            """, (stage_id,))
            
            row = cursor.fetchone()
            if not row:
                print(f"No stage found with ID: {stage_id}")
                return
            
            # Get column names
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'stages' ORDER BY ordinal_position;
            """)
            columns = [col[0] for col in cursor.fetchall()]
            
            print("\n=== STAGE DETAILS ===")
            stage_data = {}
            for i, col in enumerate(columns):
                if isinstance(row[i], uuid.UUID):
                    stage_data[col] = str(row[i])
                elif hasattr(row[i], 'isoformat'):
                    stage_data[col] = row[i].isoformat()
                else:
                    stage_data[col] = row[i]
                print(f"{col}: {stage_data[col]}")
            
            # Pretty print for inspection
            print("\nJSON representation:")
            print(json.dumps(stage_data, indent=2))
            
        else:
            # List all stages with relevant info
            logger.info("Listing all stages...")
            cursor.execute("""
                SELECT stage_id, business_id, stage_name, stage_type, created_at
                FROM stages ORDER BY created_at DESC;
            """)
            
            rows = cursor.fetchall()
            print("\n=== ALL STAGES ===")
            for row in rows:
                print(f"ID: {row[0]}, Business: {row[1]}, Name: {row[2]}, Type: {row[3]}, Created: {row[4]}")
    
    except Exception as e:
        logger.error(f"Error checking stage: {e}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    # Use command line arg if provided, otherwise list all stages
    if len(sys.argv) > 1:
        check_stage(sys.argv[1])
    else:
        check_stage()