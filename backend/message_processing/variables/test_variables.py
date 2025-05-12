#!/usr/bin/env python
import sys
import os
import logging
import argparse
from dotenv import load_dotenv

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
backend_env_path = os.path.join(project_root, 'backend', '.env')
if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path)
    print(f"Loaded environment from {backend_env_path}")

from backend.db import get_db_connection, release_db_connection
from backend.message_processing.template_variables import TemplateVariableProvider

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_variable(variable_name, business_id, user_id, conversation_id, message_content=None, max_messages=10, include_timestamps=False, agent_id=None):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        provider_info = TemplateVariableProvider.get_provider(variable_name)
        if not provider_info:
            log.error(f"No provider found for variable: {variable_name}")
            return
            
        provider_func = provider_info['provider']
        
        # Build kwargs for provider
        kwargs = {}
        if 'max_messages' in provider_func.__code__.co_varnames:
            kwargs['max_messages'] = max_messages
        if 'include_timestamps' in provider_func.__code__.co_varnames:
            kwargs['include_timestamps'] = include_timestamps
        if 'message_content' in provider_func.__code__.co_varnames and message_content is not None:
            kwargs['message_content'] = message_content
        if 'agent_id' in provider_func.__code__.co_varnames and agent_id is not None:
            kwargs['agent_id'] = agent_id
            
        # Call provider
        value = provider_func(
            conn=conn,
            business_id=business_id if 'business_id' in provider_func.__code__.co_varnames else None,
            user_id=user_id if 'user_id' in provider_func.__code__.co_varnames else None,
            conversation_id=conversation_id if 'conversation_id' in provider_func.__code__.co_varnames else None,
            **kwargs
        )
        print(f"Value for variable '{variable_name}':\n{value}")
    except Exception as e:
        log.error(f"Error testing variable: {str(e)}", exc_info=True)
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a template variable provider.")
    parser.add_argument('--variable', type=str, required=True, help='Variable name to test (e.g. conversation_history)')
    parser.add_argument('--business_id', type=str, required=True, help='Business ID')
    parser.add_argument('--user_id', type=str, required=True, help='User ID')
    parser.add_argument('--conversation_id', type=str, required=True, help='Conversation ID')
    parser.add_argument('--message_content', type=str, help='Message content (optional)')
    parser.add_argument('--max_messages', type=int, default=10, help='Max messages (optional)')
    parser.add_argument('--include_timestamps', action='store_true', help='Include timestamps (optional)')
    parser.add_argument('--agent_id', type=str, help='Agent ID (optional)')
    args = parser.parse_args()
    test_variable(
        variable_name=args.variable,
        business_id=args.business_id,
        user_id=args.user_id,
        conversation_id=args.conversation_id,
        message_content=args.message_content,
        max_messages=args.max_messages,
        include_timestamps=args.include_timestamps,
        agent_id=args.agent_id
    ) 