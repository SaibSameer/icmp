from backend.message_processing.template_variables import TemplateVariableProvider
import logging

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'user_messages',
    description='Generates a formatted history of all messages sent by a specific user',
    auth_requirement='business_key'
)
def provide_user_messages(conn, user_id: str, business_id: str, **kwargs) -> str:
    """
    Generate a formatted history of all messages sent by a specific user.
    Args:
        conn: Database connection
        user_id: ID of the user
        business_id: ID of the business
        **kwargs: Additional arguments including:
            - max_messages: Maximum number of messages to retrieve (default: 50)
            - include_timestamps: Whether to include timestamps (default: False)
            - include_conversation_id: Whether to include conversation ID (default: False)
    Returns:
        Formatted string with user messages
    """
    try:
        if not conn:
            log.error("No database connection provided")
            return "Error: No database connection"
            
        max_messages = kwargs.get('max_messages', 50)
        include_timestamps = kwargs.get('include_timestamps', False)
        include_conversation_id = kwargs.get('include_conversation_id', False)
        
        cursor = conn.cursor()
        # First, let's check if the user and business exist
        cursor.execute(
            """
            SELECT COUNT(*) FROM users WHERE user_id = %s;
            """,
            (user_id,)
        )
        user_exists = cursor.fetchone()['count'] > 0
        
        cursor.execute(
            """
            SELECT COUNT(*) FROM businesses WHERE business_id = %s;
            """,
            (business_id,)
        )
        business_exists = cursor.fetchone()['count'] > 0
        
        if not user_exists or not business_exists:
            return f"Error: {'User' if not user_exists else 'Business'} not found"
        
        # Now get the messages (fix join to prevent repetition)
        cursor.execute(
            """
            SELECT 
                m.message_content,
                m.created_at,
                c.conversation_id,
                m.message_id,
                m.sender_type
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.conversation_id
            WHERE m.user_id = %s 
            AND c.business_id = %s
            AND m.message_content IS NOT NULL
            ORDER BY m.created_at DESC
            LIMIT %s
            """,
            (user_id, business_id, max_messages)
        )
        messages = cursor.fetchall()
        
        if not messages:
            return "No messages found for this user"
            
        log.debug(f"Found {len(messages)} messages for user {user_id}")
        for msg in messages:
            log.debug(f"Message: {msg}")
            
        history = []
        for msg in messages:
            timestamp = f"[{msg['created_at'].isoformat()}] " if include_timestamps and msg['created_at'] else ""
            conversation_id = f"(Conversation: {msg['conversation_id']}) " if include_conversation_id else ""
            sender = f"{msg['sender_type']}: " if msg['sender_type'] else "User: "
            content = msg['message_content'] or "No content"
            history.append(f"{timestamp}{conversation_id}{sender}{content}")
            
        return "\n".join(history)
    except Exception as e:
        log.error(f"Error providing user_messages: {str(e)}", exc_info=True)
        return "Error retrieving user messages" 