"""
Base stage handler.

This module defines the base stage handler class.
"""

import logging
from typing import Dict, Any, Optional
from ...core.errors import StageTransitionError
from ...core.handler.base_handler import BaseMessageHandler

class BaseStageHandler(BaseMessageHandler):
    """Base class for stage handlers."""
    
    def __init__(self):
        """Initialize base stage handler."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    async def handle_stage(self, message: Dict[str, Any], stage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message in current stage.
        
        Args:
            message: Message data
            stage_config: Stage configuration
            
        Returns:
            Updated message data
            
        Raises:
            StageTransitionError: If stage transition fails
        """
        try:
            # Validate message
            await self.validate_message(message)
            
            # Process message in stage
            result = await self._process_stage(message, stage_config)
            
            # Check for stage transition
            next_stage = await self._check_transition(result, stage_config)
            if next_stage:
                result["next_stage"] = next_stage
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling stage: {str(e)}")
            raise StageTransitionError(
                message="Failed to handle stage",
                error_code="STAGE_HANDLER_ERROR",
                details=str(e)
            )
            
    async def _process_stage(self, message: Dict[str, Any], stage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process message in stage.
        
        Args:
            message: Message data
            stage_config: Stage configuration
            
        Returns:
            Updated message data
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("_process_stage must be implemented by subclass")
        
    async def _check_transition(self, result: Dict[str, Any], stage_config: Dict[str, Any]) -> Optional[str]:
        """Check if stage transition is needed.
        
        Args:
            result: Stage processing result
            stage_config: Stage configuration
            
        Returns:
            Next stage name if transition needed, None otherwise
        """
        transitions = stage_config.get("transitions", [])
        for transition in transitions:
            if await self._evaluate_transition_condition(result, transition):
                return transition["to_stage"]
        return None
        
    async def _evaluate_transition_condition(self, result: Dict[str, Any], transition: Dict[str, Any]) -> bool:
        """Evaluate transition condition.
        
        Args:
            result: Stage processing result
            transition: Transition configuration
            
        Returns:
            True if condition is met, False otherwise
        """
        condition = transition.get("condition")
        if not condition:
            return True
            
        # TODO: Implement condition evaluation logic
        return False 