"""
Test data factories for the ICMP Events API system.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class TestDataFactory:
    """Base factory class for creating test data."""
    
    def __init__(self):
        self._defaults = {}
        self._sequences = {}
    
    def _get_next_sequence(self, name: str) -> int:
        """Get the next value in a sequence."""
        if name not in self._sequences:
            self._sequences[name] = 0
        self._sequences[name] += 1
        return self._sequences[name]
    
    def _generate_uuid(self) -> str:
        """Generate a UUID for entity IDs."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> datetime:
        """Get current timestamp."""
        return datetime.utcnow()

class TemplateFactory(TestDataFactory):
    """Factory for creating template test data."""
    
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a template with default or custom values."""
        template_id = kwargs.get('template_id', self._generate_uuid())
        sequence = self._get_next_sequence('template')
        
        return {
            'template_id': template_id,
            'name': kwargs.get('name', f'Test Template {sequence}'),
            'content': kwargs.get('content', 'Hello {name}, your order {order_id} is ready.'),
            'variables': kwargs.get('variables', ['name', 'order_id']),
            'created_at': kwargs.get('created_at', self._get_timestamp()),
            'updated_at': kwargs.get('updated_at', self._get_timestamp())
        }

class MessageFactory(TestDataFactory):
    """Factory for creating message test data."""
    
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a message with default or custom values."""
        message_id = kwargs.get('message_id', self._generate_uuid())
        sequence = self._get_next_sequence('message')
        
        return {
            'message_id': message_id,
            'content': kwargs.get('content', f'Test message {sequence}'),
            'channel': kwargs.get('channel', 'whatsapp'),
            'sender_id': kwargs.get('sender_id', self._generate_uuid()),
            'timestamp': kwargs.get('timestamp', self._get_timestamp()),
            'status': kwargs.get('status', 'pending')
        }

class BusinessFactory(TestDataFactory):
    """Factory for creating business test data."""
    
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a business with default or custom values."""
        business_id = kwargs.get('business_id', self._generate_uuid())
        sequence = self._get_next_sequence('business')
        
        return {
            'business_id': business_id,
            'name': kwargs.get('name', f'Test Business {sequence}'),
            'api_key': kwargs.get('api_key', f'test_api_key_{sequence}'),
            'internal_api_key': kwargs.get('internal_api_key', f'test_internal_key_{sequence}'),
            'owner_id': kwargs.get('owner_id', self._generate_uuid()),
            'created_at': kwargs.get('created_at', self._get_timestamp()),
            'updated_at': kwargs.get('updated_at', self._get_timestamp())
        }

class StageFactory(TestDataFactory):
    """Factory for creating stage test data."""
    
    def create(self, business_id: Optional[str] = None, template_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Create a stage with default or custom values."""
        stage_id = kwargs.get('stage_id', self._generate_uuid())
        sequence = self._get_next_sequence('stage')
        
        return {
            'stage_id': stage_id,
            'business_id': business_id or kwargs.get('business_id', self._generate_uuid()),
            'name': kwargs.get('name', f'Test Stage {sequence}'),
            'template_id': template_id or kwargs.get('template_id', self._generate_uuid()),
            'created_at': kwargs.get('created_at', self._get_timestamp()),
            'updated_at': kwargs.get('updated_at', self._get_timestamp())
        }

# Create factory instances
template_factory = TemplateFactory()
message_factory = MessageFactory()
business_factory = BusinessFactory()
stage_factory = StageFactory() 