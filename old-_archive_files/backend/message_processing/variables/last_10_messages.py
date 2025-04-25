"""
Last 10 messages variable provider.
"""
import logging
import json
import re
from ..template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider('last_10_messages')
def provide_last_10_messages(conn, conversation_id: str, **kwargs) -> str:
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_content, sender_type, created_at 
            FROM messages 
            WHERE conversation_id = %s 
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (conversation_id,)
        )
        
        messages = cursor.fetchall()
        if not messages:
            return "[]"
            
        # Format messages
        message_list = []
        for msg in messages:
            content = msg['message_content']
            
            # Clean up assistant messages that contain recursive context
            if msg['sender_type'] == 'assistant':
                # The message content follows the format:
                # "user message:<user-message>\n,\nconversation sumary:[Missing: conversation_summary]\n,\nlast mesages [...]"
                # Extract just the user message part
                content_match = re.search(r'^user message:(.*?)(?:\n,\nconversation sumary:|$)', content, re.DOTALL)
                if content_match:
                    content = content_match.group(1).strip()
                else:
                    # Fallback pattern - try to clean up any assistant message
                    # that might have a different format
                    content = re.sub(r'user message:|\n,\nconversation sumary:.*|\n,\nlast mesages \[.*', '', content, flags=re.DOTALL)
                    content = content.strip()
            
            message_list.append({
                'content': content,
                'sender': 'user' if msg['sender_type'] == 'user' else 'assistant',
                'timestamp': msg['created_at'].isoformat()
            })
        
        # Reverse to get chronological order
        message_list.reverse()
        
        # Return as JSON string
        return json.dumps(message_list, indent=2)
        
    except Exception as e:
        log.error(f"Error providing last_10_messages: {str(e)}")
        return "[]"