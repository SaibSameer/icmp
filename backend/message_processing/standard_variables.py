"""
Standard template variable providers.

This module implements providers for common template variables used in the system.
These providers are automatically registered with the TemplateVariableProvider.
"""

import logging
from typing import List, Dict, Any
import json

from .template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

# ---------- Stage Variables ----------

@TemplateVariableProvider.register_provider('stage_list')
def provide_stage_list(conn, business_id: str, **kwargs) -> str:
    """
    Generate a formatted list of stage names for the business.
    
    Args:
        conn: Database connection
        business_id: UUID of the business
        
    Returns:
        Formatted string representation of stage list
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT stage_name 
            FROM stages 
            WHERE business_id = %s
            ORDER BY stage_name
            """,
            (business_id,)
        )
        
        stages = cursor.fetchall()
        stage_list = [stage['stage_name'] for stage in stages] if stages else []
        
        # Return as a Python list string representation
        return str(stage_list)
        
    except Exception as e:
        log.error(f"Error providing stage_list: {str(e)}")
        return "[]"

@TemplateVariableProvider.register_provider('available_stages')
def provide_available_stages(conn, business_id: str, **kwargs) -> str:
    """
    Generate detailed information about available stages.
    
    Args:
        conn: Database connection
        business_id: UUID of the business
        
    Returns:
        Formatted string with stage details
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT stage_id, stage_name, stage_description, stage_type
            FROM stages 
            WHERE business_id = %s
            ORDER BY stage_name
            """,
            (business_id,)
        )
        
        stages = cursor.fetchall()
        if not stages:
            return "No stages available"
            
        stage_info = []
        for stage in stages:
            stage_info.append(f"{stage['stage_name']}: {stage['stage_description']}")
            
        return "\n".join(stage_info)
        
    except Exception as e:
        log.error(f"Error providing available_stages: {str(e)}")
        return "Error retrieving stages"

# ---------- Conversation Variables ----------

@TemplateVariableProvider.register_provider('conversation_history')
def provide_conversation_history(conn, conversation_id: str, **kwargs) -> str:
    """
    Generate a formatted conversation history.
    
    Args:
        conn: Database connection
        conversation_id: UUID of the conversation
        **kwargs: Additional arguments including:
            - max_messages: Maximum number of messages to retrieve (default: 50)
            - include_timestamps: Whether to include timestamps (default: True)
        
    Returns:
        Formatted string with conversation messages
    """
    try:
        if not conn:
            log.error("No database connection provided")
            return "Error: No database connection"
            
        max_messages = kwargs.get('max_messages', 50)
        include_timestamps = kwargs.get('include_timestamps', True)
        
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_content, sender_type, created_at 
            FROM messages 
            WHERE conversation_id = %s 
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (conversation_id, max_messages)
        )
        
        messages = cursor.fetchall()
        if not messages:
            return "No conversation history"
            
        # Reverse to get chronological order
        messages.reverse()
        
        history = []
        for msg in messages:
            sender = "User" if msg['sender_type'] == 'user' else "Assistant"
            timestamp = f"[{msg['created_at'].strftime('%Y-%m-%d %H:%M:%S')}] " if include_timestamps and msg['created_at'] else ""
            history.append(f"{timestamp}{sender}: {msg['message_content']}")
            
        return "\n".join(history)
        
    except Exception as e:
        log.error(f"Error providing conversation_history: {str(e)}", exc_info=True)
        return "Error retrieving conversation history"

@TemplateVariableProvider.register_provider('summary_of_last_conversations')
def provide_conversation_summary(conn, conversation_id: str, **kwargs) -> str:
    """
    Generate a summary of recent messages.
    
    Args:
        conn: Database connection
        conversation_id: UUID of the conversation
        
    Returns:
        Summary of recent messages
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_content, sender_type, created_at 
            FROM messages 
            WHERE conversation_id = %s 
            ORDER BY created_at DESC
            LIMIT 3
            """,
            (conversation_id,)
        )
        
        messages = cursor.fetchall()
        if not messages:
            return "No previous conversations"
            
        # Simple summary approach
        summary_parts = []
        for msg in messages:
            sender = "User" if msg['sender_type'] == 'user' else "Assistant"
            content = msg['message_content']
            # Truncate long messages
            if len(content) > 30:
                content = content[:30] + "..."
            summary_parts.append(f"{sender}: {content}")
        
        # Reverse to get chronological order
        summary_parts.reverse()
        return " | ".join(summary_parts)
        
    except Exception as e:
        log.error(f"Error providing conversation_summary: {str(e)}")
        return "Error retrieving conversation summary"

@TemplateVariableProvider.register_provider('N')
def provide_message_count(conn, conversation_id: str, **kwargs) -> str:
    """
    Generate the number of messages in the conversation.
    
    Args:
        conn: Database connection
        conversation_id: UUID of the conversation
        
    Returns:
        Number of messages as a string
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM messages 
            WHERE conversation_id = %s
            """,
            (conversation_id,)
        )
        
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        # Ensure it's at least 1
        return str(max(1, min(count, 10)))
        
    except Exception as e:
        log.error(f"Error providing message_count: {str(e)}")
        return "3"  # Default to 3 if error

# ---------- User Variables ----------

@TemplateVariableProvider.register_provider('user_name')
def provide_user_name(conn, user_id: str, **kwargs) -> str:
    """
    Generate the user's full name.
    
    Args:
        conn: Database connection
        user_id: UUID of the user
        
    Returns:
        User's full name
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT first_name, last_name
            FROM users 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        if not user:
            return "Guest"
            
        return f"{user['first_name']} {user['last_name']}".strip()
        
    except Exception as e:
        log.error(f"Error providing user_name: {str(e)}")
        return "Guest"

# ---------- Business Variables ----------

@TemplateVariableProvider.register_provider('business_name')
def provide_business_name(conn, business_id: str, **kwargs) -> str:
    """
    Generate the business name.
    
    Args:
        conn: Database connection
        business_id: UUID of the business
        
    Returns:
        Business name
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT business_name
            FROM businesses 
            WHERE business_id = %s
            """,
            (business_id,)
        )
        
        business = cursor.fetchone()
        if not business:
            return "Our Business"
            
        return business['business_name']
        
    except Exception as e:
        log.error(f"Error providing business_name: {str(e)}")
        return "Our Business"

# ---------- Utility Functions ----------

@TemplateVariableProvider.register_provider('current_time')
def provide_current_time(**kwargs) -> str:
    """
    Generate the current time.
    
    Returns:
        Current time string
    """
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

@TemplateVariableProvider.register_provider('current_date')
def provide_current_date(**kwargs) -> str:
    """
    Generate the current date.
    
    Returns:
        Current date string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

@TemplateVariableProvider.register_provider('user_message')
def provide_user_message(conn, message_content: str, **kwargs) -> str:
    """
    Provide the current user message.
    
    Args:
        conn: Database connection
        message_content: The content of the current message
        
    Returns:
        The user message content
    """
    return message_content