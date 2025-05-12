"""
Base message handler.

This module provides the base class for message handling functionality.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from ..errors.message_errors import (
    MessageProcessingError, ValidationError, ProcessingError,
    StageTransitionError, StateManagementError
)
from ...services.stage_service import StageService
from ...services.template_service import TemplateService
from ...services.data_extraction_service import DataExtractionService
from ...services.llm_service import LLMService
from ...storage.redis_manager import RedisStateManager

logger = logging.getLogger(__name__)

class BaseMessageHandler:
    """Base class for message handlers with enhanced functionality."""
    
    def __init__(
        self,
        db_pool,
        redis_manager: RedisStateManager,
        llm_service: Optional[LLMService] = None,
        stage_service: Optional[StageService] = None,
        template_service: Optional[TemplateService] = None,
        data_extraction_service: Optional[DataExtractionService] = None
    ):
        """Initialize the base handler with required services.
        
        Args:
            db_pool: Database connection pool
            redis_manager: Redis state manager
            llm_service: Optional LLM service
            stage_service: Optional stage service
            template_service: Optional template service
            data_extraction_service: Optional data extraction service
        """
        self.db_pool = db_pool
        self.redis_manager = redis_manager
        self.llm_service = llm_service
        self.stage_service = stage_service
        self.template_service = template_service
        self.data_extraction_service = data_extraction_service
        self.logger = logger
        self._process_logs = {}
        self._stop_flags = {}
        self._processors: List[Callable] = []
        
    async def validate_message(self, message_data: Dict[str, Any]) -> bool:
        """Validate incoming message data.
        
        Args:
            message_data: Message data to validate
            
        Returns:
            True if message is valid
            
        Raises:
            ValidationError: If message is invalid
        """
        required_fields = ['business_id', 'user_id', 'content']
        missing_fields = [field for field in required_fields if field not in message_data]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
        return True
        
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message through the complete pipeline.
        
        Args:
            message_data: Message data to process
            
        Returns:
            Processed message data
            
        Raises:
            MessageProcessingError: If processing fails
        """
        log_id = str(uuid.uuid4())
        self._store_process_log(log_id, {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message_data': message_data
        })
        
        try:
            # Validate message
            await self.validate_message(message_data)
            
            # Check AI control
            if self._is_ai_stopped(message_data.get('user_id')):
                return self._handle_ai_stopped_response(log_id)
            
            # Process through pipeline
            result = await self._process_message_pipeline(message_data)
            
            # Store successful result
            self._store_process_log(log_id, {
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'result': result
            })
            
            return result
            
        except MessageProcessingError as e:
            return self._handle_processing_error(e, log_id)
        except Exception as e:
            return self._handle_unexpected_error(e, log_id)
            
    async def _process_message_pipeline(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process message through the complete pipeline.
        
        Args:
            message_data: Message data to process
            
        Returns:
            Processed message data
        """
        # Apply registered processors
        result = message_data.copy()
        for processor in self._processors:
            result = await processor(result)
            
        # Get or create conversation
        conversation_id = await self._get_or_create_conversation(
            result['business_id'],
            result['user_id'],
            result.get('conversation_id')
        )
        
        # Get current stage
        stage_info = await self.stage_service.get_current_stage(conversation_id)
        if not stage_info:
            raise StageTransitionError("Could not determine conversation stage")
            
        # Process stage message
        response = await self._process_stage_message(
            conversation_id,
            result['business_id'],
            result['user_id'],
            result['content'],
            stage_info
        )
        
        return {
            'success': True,
            'conversation_id': conversation_id,
            'response': response.get('content'),
            'stage_id': stage_info.get('stage_id'),
            'extracted_data': response.get('extracted_data')
        }
        
    def add_processor(self, processor: Callable) -> None:
        """Add a message processor to the pipeline.
        
        Args:
            processor: Processing function
            
        Raises:
            ValueError: If processor is not callable
        """
        if not callable(processor):
            raise ValueError("Processor must be callable")
            
        self._processors.append(processor)
        
    def stop_ai_responses(self, user_id: str) -> None:
        """Stop AI responses for a user.
        
        Args:
            user_id: User ID to stop AI responses for
        """
        self._stop_flags[user_id] = True
        self.logger.info(f"AI responses stopped for user {user_id}")
        
    def resume_ai_responses(self, user_id: str) -> None:
        """Resume AI responses for a user.
        
        Args:
            user_id: User ID to resume AI responses for
        """
        self._stop_flags[user_id] = False
        self.logger.info(f"AI responses resumed for user {user_id}")
        
    def _is_ai_stopped(self, user_id: str) -> bool:
        """Check if AI responses are stopped for a user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if AI responses are stopped
        """
        return self._stop_flags.get(user_id, False)
        
    def _store_process_log(self, log_id: str, log_data: Dict[str, Any]) -> None:
        """Store process log data.
        
        Args:
            log_id: Log ID
            log_data: Log data to store
        """
        self._process_logs[log_id] = log_data
        
    def _handle_ai_stopped_response(self, log_id: str) -> Dict[str, Any]:
        """Handle response when AI is stopped.
        
        Args:
            log_id: Log ID
            
        Returns:
            Response data
        """
        self._store_process_log(log_id, {
            'status': 'ai_stopped',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'response': None,
            'conversation_id': None,
            'message_id': None,
            'response_id': None,
            'process_log_id': log_id,
            'ai_stopped': True
        }
        
    def _handle_processing_error(self, error: MessageProcessingError, log_id: str) -> Dict[str, Any]:
        """Handle message processing error.
        
        Args:
            error: Error that occurred
            log_id: Log ID
            
        Returns:
            Error response
        """
        self._store_process_log(log_id, {
            'status': 'error',
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': False,
            'error': str(error),
            'process_log_id': log_id
        }
        
    def _handle_unexpected_error(self, error: Exception, log_id: str) -> Dict[str, Any]:
        """Handle unexpected error.
        
        Args:
            error: Error that occurred
            log_id: Log ID
            
        Returns:
            Error response
        """
        self.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        self._store_process_log(log_id, {
            'status': 'error',
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': False,
            'error': "An unexpected error occurred",
            'process_log_id': log_id
        }
        
    async def _get_or_create_conversation(
        self,
        business_id: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Get or create a conversation.
        
        Args:
            business_id: Business ID
            user_id: User ID
            conversation_id: Optional existing conversation ID
            
        Returns:
            Conversation ID
        """
        raise NotImplementedError("Subclasses must implement _get_or_create_conversation")
        
    async def _process_stage_message(
        self,
        conversation_id: str,
        business_id: str,
        user_id: str,
        content: str,
        stage_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a message in a specific stage.
        
        Args:
            conversation_id: Conversation ID
            business_id: Business ID
            user_id: User ID
            content: Message content
            stage_info: Stage information
            
        Returns:
            Processed message data
        """
        raise NotImplementedError("Subclasses must implement _process_stage_message")
        
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle processing errors.
        
        Args:
            error: The error that occurred
            
        Returns:
            Error response data
        """
        if isinstance(error, MessageProcessingError):
            return {
                'success': False,
                'error': error.message,
                'error_code': error.error_code,
                'details': error.details
            }
        else:
            return {
                'success': False,
                'error': str(error),
                'error_code': 'UNKNOWN_ERROR'
            } 