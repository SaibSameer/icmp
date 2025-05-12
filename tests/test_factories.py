"""
Tests for the test data factories.
"""

import pytest
from datetime import datetime
from tests.factories import (
    template_factory,
    message_factory,
    business_factory,
    stage_factory
)

def test_template_factory():
    """Test template factory creation."""
    # Test default creation
    template = template_factory.create()
    assert template['template_id']
    assert template['name'].startswith('Test Template')
    assert template['content'] == 'Hello {name}, your order {order_id} is ready.'
    assert template['variables'] == ['name', 'order_id']
    assert isinstance(template['created_at'], datetime)
    assert isinstance(template['updated_at'], datetime)
    
    # Test custom values
    custom_template = template_factory.create(
        name='Custom Template',
        content='Custom content {var}',
        variables=['var']
    )
    assert custom_template['name'] == 'Custom Template'
    assert custom_template['content'] == 'Custom content {var}'
    assert custom_template['variables'] == ['var']

def test_message_factory():
    """Test message factory creation."""
    # Test default creation
    message = message_factory.create()
    assert message['message_id']
    assert message['content'].startswith('Test message')
    assert message['channel'] == 'whatsapp'
    assert message['sender_id']
    assert isinstance(message['timestamp'], datetime)
    assert message['status'] == 'pending'
    
    # Test custom values
    custom_message = message_factory.create(
        content='Custom message',
        channel='telegram',
        status='processed'
    )
    assert custom_message['content'] == 'Custom message'
    assert custom_message['channel'] == 'telegram'
    assert custom_message['status'] == 'processed'

def test_business_factory():
    """Test business factory creation."""
    # Test default creation
    business = business_factory.create()
    assert business['business_id']
    assert business['name'].startswith('Test Business')
    assert business['api_key'].startswith('test_api_key_')
    assert business['internal_api_key'].startswith('test_internal_key_')
    assert business['owner_id']
    assert isinstance(business['created_at'], datetime)
    assert isinstance(business['updated_at'], datetime)
    
    # Test custom values
    custom_business = business_factory.create(
        name='Custom Business',
        api_key='custom_key',
        internal_api_key='custom_internal_key'
    )
    assert custom_business['name'] == 'Custom Business'
    assert custom_business['api_key'] == 'custom_key'
    assert custom_business['internal_api_key'] == 'custom_internal_key'

def test_stage_factory():
    """Test stage factory creation."""
    # Test default creation
    stage = stage_factory.create()
    assert stage['stage_id']
    assert stage['name'].startswith('Test Stage')
    assert stage['business_id']
    assert stage['template_id']
    assert isinstance(stage['created_at'], datetime)
    assert isinstance(stage['updated_at'], datetime)
    
    # Test with provided business and template IDs
    business_id = 'test_business_id'
    template_id = 'test_template_id'
    stage_with_ids = stage_factory.create(
        business_id=business_id,
        template_id=template_id
    )
    assert stage_with_ids['business_id'] == business_id
    assert stage_with_ids['template_id'] == template_id
    
    # Test custom values
    custom_stage = stage_factory.create(
        name='Custom Stage'
    )
    assert custom_stage['name'] == 'Custom Stage'

def test_factory_sequences():
    """Test that factory sequences increment correctly."""
    # Test template sequence
    template1 = template_factory.create()
    template2 = template_factory.create()
    assert template1['name'] != template2['name']
    
    # Test message sequence
    message1 = message_factory.create()
    message2 = message_factory.create()
    assert message1['content'] != message2['content']
    
    # Test business sequence
    business1 = business_factory.create()
    business2 = business_factory.create()
    assert business1['name'] != business2['name']
    
    # Test stage sequence
    stage1 = stage_factory.create()
    stage2 = stage_factory.create()
    assert stage1['name'] != stage2['name'] 