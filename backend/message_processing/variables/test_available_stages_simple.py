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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_available_stages(business_id):
    conn = None
    try:
        log.info(f"Testing with business_id: {business_id}")
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        
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