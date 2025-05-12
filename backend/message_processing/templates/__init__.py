"""
Template system package.

This package provides a modular system for template management, including
variable handling, rendering, and validation.
"""

from .variable_provider import TemplateVariableProvider
from .renderer import TemplateRenderer
from .validator import TemplateValidator

__all__ = ['TemplateVariableProvider', 'TemplateRenderer', 'TemplateValidator'] 