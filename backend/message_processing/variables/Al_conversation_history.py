from backend.message_processing.template_variables import TemplateVariableProvider
import logging

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider('all_conversation_history')
def provide_all_conversation_history(conn, **kwargs) -> str:
    """
    Generate a formatted history of all messages across all conversations.
    Args:
        conn: Database connection
        **kwargs: Additional arguments including:
            - max_messages: Maximum number of messages to retrieve (default: 100)
            - include_timestamps: Whether to include timestamps (default: False)
    Returns:
        Formatted string with all messages
    """
    try:
        if not conn:
            log.error("No database connection provided")
            return "Error: No database connection"
        max_messages = kwargs.get('max_messages', 100)
        include_timestamps = kwargs.get('include_timestamps', False)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_content, sender_type, created_at, conversation_id 
            FROM messages 
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (max_messages,)
        )
        messages = cursor.fetchall()
        if not messages:
            return "No messages found"
        history = []
        for msg in messages:
            sender_type = str(msg['sender_type']).lower()
            if sender_type in ['assistant', 'bot', 'system']:
                sender = "Assistant"
            else:
                sender = "User"
            timestamp = f"[{msg['created_at'].isoformat()}] " if include_timestamps and msg['created_at'] else ""
            conversation_id = f"[Conversation: {msg['conversation_id']}] "
            history.append(f"{conversation_id}{timestamp}{sender}: {msg['message_content']}")
        return "\n".join(history)
    except Exception as e:
        log.error(f"Error providing all_conversation_history: {str(e)}")
        return "Error retrieving conversation history" 