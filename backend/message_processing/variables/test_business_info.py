#!/usr/bin/env python
import sys
import os
import logging
import unittest
import argparse
from unittest.mock import MagicMock, patch

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

from backend.message_processing.template_variables import TemplateVariableProvider
from backend.message_processing.variables.business_info import provide_business_info
from backend.db import get_db_connection, release_db_connection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class TestBusinessInfo(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.conn = MagicMock()
        self.business_id = "test-business-id"
        self.mock_business = {
            'business_id': 'test-business-id',
            'business_name': 'Test Business',
            'business_description': 'A test business',
            'address': '123 Test St',
            'phone_number': '555-1234',
            'website': 'https://test.example.com',
            'owner_id': 'test-owner-id',
            'first_stage_id': 'test-stage-id',
            'facebook_page_id': 'test-facebook-id',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00'
        }

    def test_business_info_full(self):
        """Test business_info with all fields."""
        cursor = MagicMock()
        cursor.fetchone.return_value = self.mock_business
        self.conn.cursor.return_value = cursor

        result = provide_business_info(self.conn, self.business_id, format='json')
        
        # Verify database query
        cursor.execute.assert_called_once()
        self.assertIn("SELECT", cursor.execute.call_args[0][0])
        self.assertIn("business_name", cursor.execute.call_args[0][0])
        self.assertIn("business_description", cursor.execute.call_args[0][0])
        self.assertIn("address", cursor.execute.call_args[0][0])
        self.assertIn("phone_number", cursor.execute.call_args[0][0])
        self.assertIn("website", cursor.execute.call_args[0][0])
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.mock_business['business_id'])
        self.assertEqual(result['name'], self.mock_business['business_name'])
        self.assertEqual(result['description'], self.mock_business['business_description'])
        self.assertEqual(result['address'], self.mock_business['address'])
        self.assertEqual(result['contact']['phone'], self.mock_business['phone_number'])
        self.assertEqual(result['contact']['website'], self.mock_business['website'])
        self.assertEqual(result['metadata']['owner_id'], self.mock_business['owner_id'])
        self.assertEqual(result['metadata']['first_stage_id'], self.mock_business['first_stage_id'])
        self.assertEqual(result['metadata']['facebook_page_id'], self.mock_business['facebook_page_id'])

    def test_business_info_no_address(self):
        """Test business_info with address excluded."""
        cursor = MagicMock()
        cursor.fetchone.return_value = self.mock_business
        self.conn.cursor.return_value = cursor

        result = provide_business_info(self.conn, self.business_id, include_address=False, format='json')
        
        # Verify address is not included
        self.assertNotIn('address', result)

    def test_business_info_no_contact(self):
        """Test business_info with contact info excluded."""
        cursor = MagicMock()
        cursor.fetchone.return_value = self.mock_business
        self.conn.cursor.return_value = cursor

        result = provide_business_info(self.conn, self.business_id, include_contact=False, format='json')
        
        # Verify contact info is not included
        self.assertNotIn('contact', result)

    def test_business_info_not_found(self):
        """Test business_info when business is not found."""
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        self.conn.cursor.return_value = cursor

        result = provide_business_info(self.conn, self.business_id, format='json')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Business not found")

    def test_business_info_no_connection(self):
        """Test business_info with no database connection."""
        result = provide_business_info(None, self.business_id, format='json')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], "No database connection")

    def test_business_info_partial_data(self):
        """Test business_info with partial data."""
        cursor = MagicMock()
        partial_business = {
            'business_id': 'test-business-id',
            'business_name': 'Test Business',
            'business_description': None,
            'address': None,
            'phone_number': None,
            'website': None,
            'owner_id': None,
            'first_stage_id': None,
            'facebook_page_id': None,
            'created_at': None,
            'updated_at': None
        }
        cursor.fetchone.return_value = partial_business
        self.conn.cursor.return_value = cursor

        result = provide_business_info(self.conn, self.business_id, format='json')
        
        # Verify only name is included
        self.assertEqual(result['name'], 'Test Business')
        self.assertIsNone(result['description'])
        self.assertIsNone(result.get('address'))
        self.assertIsNone(result.get('contact', {}).get('phone'))
        self.assertIsNone(result.get('contact', {}).get('website'))

def test_business_info_command():
    """Command-line function to test business_info variable."""
    parser = argparse.ArgumentParser(description="Test business_info template variable")
    parser.add_argument('--test-db', action='store_true', help='Run database test')
    parser.add_argument('--business_id', type=str, required=True, help='Business ID to test')
    parser.add_argument('--include_address', action='store_true', help='Include address in output')
    parser.add_argument('--include_contact', action='store_true', help='Include contact info in output')
    parser.add_argument('--format', type=str, default='text', choices=['text', 'json'], help='Output format')
    args = parser.parse_args()
    
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
            
        kwargs = {
            'format': args.format
        }
        if args.include_address:
            kwargs['include_address'] = True
        if args.include_contact:
            kwargs['include_contact'] = True
            
        result = provide_business_info(conn, args.business_id, **kwargs)
        
        if args.format == 'json':
            import json
            print("\nBusiness Information (JSON):")
            print(json.dumps(result, indent=2))
        else:
            print("\nBusiness Information:")
            print(result)
        
    except Exception as e:
        log.error(f"Error testing business_info: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    if '--test-db' in sys.argv:
        # Remove --test-db from sys.argv before parsing
        sys.argv.remove('--test-db')
        test_business_info_command()
    else:
        # Run unit tests
        unittest.main() 