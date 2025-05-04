#!/usr/bin/env python
import sys
import os
import logging
import argparse
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.template_variables import TemplateVariableProvider

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_variable(variable_name, business_id, user_id, conversation_id, message_content=None, max_messages=10, include_timestamps=False):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        provider = TemplateVariableProvider.get_provider(variable_name)
        if not provider:
            log.error(f"No provider found for variable: {variable_name}")
            return
        # Build kwargs for provider
        kwargs = {}
        if 'max_messages' in provider.__code__.co_varnames:
            kwargs['max_messages'] = max_messages
        if 'include_timestamps' in provider.__code__.co_varnames:
            kwargs['include_timestamps'] = include_timestamps
        if 'message_content' in provider.__code__.co_varnames and message_content is not None:
            kwargs['message_content'] = message_content
        # Call provider
        value = provider(
            conn=conn,
            business_id=business_id if 'business_id' in provider.__code__.co_varnames else None,
            user_id=user_id if 'user_id' in provider.__code__.co_varnames else None,
            conversation_id=conversation_id if 'conversation_id' in provider.__code__.co_varnames else None,
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
    args = parser.parse_args()
    test_variable(
        variable_name=args.variable,
        business_id=args.business_id,
        user_id=args.user_id,
        conversation_id=args.conversation_id,
        message_content=args.message_content,
        max_messages=args.max_messages,
        include_timestamps=args.include_timestamps
    ) 