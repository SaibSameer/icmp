"""
Test script for variable providers.
"""
import sys
import os
import json
import psycopg2
import argparse
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.message_processing.template_variables import TemplateVariableProvider
from backend.message_processing.variables import *  # This imports all variable providers

# Database connection configuration
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def test_variable(variable_name, business_id=None, user_id=None, conversation_id=None, message_content=None, api_key=None, owner_id=None):
    """Test a specific variable provider."""
    try:
        # Get the provider
        provider = TemplateVariableProvider.get_provider(variable_name)
        if not provider:
            print(f"Error: No provider found for variable '{variable_name}'")
            return

        # Get database connection
        conn = get_db_connection()
        if not conn:
            print("Error: Could not establish database connection")
            return

        try:
            # Prepare kwargs based on what's provided
            kwargs = {}
            if business_id:
                kwargs['business_id'] = business_id
            if user_id:
                kwargs['user_id'] = user_id
            if conversation_id:
                kwargs['conversation_id'] = conversation_id
            if message_content:
                kwargs['message_content'] = message_content
            if api_key:
                kwargs['api_key'] = api_key
            if owner_id:
                kwargs['owner_id'] = owner_id

            # Call the provider with the given kwargs
            try:
                result = provider(conn=conn, **kwargs)
                
                # Try to pretty print if result is JSON
                try:
                    parsed = json.loads(result)
                    print(json.dumps(parsed, indent=2))
                except:
                    print(result)
            except Exception as provider_error:
                print(f"Error in provider execution: {str(provider_error)}")
                import traceback
                traceback.print_exc()
        finally:
            conn.close()

    except Exception as e:
        print(f"Error testing variable: {str(e)}")
        import traceback
        traceback.print_exc()

def list_variables():
    """List all registered variables."""
    variables = TemplateVariableProvider.get_all_variable_names()
    print("\nRegistered Variables:")
    for var in sorted(variables):
        print(f"- {var}")

def main():
    parser = argparse.ArgumentParser(description='Test template variables')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # List command
    list_parser = subparsers.add_parser('list', help='List all available variables')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test a specific variable')
    test_parser.add_argument('variable_name', help='Name of the variable to test')
    test_parser.add_argument('--business-id', help='Business ID for testing')
    test_parser.add_argument('--user-id', help='User ID for testing')
    test_parser.add_argument('--conversation-id', help='Conversation ID for testing')
    test_parser.add_argument('--message-content', help='Message content for testing')
    test_parser.add_argument('--api-key', help='API key for testing')
    test_parser.add_argument('--owner-id', help='Owner ID for testing')

    args = parser.parse_args()

    if args.command == 'list':
        list_variables()
    elif args.command == 'test':
        test_variable(
            args.variable_name,
            business_id=args.business_id,
            user_id=args.user_id,
            conversation_id=args.conversation_id,
            message_content=args.message_content,
            api_key=args.api_key,
            owner_id=args.owner_id
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()