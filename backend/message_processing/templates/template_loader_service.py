"""
Template loader.

This module defines the template loader class.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from .validator import TemplateValidator

class TemplateLoader:
    """Template loader for loading and caching templates."""
    
    def __init__(self, template_dir: str):
        """Initialize template loader.
        
        Args:
            template_dir: Directory containing templates
        """
        self.logger = logging.getLogger(__name__)
        self.template_dir = template_dir
        self.template_cache: Dict[str, Dict[str, Any]] = {}
        self.validator = TemplateValidator()
        
    async def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load template by name.
        
        Args:
            template_name: Name of template to load
            
        Returns:
            Template data
            
        Raises:
            FileNotFoundError: If template file not found
            ValueError: If template is invalid
        """
        # Check cache first
        if template_name in self.template_cache:
            return self.template_cache[template_name]
            
        # Load template file
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
            
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
                
            # Validate template
            if not await self.validator.validate(template_data):
                raise ValueError(f"Invalid template: {template_name}")
                
            # Cache template
            self.template_cache[template_name] = template_data
            return template_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error loading template {template_name}: {str(e)}")
            raise ValueError(f"Invalid template file format: {template_name}")
            
    async def load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates in directory.
        
        Returns:
            Dictionary of template name to template data
        """
        templates = {}
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.json'):
                template_name = os.path.splitext(filename)[0]
                try:
                    templates[template_name] = await self.load_template(template_name)
                except Exception as e:
                    self.logger.error(f"Error loading template {template_name}: {str(e)}")
        return templates
        
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.template_cache.clear()
        
    def get_cached_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get currently cached templates.
        
        Returns:
            Dictionary of cached template name to template data
        """
        return self.template_cache.copy() 