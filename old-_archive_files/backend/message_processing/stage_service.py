"""
Stage service for conversation flow management.

This module provides functionality for managing conversation stages,
determining the current stage, and handling transitions between stages.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import uuid
import json

log = logging.getLogger(__name__)

class StageService:
    """
    Service for managing conversation flow stages.
    
    Provides methods for retrieving the current stage of a conversation,
    determining next stages, and managing stage transitions based on 
    conversation state and user inputs.
    """
    
    def __init__(self, db_pool: SimpleConnectionPool):
        """
        Initialize the stage service.
        
        Args:
            db_pool: Database connection pool for stage data operations
        """
        self.db_pool = db_pool
    
    def get_current_stage(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the current stage for a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            Dictionary containing stage information including:
            - id: Stage ID
            - name: Stage name
            - description: Stage description
            - input_template_id: ID of template for input processing
            - output_template_id: ID of template for response generation
            - next_stages: List of possible next stages
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # First get the current stage ID from the conversation
                cursor.execute(
                    "SELECT current_stage_id FROM conversations WHERE id = %s",
                    (conversation_id,)
                )
                result = cursor.fetchone()
                
                if not result or not result['current_stage_id']:
                    log.warning(f"No current stage found for conversation {conversation_id}")
                    return self._get_default_stage(cursor)
                
                stage_id = result['current_stage_id']
                
                # Now get the full stage details
                cursor.execute(
                    """
                    SELECT 
                        s.id, s.name, s.description, 
                        s.input_template_id, s.output_template_id,
                        s.config
                    FROM stages s
                    WHERE s.id = %s
                    """,
                    (stage_id,)
                )
                stage = cursor.fetchone()
                
                if not stage:
                    log.error(f"Stage with ID {stage_id} not found")
                    return self._get_default_stage(cursor)
                
                # Get next possible stages
                cursor.execute(
                    """
                    SELECT 
                        next_stage_id, condition, priority
                    FROM stage_transitions
                    WHERE current_stage_id = %s
                    ORDER BY priority DESC
                    """,
                    (stage_id,)
                )
                transitions = cursor.fetchall()
                
                # Get detailed information about next stages
                next_stages = []
                for transition in transitions:
                    cursor.execute(
                        "SELECT id, name, description FROM stages WHERE id = %s",
                        (transition['next_stage_id'],)
                    )
                    next_stage = cursor.fetchone()
                    if next_stage:
                        next_stage_info = dict(next_stage)
                        next_stage_info['condition'] = transition['condition']
                        next_stage_info['priority'] = transition['priority']
                        next_stages.append(next_stage_info)
                
                # Combine all information
                stage_info = dict(stage)
                stage_info['next_stages'] = next_stages
                
                return stage_info
                
        except Exception as e:
            log.error(f"Error getting current stage: {str(e)}")
            # Return a fallback stage in case of errors
            return {
                'id': 'error',
                'name': 'Error Stage',
                'description': 'Fallback stage due to error',
                'input_template_id': None,
                'output_template_id': None,
                'next_stages': [],
                'config': {}
            }
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def _get_default_stage(self, cursor) -> Dict[str, Any]:
        """
        Get the default initial stage.
        
        Returns:
            Dictionary containing default stage information
        """
        try:
            # First try to get the default stage from the database
            cursor.execute(
                """
                SELECT 
                    s.id, s.name, s.description, 
                    s.input_template_id, s.output_template_id,
                    s.config
                FROM stages s
                WHERE s.is_default = true
                LIMIT 1
                """
            )
            stage = cursor.fetchone()
            
            if stage:
                # Get next possible stages for the default stage
                cursor.execute(
                    """
                    SELECT 
                        next_stage_id, condition, priority
                    FROM stage_transitions
                    WHERE current_stage_id = %s
                    ORDER BY priority DESC
                    """,
                    (stage['id'],)
                )
                transitions = cursor.fetchall()
                
                # Get detailed information about next stages
                next_stages = []
                for transition in transitions:
                    cursor.execute(
                        """
                        SELECT 
                            id, name, description
                        FROM stages
                        WHERE id = %s
                        """,
                        (transition['next_stage_id'],)
                    )
                    next_stage = cursor.fetchone()
                    if next_stage:
                        next_stages.append({
                            'id': next_stage['id'],
                            'name': next_stage['name'],
                            'description': next_stage['description'],
                            'condition': transition['condition'],
                            'priority': transition['priority']
                        })
                
                return {
                    'id': stage['id'],
                    'name': stage['name'],
                    'description': stage['description'],
                    'input_template_id': stage['input_template_id'],
                    'output_template_id': stage['output_template_id'],
                    'config': stage['config'],
                    'next_stages': next_stages
                }
            
            # If no default stage found, create one
            log.warning("No default stage found, creating one...")
            default_stage_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO stages (
                    id, name, description, is_default,
                    input_template_id, output_template_id, config
                )
                VALUES (%s, %s, %s, true, %s, %s, %s)
                """,
                (
                    default_stage_id,
                    'Initial Stage',
                    'Default initial stage for new conversations',
                    None,  # input_template_id
                    None,  # output_template_id
                    json.dumps({'type': 'initial'})  # config
                )
            )
            
            return {
                'id': default_stage_id,
                'name': 'Initial Stage',
                'description': 'Default initial stage for new conversations',
                'input_template_id': None,
                'output_template_id': None,
                'config': {'type': 'initial'},
                'next_stages': []
            }
            
        except Exception as e:
            log.error(f"Error getting default stage: {str(e)}")
            # Return a hardcoded fallback stage
            return {
                'id': '00000000-0000-0000-0000-000000000000',
                'name': 'Fallback Stage',
                'description': 'Fallback stage when database access fails',
                'input_template_id': None,
                'output_template_id': None,
                'config': {'type': 'fallback'},
                'next_stages': []
            }
    
    def determine_next_stage(self, conversation_id: str, message_text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Determine the next stage based on the message and context.
        
        Args:
            conversation_id: The ID of the conversation
            message_text: The text of the current message
            context: Additional context data for evaluating stage conditions
            
        Returns:
            Dictionary containing the next stage information or None if 
            the stage should not change
        """
        current_stage = self.get_current_stage(conversation_id)
        
        # If there are no next stages defined, keep the current stage
        if not current_stage.get('next_stages'):
            return None
        
        for next_stage in current_stage.get('next_stages', []):
            # Evaluate the condition for this transition
            if self._evaluate_stage_condition(next_stage.get('condition'), message_text, context):
                # Get the full stage details for the next stage
                return self.get_stage_by_id(next_stage['id'])
        
        # If no conditions are met, keep the current stage
        return None
    
    def _evaluate_stage_condition(self, condition: str, message_text: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a stage transition condition.
        
        Args:
            condition: String representation of the condition logic
            message_text: The message text to evaluate against
            context: Additional context data for condition evaluation
            
        Returns:
            True if the condition is met, False otherwise
        """
        if not condition:
            return False
            
        try:
            # Simple keyword-based conditions
            if condition.startswith('keyword:'):
                keywords = condition[9:].split(',')
                return any(keyword.strip().lower() in message_text.lower() for keyword in keywords)
                
            # Intent-based conditions - would integrate with NLU service
            elif condition.startswith('intent:'):
                intent = condition[7:].strip()
                # This would typically call an NLU service to check intents
                # For now, implement a simple placeholder
                return intent.lower() in message_text.lower()
                
            # Entity-based conditions
            elif condition.startswith('entity:'):
                entity_check = condition[7:].strip()
                entity_type, entity_value = entity_check.split('=')
                # This would typically check entities extracted by NLU
                # For now, implement a simple placeholder
                return entity_value.lower() in message_text.lower()
                
            # Context-based conditions
            elif condition.startswith('context:'):
                context_check = condition[8:].strip()
                context_key, context_value = context_check.split('=')
                return context.get(context_key) == context_value
                
            # Python expression evaluation (limited and potentially unsafe)
            elif condition.startswith('expr:'):
                # Note: This should be used with caution as it evaluates code
                expr = condition[5:].strip()
                
                # Create a safe evaluation environment with limited variables
                eval_locals = {
                    'message': message_text,
                    'context': context,
                    'length': len,
                    'contains': lambda s, sub: sub in s,
                    'startswith': lambda s, sub: s.startswith(sub),
                    'endswith': lambda s, sub: s.endswith(sub)
                }
                
                return eval(expr, {'__builtins__': {}}, eval_locals)
                
            # Default: treat as a simple keyword check
            else:
                return condition.lower() in message_text.lower()
                
        except Exception as e:
            log.error(f"Error evaluating stage condition '{condition}': {str(e)}")
            return False
    
    def get_stage_by_id(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stage information by ID.
        
        Args:
            stage_id: The ID of the stage to retrieve
            
        Returns:
            Dictionary containing stage information or None if not found
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        s.id, s.name, s.description, 
                        s.input_template_id, s.output_template_id,
                        s.config
                    FROM stages s
                    WHERE s.id = %s
                    """,
                    (stage_id,)
                )
                stage = cursor.fetchone()
                
                if not stage:
                    log.warning(f"Stage with ID {stage_id} not found")
                    return None
                
                # Get next possible stages
                cursor.execute(
                    """
                    SELECT 
                        next_stage_id, condition, priority
                    FROM stage_transitions
                    WHERE current_stage_id = %s
                    ORDER BY priority DESC
                    """,
                    (stage_id,)
                )
                transitions = cursor.fetchall()
                
                # Get detailed information about next stages
                next_stages = []
                for transition in transitions:
                    cursor.execute(
                        "SELECT id, name, description FROM stages WHERE id = %s",
                        (transition['next_stage_id'],)
                    )
                    next_stage = cursor.fetchone()
                    if next_stage:
                        next_stage_info = dict(next_stage)
                        next_stage_info['condition'] = transition['condition']
                        next_stage_info['priority'] = transition['priority']
                        next_stages.append(next_stage_info)
                
                # Combine all information
                stage_info = dict(stage)
                stage_info['next_stages'] = next_stages
                
                return stage_info
                
        except Exception as e:
            log.error(f"Error getting stage by ID: {str(e)}")
            return None
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def update_conversation_stage(self, conversation_id: str, new_stage_id: str) -> bool:
        """
        Update the current stage of a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            new_stage_id: The ID of the new stage
            
        Returns:
            True if the update was successful, False otherwise
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversations
                    SET current_stage_id = %s, 
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (new_stage_id, conversation_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    log.info(f"Updated conversation {conversation_id} to stage {new_stage_id}")
                    return True
                else:
                    log.warning(f"Failed to update conversation {conversation_id} to stage {new_stage_id}")
                    return False
                    
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating conversation stage: {str(e)}")
            return False
        finally:
            if conn:
                self.db_pool.putconn(conn)

    @staticmethod
    def get_stage_for_message(conn, business_id: str, user_id: str, 
                             conversation_id: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Determine the appropriate stage for the current message.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            conversation_id: UUID of the conversation
            
        Returns:
            A tuple containing (stage_id, stage_selection_template_id, data_extraction_template_id, response_generation_template_id)
            or None if no stage is found
        """
        try:
            cursor = conn.cursor()
            
            # First, check if there's a stage set for this conversation
            cursor.execute(
                """
                SELECT stage_id
                FROM conversations
                WHERE conversation_id = %s
                LIMIT 1
                """,
                (conversation_id,)
            )
            
            result = cursor.fetchone()
            stage_id = result[0] if result and result[0] is not None else None
            
            # If no stage is set, get the default stage for this business
            if not stage_id:
                # Try to get the default stage first
                cursor.execute(
                    """
                    SELECT stage_id
                    FROM stages
                    WHERE business_id = %s AND stage_type = 'default'
                    LIMIT 1
                    """,
                    (business_id,)
                )
                
                result = cursor.fetchone()
                
                # If no default stage, get the first stage
                if not result:
                    cursor.execute(
                        """
                        SELECT stage_id
                        FROM stages
                        WHERE business_id = %s
                        ORDER BY created_at ASC
                        LIMIT 1
                        """,
                        (business_id,)
                    )
                    
                    result = cursor.fetchone()
                
                if not result:
                    log.warning(f"No stages found for business {business_id}")
                    return None
                
                stage_id = result[0]
                
                # Update the conversation with the new stage_id
                try:
                    cursor.execute(
                        """
                        UPDATE conversations
                        SET stage_id = %s,
                            last_updated = NOW()
                        WHERE conversation_id = %s
                        """,
                        (stage_id, conversation_id)
                    )
                    conn.commit()
                    log.info(f"Updated conversation {conversation_id} with initial stage {stage_id}")
                except Exception as e:
                    conn.rollback()
                    log.error(f"Error updating conversation stage: {str(e)}")
                    # Continue processing even if we couldn't save the stage
            
            # Get the template IDs for this stage
            cursor.execute(
                """
                SELECT stage_id, 
                       stage_selection_template_id, 
                       data_extraction_template_id, 
                       response_generation_template_id
                FROM stages
                WHERE stage_id = %s
                LIMIT 1
                """,
                (stage_id,)
            )
            
            stage_data = cursor.fetchone()
            if not stage_data:
                log.error(f"Could not find stage with ID {stage_id}")
                return None
                
            return stage_data
            
        except Exception as e:
            log.error(f"Error determining stage: {str(e)}")
            return None
    
    @staticmethod
    def transition_to_stage(conn, conversation_id: str, new_stage_id: str) -> bool:
        """
        Transition a conversation to a new stage.
        
        Args:
            conn: Database connection
            conversation_id: UUID of the conversation
            new_stage_id: UUID of the new stage
            
        Returns:
            Boolean indicating success
        """
        try:
            cursor = conn.cursor()
            
            # Mark current active stages as inactive
            cursor.execute(
                """
                UPDATE conversation_stages
                SET is_active = FALSE
                WHERE conversation_id = %s
                AND is_active = TRUE
                """,
                (conversation_id,)
            )
            
            # Create a new active stage
            cursor.execute(
                """
                INSERT INTO conversation_stages
                (conversation_id, stage_id, is_active, created)
                VALUES (%s, %s, TRUE, NOW())
                """,
                (conversation_id, new_stage_id)
            )
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            log.error(f"Error transitioning stage: {str(e)}")
            return False
    
    @staticmethod
    def get_available_stages(conn, business_id: str) -> List[Dict[str, Any]]:
        """
        Get all available stages for a business.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            
        Returns:
            List of stage dictionaries with keys: stage_id, name, description
        """
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT stage_id, name, description
                FROM stages
                WHERE business_id = %s
                ORDER BY name
                """,
                (business_id,)
            )
            
            stages = []
            for row in cursor.fetchall():
                stage_id, name, description = row
                stages.append({
                    'stage_id': stage_id,
                    'name': name,
                    'description': description
                })
            
            return stages
            
        except Exception as e:
            log.error(f"Error getting available stages: {str(e)}")
            return []