# tests.py
import unittest
import json
import os
from jsonschema import ValidationError
from app import app, SCHEMAS  # Import Flask app and schemas
from db import get_db_connection # Import get_db_connection

class TestICMP(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_message_endpoint_validation(self):
        # Send an invalid POST request to /message (missing required field)
        invalid_payload = {
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "message": "Help"
        }
        with self.app as client:
            response = client.post('/message', json=invalid_payload, headers={'Authorization': 'Bearer cd0fd3314e8f1fe7cef737db4ac21778ccc7d5a97bbb33d9af17612e337231d6'})

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["error_code"], "INVALID_REQUEST")
        self.assertIn("is a required property", data["details"]) #changed to error code instead of error
        self.assertIn("business_id", data["details"]) #check if error is business id


if __name__ == '__main__':
    unittest.main()