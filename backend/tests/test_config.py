# backend/tests/test_config.py
import unittest
import os
from config import Config  # Corrected import path
import pytest

class TestConfig(unittest.TestCase):
    def test_db_config(self):
        """Test that database configuration settings are loaded correctly."""
        self.assertEqual(Config.DB_NAME, os.environ.get("DB_NAME", "icmp_db"))
        self.assertEqual(Config.DB_USER, os.environ.get("DB_USER", "icmp_user"))
        # Add assertions for other DB config settings
    def test_openai_config(self):
        """Test that OpenAI configuration settings are loaded correctly."""
        self.assertEqual(Config.OPENAI_API_KEY, os.environ.get("OPENAI_API_KEY"))
        self.assertEqual(Config.ICMP_API_KEY, os.environ.get("ICMP_API_KEY", "YOUR_FALLBACK_ICMP_KEY"))
        # Add assertions for other OpenAI config settings

    def test_load_schemas(self):
        """Test that schemas are loaded successfully."""
        schemas_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas') # Adjust path
        schemas = Config.load_schemas(schemas_dir)
        self.assertIsInstance(schemas, dict)
        self.assertTrue(len(schemas) > 0)  # Assuming you have at least one schema
        self.assertIn('users', schemas)  # Assuming you have users schema