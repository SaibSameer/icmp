"""
Message processing package for ICMP.

This package contains the classes and functions for handling messages in the
Intelligent Conversation Management Platform (ICMP).
"""

from .message_handler import MessageHandler
from .services.stage_service import StageService
from .services.template_service import TemplateService
from .template_variables import TemplateVariableProvider

# Import variables package to ensure all providers are registered
from . import variables

__all__ = [
    'MessageHandler', 
    'StageService',
    'TemplateVariableProvider',
    'TemplateService'
]