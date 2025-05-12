"""
Enhanced Message Handler

This module provides a consolidated and enhanced message processing system that combines:
- Advanced error handling and rate limiting
- Complete message processing pipeline
- AI response control
- Improved connection management
- State management
- Audit logging
"""

import logging
import uuid
import re
import json
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

# Core imports
from ..core.errors import (
    MessageProcessingError, StageTransitionError, ValidationError,
    RateLimitError, StateManagementError
)

# Service imports
from .services.llm_service import LLMService
from .services.stage_service import StageService
from .services.template_service import TemplateService
from .services.data_extraction_service import DataExtractionService
from .services.storage.redis_manager import RedisStateManager

# Database imports
from ..db.connection_manager import ConnectionManager

# Local imports
from .template_variables import TemplateVariableProvider
from .ai_control_service import ai_control_service

log = logging.getLogger(__name__)

class MessageHandler:
    """
    Enhanced message handler that provides a complete, robust message handling system.
    
    Features:
    - Rate limiting per business
    - AI response control
    - Comprehensive error handling
    - State management
    - Audit logging
    - Connection management with retries
    - Data extraction and validation
    """
    
    # In-memory storage for process logs
    _process_logs = {}
    
    # In-memory storage for stop flags per conversation
    _stop_flags = {}
    
    def __init__(self, db_pool, redis_manager: RedisStateManager, llm_service: Optional[LLMService] = None):
        """
        Initialize the enhanced message handler.
        
        Args:
            db_pool: Database connection pool
            redis_manager: Redis state manager for caching and rate limiting
            llm_service: Optional LLM service for AI responses
        """
        self.db_pool = db_pool
        self.redis_manager = redis_manager
        self.connection_manager = ConnectionManager(db_pool)
        self.llm_service = llm_service or LLMService(db_pool)
        self.stage_service = StageService(db_pool, redis_manager)
        self.template_service = TemplateService(db_pool, redis_manager)
        self.data_extraction_service = DataExtractionService()
        
        # Rate limiting configuration
        self.rate_limit_key_prefix = "rate_limit:"
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_max_requests = 100  # requests per minute
    
    def stop_ai_responses(self, conversation_id: str) -> None:
        """
        Stop AI from generating responses for a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation to stop
        """
        self._stop_flags[conversation_id] = True
        log.info(f"AI responses stopped for conversation {conversation_id}")
    
    def resume_ai_responses(self, conversation_id: str) -> None:
        """
        Resume AI response generation for a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation to resume
        """
        self._stop_flags[conversation_id] = False
        log.info(f"AI responses resumed for conversation {conversation_id}")
    
    def is_ai_stopped(self, conversation_id: str) -> bool:
        """
        Check if AI responses are stopped for a conversation.
        
        Args:
            conversation_id: The ID of the conversation to check
            
        Returns:
            bool: True if AI responses are stopped, False otherwise
        """
        return self._stop_flags.get(conversation_id, False)
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message with enhanced error handling and logging.
        
        Args:
            message_data: Dictionary containing message data
            
        Returns:
            Dictionary containing the processing result
        """
        log_id = str(uuid.uuid4())
        self._store_process_log(log_id, {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message_data': message_data
        })
        
        try:
            # Validate input
            self._validate_message_data(message_data)
            
            # Check rate limits
            await self._check_rate_limit(message_data['business_id'])
            
            # Check AI control
            if self._is_ai_stopped(message_data.get('conversation_id')):
                return self._create_ai_stopped_response(log_id)
            
            # Process message with connection management
            result = await self._process_with_connection(message_data)
            
            # Update state and log success
            await self._update_processing_state(result)
            self._log_successful_processing(log_id, result)
            
            return result
            
        except Exception as e:
            return await self._handle_processing_error(e, log_id, message_data)
    
    def _validate_message_data(self, message_data: Dict[str, Any]) -> None:
        """Validate incoming message data."""
        required_fields = ['business_id', 'user_id', 'content']
        missing_fields = [field for field in required_fields if field not in message_data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field=missing_fields[0]
            )
    
    async def _check_rate_limit(self, business_id: str) -> None:
        """Check if the business has exceeded rate limits."""
        rate_limit_key = f"{self.rate_limit_key_prefix}{business_id}"
        current_count = await self.redis_manager.get_rate_limit(rate_limit_key)
        
        if current_count >= self.rate_limit_max_requests:
            raise RateLimitError(
                f"Rate limit exceeded: {self.rate_limit_max_requests} requests per minute",
                service="message_processing"
            )
        
        await self.redis_manager.increment_rate_limit(rate_limit_key)
    
    def _is_ai_stopped(self, conversation_id: Optional[str]) -> bool:
        """Check if AI responses are stopped for a conversation."""
        if not conversation_id:
            return False
        return self._stop_flags.get(conversation_id, False)
    
    def _create_ai_stopped_response(self, log_id: str) -> Dict[str, Any]:
        """Create response for when AI is stopped."""
        return {
            'success': True,
            'response': None,
            'conversation_id': None,
            'message_id': None,
            'response_id': None,
            'process_log_id': log_id,
            'ai_stopped': True
        }
    
    async def _process_with_connection(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process message with connection management."""
        async def process_with_connection(conn):
            # Get or create conversation
            conversation_id = await self._get_or_create_conversation(
                conn,
                message_data['business_id'],
                message_data['user_id'],
                message_data.get('conversation_id')
            )
            
            # Process message
            return await self._process_message_content(
                conn,
                conversation_id,
                message_data
            )
        
        return await self.connection_manager.execute_with_retry(process_with_connection)
    
    async def _process_message_content(
        self,
        conn,
        conversation_id: str,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process the actual message content."""
        # Save user message
        message_id = await self._save_message(
            conn,
            conversation_id,
            message_data['content'],
            'user',
            message_data['user_id']
        )
        
        # Get current stage
        stage_info = await self.stage_service.get_current_stage(conversation_id)
        if not stage_info:
            raise StageTransitionError("Could not determine conversation stage")
        
        # Extract data
        extracted_data = await self.data_extraction_service.extract_data(
            message_data['content'],
            stage_info['extraction_rules']
        )
        
        # Get template and generate response
        template = await self.template_service.get_template(
            stage_info['template_id'],
            message_data['business_id']
        )
        
        response = await self.llm_service.generate_response(
            template,
            message_data['content'],
            extracted_data
        )
        
        # Determine next stage
        next_stage = await self.stage_service.determine_next_stage(
            conversation_id,
            stage_info['id'],
            extracted_data
        )
        
        return {
            'conversation_id': conversation_id,
            'message_id': message_id,
            'response': response,
            'stage_id': next_stage['id'],
            'extracted_data': extracted_data
        }
    
    async def _update_processing_state(self, result: Dict[str, Any]) -> None:
        """Update processing state in Redis."""
        try:
            await self.redis_manager.update_conversation_state(
                result['conversation_id'],
                {
                    'last_message_id': result['message_id'],
                    'current_stage_id': result['stage_id'],
                    'last_updated': datetime.now().isoformat()
                }
            )
        except Exception as e:
            raise StateManagementError(
                f"Failed to update conversation state: {str(e)}",
                state_key=f"conv:{result['conversation_id']}:state"
            )
    
    def _log_successful_processing(self, log_id: str, result: Dict[str, Any]) -> None:
        """Log successful message processing."""
        self._store_process_log(log_id, {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
    
    async def _handle_processing_error(
        self,
        error: Exception,
        log_id: str,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle processing errors."""
        error_message = str(error)
        log.error(f"Error processing message: {error_message}", exc_info=True)
        
        self._store_process_log(log_id, {
            'status': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': False,
            'error': error_message,
            'process_log_id': log_id
        }
    
    async def _get_or_create_conversation(
        self,
        conn,
        business_id: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Get or create a conversation."""
        if conversation_id:
            return conversation_id
            
        return await self._create_conversation(conn, business_id, user_id)
    
    async def _create_conversation(
        self,
        conn,
        business_id: str,
        user_id: str
    ) -> str:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())
        
        await conn.execute(
            """
            INSERT INTO conversations (
                conversation_id, business_id, user_id, created_at, updated_at
            ) VALUES (%s, %s, %s, NOW(), NOW())
            """,
            (conversation_id, business_id, user_id)
        )
        
        return conversation_id
    
    async def _save_message(
        self,
        conn,
        conversation_id: str,
        content: str,
        sender_type: str,
        user_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        status: str = 'delivered'
    ) -> str:
        """Save a message to the database."""
        message_id = str(uuid.uuid4())
        
        await conn.execute(
            """
            INSERT INTO messages (
                message_id, conversation_id, content, sender_type,
                user_id, stage_id, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (message_id, conversation_id, content, sender_type,
             user_id, stage_id, status)
        )
        
        return message_id
    
    @classmethod
    def _store_process_log(cls, log_id: str, log_data: Dict[str, Any]) -> None:
        """Store a process log entry."""
        cls._process_logs[log_id] = log_data
    
    @classmethod
    def get_process_log(cls, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a process log entry."""
        return cls._process_logs.get(log_id)
    
    @classmethod
    def get_recent_process_logs(cls, business_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent process logs for a business."""
        logs = [
            log for log in cls._process_logs.values()
            if log.get('message_data', {}).get('business_id') == business_id
        ]
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)[:limit]