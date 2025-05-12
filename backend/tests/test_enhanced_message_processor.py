"""
Tests for the Enhanced Message Processor.

This module contains comprehensive tests for the enhanced message processing system,
verifying all major functionality including:
- Message processing
- Error handling
- Rate limiting
- AI control
- State management
- Audit logging
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from backend.message_processing.enhanced_message_processor import EnhancedMessageProcessor
from backend.core.errors import (
    MessageProcessingError, StageTransitionError, ValidationError,
    RateLimitError, StateManagementError
)

@pytest.fixture
def mock_db_pool():
    """Mock database pool."""
    return AsyncMock()

@pytest.fixture
def mock_redis_manager():
    """Mock Redis manager."""
    return AsyncMock()

@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    return AsyncMock()

@pytest.fixture
def processor(mock_db_pool, mock_redis_manager, mock_llm_service):
    """Create processor instance with mocked dependencies."""
    return EnhancedMessageProcessor(
        mock_db_pool,
        mock_redis_manager,
        mock_llm_service
    )

@pytest.fixture
def valid_message_data():
    """Valid message data for testing."""
    return {
        'business_id': str(uuid.uuid4()),
        'user_id': str(uuid.uuid4()),
        'content': 'Test message',
        'conversation_id': str(uuid.uuid4())
    }

class TestEnhancedMessageProcessor:
    """Test suite for EnhancedMessageProcessor."""
    
    async def test_process_message_success(self, processor, valid_message_data, mock_redis_manager):
        """Test successful message processing."""
        # Setup
        mock_redis_manager.get_rate_limit.return_value = 0
        processor._process_with_connection = AsyncMock(return_value={
            'conversation_id': valid_message_data['conversation_id'],
            'message_id': str(uuid.uuid4()),
            'response': 'Test response',
            'stage_id': str(uuid.uuid4()),
            'extracted_data': {}
        })
        
        # Execute
        result = await processor.process_message(valid_message_data)
        
        # Verify
        assert result['success'] is True
        assert 'response' in result
        assert 'conversation_id' in result
        assert 'message_id' in result
        assert 'stage_id' in result
    
    async def test_process_message_missing_fields(self, processor):
        """Test message processing with missing required fields."""
        # Setup
        invalid_data = {
            'business_id': str(uuid.uuid4()),
            # Missing user_id and content
        }
        
        # Execute
        result = await processor.process_message(invalid_data)
        
        # Verify
        assert result['success'] is False
        assert 'error' in result
        assert 'Missing required fields' in result['error']
    
    async def test_process_message_rate_limit(self, processor, valid_message_data, mock_redis_manager):
        """Test rate limiting functionality."""
        # Setup
        mock_redis_manager.get_rate_limit.return_value = 100  # Exceed rate limit
        
        # Execute
        result = await processor.process_message(valid_message_data)
        
        # Verify
        assert result['success'] is False
        assert 'error' in result
        assert 'Rate limit exceeded' in result['error']
    
    async def test_process_message_ai_stopped(self, processor, valid_message_data):
        """Test message processing when AI is stopped."""
        # Setup
        processor._stop_flags[valid_message_data['user_id']] = True
        
        # Execute
        result = await processor.process_message(valid_message_data)
        
        # Verify
        assert result['success'] is True
        assert result['ai_stopped'] is True
        assert result['response'] is None
    
    async def test_process_message_error_handling(self, processor, valid_message_data):
        """Test error handling during message processing."""
        # Setup
        processor._process_with_connection = AsyncMock(side_effect=Exception("Test error"))
        
        # Execute
        result = await processor.process_message(valid_message_data)
        
        # Verify
        assert result['success'] is False
        assert 'error' in result
        assert 'error_id' in result
        assert 'process_log_id' in result
    
    async def test_audit_logging(self, processor, valid_message_data, mock_db_pool):
        """Test audit logging functionality."""
        # Setup
        action_type = 'test_action'
        action_data = {'test': 'data'}
        
        # Execute
        await processor._log_audit(
            valid_message_data['business_id'],
            valid_message_data['user_id'],
            action_type,
            action_data
        )
        
        # Verify
        mock_db_pool.acquire.assert_called_once()
        mock_db_pool.acquire.return_value.__aenter__.return_value.execute.assert_called_once()
    
    def test_process_log_storage(self, processor, valid_message_data):
        """Test process log storage and retrieval."""
        # Setup
        log_id = str(uuid.uuid4())
        log_data = {
            'status': 'test',
            'timestamp': datetime.now().isoformat(),
            'message_data': valid_message_data
        }
        
        # Execute
        processor._store_process_log(log_id, log_data)
        retrieved_log = processor.get_process_log(log_id)
        
        # Verify
        assert retrieved_log == log_data
    
    def test_recent_process_logs(self, processor, valid_message_data):
        """Test retrieval of recent process logs."""
        # Setup
        business_id = valid_message_data['business_id']
        for i in range(15):  # Create 15 logs
            log_id = str(uuid.uuid4())
            log_data = {
                'status': 'test',
                'timestamp': datetime.now().isoformat(),
                'message_data': {'business_id': business_id}
            }
            processor._store_process_log(log_id, log_data)
        
        # Execute
        recent_logs = processor.get_recent_process_logs(business_id, limit=10)
        
        # Verify
        assert len(recent_logs) == 10  # Should return only 10 most recent logs
        assert all(log['message_data']['business_id'] == business_id for log in recent_logs) 