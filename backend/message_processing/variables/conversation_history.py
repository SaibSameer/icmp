from backend.message_processing.template_variables import TemplateVariableProvider
import logging

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'conversation_history',
    description='Provides the history of messages in a conversation',
    auth_requirement='business_key'
)
def provide_conversation_history(conn, conversation_id: str, **kwargs) -> str:
    """
    Generate a formatted conversation history.
    Args:
        conn: Database connection
        conversation_id: UUID of the conversation
        **kwargs: Additional arguments including:
            - max_messages: Maximum number of messages to retrieve (default: 10)
            - include_timestamps: Whether to include timestamps (default: False)
    Returns:
        Formatted string with conversation messages
    """
    try:
        if not conn:
            log.error("No database connection provided")
            return "Error: No database connection"
        max_messages = kwargs.get('max_messages', 10)
        include_timestamps = kwargs.get('include_timestamps', False)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_content, sender_type, created_at 
            FROM messages 
            WHERE conversation_id = %s 
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (conversation_id, max_messages)
        )
        messages = cursor.fetchall()
        if not messages:
            return "No conversation history"
        history = []
        for msg in messages:
            sender_type = str(msg['sender_type']).lower()
            if sender_type in ['assistant', 'bot', 'system']:
                sender = "Assistant"
            else:
                sender = "User"
            timestamp = f"[{msg['created_at'].isoformat()}] " if include_timestamps and msg['created_at'] else ""
            history.append(f"{timestamp}{sender}: {msg['message_content']}")
        return "\n".join(history)
    except Exception as e:
        log.error(f"Error providing conversation_history: {str(e)}")
        return "Error retrieving conversation history" 