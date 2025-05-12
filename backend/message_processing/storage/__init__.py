"""
Storage module for message processing system.
Contains Redis state management and other storage-related functionality.
"""

from .redis_manager import RedisStateManager

__all__ = ['RedisStateManager'] 