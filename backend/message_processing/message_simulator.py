"""
Message Simulator for testing message processing.

This module provides functionality to simulate message processing
for testing and development purposes.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from backend.message_processing.message_handler import MessageHandler
from backend.message_processing.services.stage_service import StageService
from backend.message_processing.services.template_service import TemplateService
from backend.database.db import get_db_pool
from backend.redis.redis_state_manager import RedisStateManager
from backend.config import Config
from ..db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

class MessageSimulator:
    """
    Interface for simulating message processing and testing the template system.
    
    This class provides methods to:
    - Send test messages
    - View conversation history
    - Test template applications
    - Monitor message processing flow
    """
    
    def __init__(self):
        """Initialize the message simulator with required services."""
        # Initialize database pool
        self.db_pool = get_db_pool()
        
        # Initialize Redis manager with configuration
        self.redis_manager = RedisStateManager(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            password=Config.REDIS_PASSWORD,
            ssl=Config.REDIS_SSL
        )
        
        # Initialize services with both db_pool and redis_manager
        self.stage_service = StageService(self.db_pool, self.redis_manager)
        self.template_service = TemplateService(self.db_pool, self.redis_manager)
        self.message_handler = MessageHandler(
            db_pool=self.db_pool,
            redis_manager=self.redis_manager
        )
    
    def simulate_message(self, user_id: str, message_content: str, 
                        business_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate sending a message and process it through the system.
        
        Args:
            user_id: ID of the user sending the message
            message_content: Content of the message
            business_id: ID of the business context
            conversation_id: Optional ID of existing conversation
            
        Returns:
            Dictionary containing processing results
        """
        conn = None
        try:
            log.info(f"Starting message simulation for user {user_id} to business {business_id}")
            log.info(f"Message content: {message_content}")
            
            # Get database connection
            conn = get_db_connection()
            if not conn:
                raise Exception("Failed to get database connection")
            
            # Start transaction
            conn.autocommit = False
            
            # If no conversation_id provided, create new conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                log.info(f"Creating new conversation with ID: {conversation_id}")
                
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversations 
                    (conversation_id, business_id, user_id, session_id, status)
                    VALUES (%s, %s, %s, %s, 'active')
                    """,
                    (conversation_id, business_id, user_id, str(uuid.uuid4()))
                )
                log.info("Created new conversation record")
                conn.commit()
            
            # Process the message through the handler
            message_data = {
                'business_id': business_id,
                'user_id': user_id,
                'content': message_content,
                'conversation_id': conversation_id
            }
            
            result = self.message_handler.process_message(message_data)
            log.info(f"Message processed successfully: {result}")
            
            # Add simulation metadata
            result['simulation_timestamp'] = datetime.now().isoformat()
            result['simulation_type'] = 'test_message'
            
            return result
            
        except Exception as e:
            log.error(f"Error in message simulation: {str(e)}", exc_info=True)
            if conn:
                try:
                    conn.rollback()
                    log.info("Transaction rolled back due to error")
                except Exception as rollback_error:
                    log.error(f"Error during rollback: {str(rollback_error)}")
            return {
                'success': False,
                'error': str(e),
                'simulation_timestamp': datetime.now().isoformat()
            }
        finally:
            if conn:
                release_db_connection(conn)
                log.info("Database connection released")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve the history of a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT message_id, message_content, sender_type, created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'message_id': row['message_id'],
                    'content': row['message_content'],
                    'sender': row['sender_type'],
                    'timestamp': row['created_at'].isoformat()
                })
            
            cursor.close()
            return messages
            
        except Exception as e:
            log.error(f"Error retrieving conversation history: {str(e)}")
            return []
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of conversations
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT conversation_id, created_at, updated_at
                FROM conversations
                WHERE user_id = %s
                ORDER BY updated_at DESC
                """,
                (user_id,)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'conversation_id': row['conversation_id'],
                    'created_at': row['created_at'].isoformat(),
                    'updated_at': row['updated_at'].isoformat()
                })
            
            cursor.close()
            return conversations
            
        except Exception as e:
            log.error(f"Error retrieving user conversations: {str(e)}")
            return []
        finally:
            if conn:
                self.db_pool.putconn(conn)

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: Message data
            
        Returns:
            Processing result
        """
        try:
            # Get current stage
            current_stage = self.stage_service.get_current_stage(message['conversation_id'])
            
            # Process message
            result = self.message_handler.process_message(message)
            
            # Update stage if needed
            if result.get('next_stage'):
                self.stage_service.set_current_stage(
                    message['conversation_id'],
                    result['next_stage']
                )
            
            return result
            
        except Exception as e:
            log.error(f"Error processing message: {str(e)}")
            raise
    
    def clear_state(self, conversation_id: str) -> None:
        """Clear conversation state.
        
        Args:
            conversation_id: Conversation ID
        """
        try:
            self.stage_service.clear_stage_state(conversation_id)
        except Exception as e:
            log.error(f"Error clearing state: {str(e)}")
            raise 