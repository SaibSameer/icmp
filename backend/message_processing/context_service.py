"""
Context service for message processing.

This module handles retrieving and preparing conversation context
for message processing.
"""

import logging
from typing import List, Dict, Any, Optional

log = logging.getLogger(__name__)

class ContextService:
    """Service for retrieving and managing conversation context."""
    
    @staticmethod
    def get_conversation_context(conn, business_id: str, user_id: str, 
                                 limit: int = 3) -> Dict[str, Any]:
        """
        Retrieve conversation history and context for the given business and user.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            limit: Maximum number of conversations to retrieve
            
        Returns:
            Dictionary with conversation context data
        """
        cursor = conn.cursor()
        context = {
            'conversation_history': [],
            'summary': "",
            'user_info': {},
            'business_info': {}
        }
        
        try:
            # Get recent conversations
            cursor.execute(
                """
                SELECT conversation_id 
                FROM conversations 
                WHERE business_id = %s AND user_id = %s 
                ORDER BY last_updated DESC 
                LIMIT %s
                """, 
                (business_id, user_id, limit)
            )
            conversation_ids = [row[0] for row in cursor.fetchall()]
            
            # Get messages from these conversations
            if conversation_ids:
                placeholders = ', '.join(['%s'] * len(conversation_ids))
                query = f"""
                    SELECT conversation_id, sender_type, message_content, timestamp
                    FROM messages 
                    WHERE conversation_id IN ({placeholders})
                    ORDER BY timestamp ASC
                """
                cursor.execute(query, conversation_ids)
                
                # Group messages by conversation
                conversations = {}
                for row in cursor.fetchall():
                    conv_id, sender, content, timestamp = row
                    
                    if conv_id not in conversations:
                        conversations[conv_id] = []
                        
                    conversations[conv_id].append({
                        'sender': sender,
                        'content': content,
                        'timestamp': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
                    })
                
                # Add to context
                context['conversation_history'] = [
                    {'conversation_id': conv_id, 'messages': messages}
                    for conv_id, messages in conversations.items()
                ]
                
                # Generate simple summary (could be enhanced with OpenAI)
                message_count = sum(len(msgs) for msgs in conversations.values())
                user_messages = sum(1 for c in conversations.values() 
                                   for m in c if m['sender'] == 'user')
                
                context['summary'] = f"User has sent {user_messages} messages across {len(conversations)} conversations"
            
            # Get basic user info if available
            cursor.execute(
                """
                SELECT first_name, last_name, email
                FROM users WHERE user_id = %s
                """, 
                (user_id,)
            )
            user_row = cursor.fetchone()
            if user_row:
                context['user_info'] = {
                    'first_name': user_row[0],
                    'last_name': user_row[1],
                    'email': user_row[2]
                }
            
            # Get basic business info
            cursor.execute(
                """
                SELECT business_name, business_description
                FROM businesses WHERE business_id = %s
                """, 
                (business_id,)
            )
            business_row = cursor.fetchone()
            if business_row:
                context['business_info'] = {
                    'name': business_row[0],
                    'description': business_row[1]
                }
                
            return context
            
        except Exception as e:
            log.error(f"Error getting conversation context: {str(e)}")
            return context
    
    @staticmethod
    def is_new_user(conn, business_id: str, user_id: str) -> bool:
        """
        Check if this is a new user with no previous conversations.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            
        Returns:
            True if this is a new user, False otherwise
        """
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM conversations 
                WHERE business_id = %s AND user_id = %s
                """, 
                (business_id, user_id)
            )
            count = cursor.fetchone()[0]
            return count == 0
            
        except Exception as e:
            log.error(f"Error checking if user is new: {str(e)}")
            return True  # Assume new user if error