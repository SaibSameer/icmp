"""
Template renderer system.

This module handles the rendering of templates with variable substitution
and conditional logic.
"""

import logging
from typing import Dict, Any, List, Optional
from .variable_provider import TemplateVariableProvider

log = logging.getLogger(__name__)

class TemplateRenderer:
    """Handles template rendering with variable substitution."""
    
    def __init__(self, variable_provider: TemplateVariableProvider):
        """Initialize the template renderer."""
        self.variable_provider = variable_provider
    
    def render_text_template(self, content: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render a text template with variable substitution."""
        try:
            template_text = content.get('text', '')
            if not template_text:
                return ''
                
            # Replace variables in template
            for key, value in context.items():
                placeholder = f"{{{{{key}}}}}"
                template_text = template_text.replace(placeholder, str(value))
                
            return template_text
            
        except Exception as e:
            log.error(f"Text template rendering failed: {str(e)}")
            raise
    
    def render_structured_template(self, content: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render a structured template with component substitution."""
        try:
            components = content.get('components', [])
            if not components:
                return ''
                
            rendered_components = []
            for component in components:
                component_type = component.get('type')
                if component_type == 'text':
                    rendered_components.append(self.render_text_template(component, context))
                elif component_type == 'variable':
                    var_name = component.get('name')
                    if var_name in context:
                        rendered_components.append(str(context[var_name]))
                elif component_type == 'conditional':
                    if self.evaluate_condition(component.get('condition', ''), context):
                        rendered_components.append(self.render_text_template(component, context))
                        
            return ' '.join(filter(None, rendered_components))
            
        except Exception as e:
            log.error(f"Structured template rendering failed: {str(e)}")
            raise
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string against the context."""
        try:
            # TODO: Implement more complex condition evaluation
            # For now, return True for all conditions
            return True
        except Exception:
            return False
    
    def render_template(
        self,
        template_content: Dict[str, Any],
        template_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Render a template based on its type."""
        try:
            if template_type == 'text':
                return self.render_text_template(template_content, context)
            elif template_type == 'structured':
                return self.render_structured_template(template_content, context)
            else:
                raise ValueError(f"Unsupported template type: {template_type}")
                
        except Exception as e:
            log.error(f"Template rendering failed: {str(e)}")
            raise 