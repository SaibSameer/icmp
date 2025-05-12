"""
Stage transition validator system.

This module handles the validation of stage transitions, including
condition evaluation and transition rules.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from ..errors import StageValidationError

logger = logging.getLogger(__name__)

class StageTransitionValidator:
    """Validates stage transitions and their conditions."""
    
    def __init__(self):
        """Initialize the transition validator."""
        self.valid_stage_types = {'initial', 'intermediate', 'final'}
        
    def validate_stage_type(self, stage_type: str) -> bool:
        """Validate stage type.
        
        Args:
            stage_type: Stage type to validate
            
        Returns:
            True if valid
            
        Raises:
            StageValidationError: If stage type is invalid
        """
        if stage_type not in self.valid_stage_types:
            raise StageValidationError(f"Invalid stage type: {stage_type}")
        return True
        
    def validate_transition_condition(self, condition: Optional[str]) -> bool:
        """Validate transition condition.
        
        Args:
            condition: Condition to validate
            
        Returns:
            True if valid
            
        Raises:
            StageValidationError: If condition is invalid
        """
        if condition is None:
            return True
            
        try:
            # TODO: Implement proper condition validation
            # For now, just check if it's a non-empty string
            if not isinstance(condition, str) or not condition.strip():
                raise StageValidationError("Invalid condition format")
            return True
            
        except Exception as e:
            logger.error(f"Error validating transition condition: {str(e)}")
            raise StageValidationError(f"Invalid transition condition: {str(e)}")
            
    def validate_transition(
        self,
        from_stage_type: str,
        to_stage_type: str,
        condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a stage transition.
        
        Args:
            from_stage_type: Source stage type
            to_stage_type: Target stage type
            condition: Optional transition condition
            
        Returns:
            Validation result
            
        Raises:
            StageValidationError: If transition is invalid
        """
        try:
            # Validate stage types
            self.validate_stage_type(from_stage_type)
            self.validate_stage_type(to_stage_type)
            
            # Validate condition
            self.validate_transition_condition(condition)
            
            # Check transition rules
            if from_stage_type == 'final':
                raise StageValidationError("Cannot transition from a final stage")
                
            if to_stage_type == 'initial':
                raise StageValidationError("Cannot transition to an initial stage")
                
            return {
                "is_valid": True,
                "errors": []
            }
            
        except StageValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating transition: {str(e)}")
            raise StageValidationError(f"Failed to validate transition: {str(e)}")
            
    def evaluate_transition_condition(
        self,
        condition: Optional[str],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a transition condition against context.
        
        Args:
            condition: Condition to evaluate
            context: Context data
            
        Returns:
            True if condition is met
            
        Raises:
            StageValidationError: If condition evaluation fails
        """
        if condition is None:
            return True
            
        try:
            # TODO: Implement proper condition evaluation
            # For now, return True for all conditions
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating transition condition: {str(e)}")
            raise StageValidationError(f"Failed to evaluate condition: {str(e)}")
            
    def get_valid_transitions(
        self,
        current_stage_type: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid transitions for current stage.
        
        Args:
            current_stage_type: Current stage type
            context: Context data
            
        Returns:
            List of valid transitions
            
        Raises:
            StageValidationError: If validation fails
        """
        try:
            # Validate current stage type
            self.validate_stage_type(current_stage_type)
            
            # Get valid target types
            valid_targets = self.valid_stage_types - {'initial'}
            if current_stage_type == 'final':
                valid_targets = set()
                
            return [
                {
                    "from_type": current_stage_type,
                    "to_type": target_type,
                    "is_valid": True
                }
                for target_type in valid_targets
            ]
            
        except StageValidationError:
            raise
        except Exception as e:
            logger.error(f"Error getting valid transitions: {str(e)}")
            raise StageValidationError(f"Failed to get valid transitions: {str(e)}") 