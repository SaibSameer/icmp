"""
Service for controlling AI response generation.

This module handles the logic for stopping and resuming AI responses
for specific conversations and users.
"""

import logging
from typing import Dict, Optional, Set
from datetime import datetime, timedelta
import uuid
from backend.db import get_db_connection, release_db_connection
from datetime import timezone

log = logging.getLogger(__name__)

class AIControlService:
    """
    Service for controlling AI response generation.
    
    This service manages the state of AI response generation for conversations
    and users, allowing for fine-grained control over when AI responses are
    generated.
    """
    
    def __init__(self):
        """Initialize the AI control service."""
        self._stopped_conversations: Set[str] = set()
        self._rate_limits: Dict[str, int] = {}
        # Default stop duration (24 hours)
        self._default_stop_duration = timedelta(hours=24)
    
    def _get_current_time(self):
        """Get current time in UTC timezone."""
        return datetime.now(timezone.utc)
    
    def stop_ai_responses(self, conversation_id: str) -> None:
        """
        Stop AI responses for a conversation.
        
        Args:
            conversation_id: ID of the conversation to stop
        """
        self._stopped_conversations.add(conversation_id)
        log.info(f"AI responses stopped for conversation {conversation_id}")
    
    def resume_ai_responses(self, conversation_id: str) -> None:
        """
        Resume AI responses for a conversation.
        
        Args:
            conversation_id: ID of the conversation to resume
        """
        self._stopped_conversations.discard(conversation_id)
        log.info(f"AI responses resumed for conversation {conversation_id}")
    
    def is_ai_stopped(self, conversation_id: str) -> bool:
        """
        Check if AI responses are stopped for a conversation.
        
        Args:
            conversation_id: ID of the conversation to check
            
        Returns:
            True if AI responses are stopped, False otherwise
        """
        return conversation_id in self._stopped_conversations
    
    def set_rate_limit(self, business_id: str, limit: int) -> None:
        """
        Set rate limit for a business.
        
        Args:
            business_id: ID of the business
            limit: Maximum number of requests per minute
        """
        self._rate_limits[business_id] = limit
        log.info(f"Rate limit set to {limit} for business {business_id}")
    
    def get_rate_limit(self, business_id: str) -> int:
        """
        Get rate limit for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Rate limit value
        """
        return self._rate_limits.get(business_id, 60)  # Default to 60 requests per minute
    
    def stop_ai_responses_for_user(self, user_id: Optional[str] = None, 
                                  duration: Optional[timedelta] = None) -> None:
        """
        Stop AI from generating responses for a user.
        
        Args:
            user_id: Optional user ID to stop responses for all their conversations (can be string or UUID)
            duration: Optional duration for the stop (defaults to 24 hours)
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Calculate expiration time
            stop_time = self._get_current_time()
            expiration_time = stop_time + (duration or self._default_stop_duration)
            
            if user_id:
                # Convert to string if it's a UUID object
                user_id_str = str(user_id) if hasattr(user_id, 'hex') else user_id
                # Check if user setting exists
                cursor.execute(
                    """
                    SELECT id FROM ai_control_settings 
                    WHERE user_id = %s
                    """,
                    (user_id_str,)
                )
                if cursor.fetchone():
                    # Update existing setting
                    cursor.execute(
                        """
                        UPDATE ai_control_settings 
                        SET is_stopped = true,
                            stop_time = %s,
                            expiration_time = %s,
                            updated_at = NOW()
                        WHERE user_id = %s
                        """,
                        (stop_time, expiration_time, user_id_str)
                    )
                else:
                    # Create new setting
                    cursor.execute(
                        """
                        INSERT INTO ai_control_settings (
                            user_id, is_stopped, stop_time, expiration_time
                        )
                        VALUES (%s, true, %s, %s)
                        """,
                        (user_id_str, stop_time, expiration_time)
                    )
                log.info(f"AI responses stopped for user {user_id_str}")
            else:
                # Convert to string if it's a UUID object
                conv_id_str = str(conversation_id) if hasattr(conversation_id, 'hex') else conversation_id
                # Check if conversation setting exists
                cursor.execute(
                    """
                    SELECT id FROM ai_control_settings 
                    WHERE conversation_id = %s
                    """,
                    (conv_id_str,)
                )
                if cursor.fetchone():
                    # Update existing setting
                    cursor.execute(
                        """
                        UPDATE ai_control_settings 
                        SET is_stopped = true,
                            stop_time = %s,
                            expiration_time = %s,
                            updated_at = NOW()
                        WHERE conversation_id = %s
                        """,
                        (stop_time, expiration_time, conv_id_str)
                    )
                else:
                    # Create new setting
                    cursor.execute(
                        """
                        INSERT INTO ai_control_settings (
                            conversation_id, is_stopped, stop_time, expiration_time
                        )
                        VALUES (%s, true, %s, %s)
                        """,
                        (conv_id_str, stop_time, expiration_time)
                    )
                log.info(f"AI responses stopped for conversation {conv_id_str}")
            
            conn.commit()
            
        except Exception as e:
            log.error(f"Error stopping AI responses: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                release_db_connection(conn)
    
    def resume_ai_responses_for_user(self, user_id: Optional[str] = None) -> None:
        """
        Resume AI response generation for a user.
        
        Args:
            user_id: Optional user ID to resume responses for all their conversations (can be string or UUID)
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if user_id:
                # Convert to string if it's a UUID object
                user_id_str = str(user_id) if hasattr(user_id, 'hex') else user_id
                cursor.execute(
                    """
                    UPDATE ai_control_settings 
                    SET is_stopped = false,
                        stop_time = NULL,
                        expiration_time = NULL,
                        updated_at = NOW()
                    WHERE user_id = %s
                    """,
                    (user_id_str,)
                )
                log.info(f"AI responses resumed for user {user_id_str}")
            else:
                # Convert to string if it's a UUID object
                conv_id_str = str(conversation_id) if hasattr(conversation_id, 'hex') else conversation_id
                cursor.execute(
                    """
                    UPDATE ai_control_settings 
                    SET is_stopped = false,
                        stop_time = NULL,
                        expiration_time = NULL,
                        updated_at = NOW()
                    WHERE conversation_id = %s
                    """,
                    (conv_id_str,)
                )
                log.info(f"AI responses resumed for conversation {conv_id_str}")
            
            conn.commit()
            
        except Exception as e:
            log.error(f"Error resuming AI responses: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                release_db_connection(conn)
    
    def get_stop_status(self, conversation_id: str, user_id: Optional[str] = None) -> Dict:
        """
        Get the current stop status for a conversation or user.
        
        Args:
            conversation_id: The ID of the conversation to check (can be string or UUID)
            user_id: Optional user ID to check (can be string or UUID)
            
        Returns:
            Dict: Status information including whether AI is stopped and expiration time
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            is_stopped = self.is_ai_stopped(conversation_id)
            
            if user_id:
                # Convert to string if it's a UUID object
                user_id_str = str(user_id) if hasattr(user_id, 'hex') else user_id
                cursor.execute(
                    """
                    SELECT stop_time, expiration_time 
                    FROM ai_control_settings 
                    WHERE user_id = %s
                    """,
                    (user_id_str,)
                )
            else:
                # Convert to string if it's a UUID object
                conv_id_str = str(conversation_id) if hasattr(conversation_id, 'hex') else conversation_id
                cursor.execute(
                    """
                    SELECT stop_time, expiration_time 
                    FROM ai_control_settings 
                    WHERE conversation_id = %s
                    """,
                    (conv_id_str,)
                )
            
            result = cursor.fetchone()
            
            if result:
                stop_time, expiration_time = result
                time_remaining = expiration_time - self._get_current_time() if expiration_time else timedelta(0)
                
                return {
                    'is_stopped': is_stopped,
                    'stop_time': stop_time.isoformat() if stop_time else None,
                    'expiration_time': expiration_time.isoformat() if expiration_time else None,
                    'time_remaining_seconds': max(0, int(time_remaining.total_seconds()))
                }
            
            return {
                'is_stopped': is_stopped,
                'stop_time': None,
                'expiration_time': None,
                'time_remaining_seconds': 0
            }
            
        except Exception as e:
            log.error(f"Error getting stop status: {str(e)}")
            return {
                'is_stopped': False,
                'stop_time': None,
                'expiration_time': None,
                'time_remaining_seconds': 0
            }
        finally:
            if conn:
                release_db_connection(conn)

# Create a singleton instance of the service
ai_control_service = AIControlService()