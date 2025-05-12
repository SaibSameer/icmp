"""
Stage management package.

This package provides a modular system for stage management, including
stage transitions, validation, and state management.
"""

from .stage_manager import StageManager
from .transition_validator import StageTransitionValidator
from .state_manager import StageStateManager

__all__ = ['StageManager', 'StageTransitionValidator', 'StageStateManager'] 