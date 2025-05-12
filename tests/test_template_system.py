"""
Test suite for the template system.
"""

import pytest
from datetime import datetime
from backend.message_processing.template_system import TemplateSystem
from backend.message_processing.template_validator import TemplateValidator

@pytest.mark.unit
class TestTemplateSystem:
    """Test cases for the template system."""

    def test_template_creation(self, test_db_pool, sample_template):
        """Test creating a new template."""
        template_system = TemplateSystem(test_db_pool)
        result = template_system.create_template(sample_template)
        
        assert result['template_id'] == sample_template['template_id']
        assert result['name'] == sample_template['name']
        assert result['content'] == sample_template['content']
        assert result['variables'] == sample_template['variables']

    def test_template_validation(self, sample_template):
        """Test template validation."""
        validator = TemplateValidator()
        result = validator.validate_template(sample_template)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0

    def test_template_rendering(self, test_db_pool, sample_template):
        """Test template rendering with variables."""
        template_system = TemplateSystem(test_db_pool)
        variables = {
            'name': 'John',
            'order_id': '12345'
        }
        
        rendered = template_system.render_template(
            sample_template['template_id'],
            variables
        )
        
        assert rendered == 'Hello John, your order 12345 is ready.'

    def test_template_update(self, test_db_pool, sample_template):
        """Test updating an existing template."""
        template_system = TemplateSystem(test_db_pool)
        
        # First create the template
        template_system.create_template(sample_template)
        
        # Update the template
        updated_content = 'Updated: Hello {name}, your order {order_id} is ready.'
        sample_template['content'] = updated_content
        
        result = template_system.update_template(sample_template)
        
        assert result['content'] == updated_content
        assert result['updated_at'] > result['created_at']

    def test_template_deletion(self, test_db_pool, sample_template):
        """Test deleting a template."""
        template_system = TemplateSystem(test_db_pool)
        
        # First create the template
        template_system.create_template(sample_template)
        
        # Delete the template
        result = template_system.delete_template(sample_template['template_id'])
        
        assert result['success'] is True
        
        # Verify template is deleted
        with pytest.raises(Exception):
            template_system.get_template(sample_template['template_id'])

@pytest.mark.integration
class TestTemplateSystemIntegration:
    """Integration tests for the template system."""

    def test_template_with_stage(self, test_db_pool, sample_template, sample_stage):
        """Test template integration with stage management."""
        template_system = TemplateSystem(test_db_pool)
        
        # Create template
        template = template_system.create_template(sample_template)
        
        # Create stage with template
        stage = template_system.create_stage(sample_stage)
        
        assert stage['template_id'] == template['template_id']
        assert stage['business_id'] == sample_stage['business_id']

    def test_template_variable_validation(self, test_db_pool, sample_template):
        """Test template variable validation and processing."""
        template_system = TemplateSystem(test_db_pool)
        
        # Create template
        template = template_system.create_template(sample_template)
        
        # Test with missing variable
        with pytest.raises(ValueError):
            template_system.render_template(
                template['template_id'],
                {'name': 'John'}  # Missing order_id
            )
        
        # Test with extra variable
        result = template_system.render_template(
            template['template_id'],
            {
                'name': 'John',
                'order_id': '12345',
                'extra_var': 'value'  # Extra variable should be ignored
            }
        )
        
        assert result == 'Hello John, your order 12345 is ready.' 