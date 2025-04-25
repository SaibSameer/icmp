"""
Message processing package for ICMP.

This package contains the classes and functions for handling messages in the
Intelligent Conversation Management Platform (ICMP).
"""

from .message_handler import MessageHandler
from .stage_service import StageService
from .context_service import ContextService
from .template_variables import TemplateVariableProvider
from .template_service import TemplateService

# Import variables package to ensure all providers are registered
from . import variables

__all__ = [
    'MessageHandler', 
    'StageService', 
    'ContextService',
    'TemplateVariableProvider',
    'TemplateService'
]