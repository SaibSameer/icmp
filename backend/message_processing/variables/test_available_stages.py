#!/usr/bin/env python
import os
import sys
import argparse
import logging

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

# Import after adding to path
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.variables.available_stages import provide_available_stages

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def check_database_state(conn, business_id):
    """Check the state of relevant tables in the database"""
    cursor = conn.cursor()
    
    # Check businesses table
    cursor.execute("SELECT * FROM businesses WHERE business_id = %s", (business_id,))
    business = cursor.fetchone()
    log.info(f"Business found: {business is not None}")
    
    # Check stages table
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM stages 
        WHERE business_id = %s
    """, (business_id,))
    stages_count = cursor.fetchone()['count']
    log.info(f"Stages found: {stages_count}")
    
    # Show some sample stages if they exist
    if stages_count > 0:
        cursor.execute("""
            SELECT stage_name, stage_description 
            FROM stages 
            WHERE business_id = %s
            LIMIT 5
        """, (business_id,))
        sample_stages = cursor.fetchall()
        log.info("Sample stages:")
        for stage in sample_stages:
            log.info(f"Stage: {stage}")

def test_available_stages(business_id):
    conn = None
    try:
        log.info(f"Testing with business_id: {business_id}")
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        
        # Check database state first
        check_database_state(conn, business_id)
        
        value = provide_available_stages(
            conn=conn,
            business_id=business_id
        )
        print(f"\nAvailable Stages:")
        print("------------")
        print(value)
    except Exception as e:
        log.error(f"Error testing available_stages: {str(e)}", exc_info=True)
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the available_stages variable provider.")
    parser.add_argument('--business_id', type=str, help='Business ID')
    args = parser.parse_args()

    business_id = args.business_id or input('Enter Business ID: ')

    test_available_stages(
        business_id=business_id
    ) 