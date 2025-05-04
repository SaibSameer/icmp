"""
Variable provider for fetching stages associated with a specific agent.
"""

import logging
from typing import Dict, List, Optional
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'agent_stages',
    description="Returns a list of stages associated with a specific agent",
    example_value=[
        {
            "stage_id": "123e4567-e89b-12d3-a456-426614174000",
            "stage_name": "Initial Contact",
            "stage_description": "First contact with the customer",
            "stage_type": "conversation",
            "created_at": "2023-01-01T00:00:00"
        }
    ],
    category='agent',
    is_dynamic=True
)
class AgentStagesVariable:
    """Variable provider for agent-specific stages."""
    
    @classmethod
    def get_variable_name(cls) -> str:
        """Get the name of this variable provider."""
        return "agent_stages"
    
    @classmethod
    def get_variable_description(cls) -> str:
        """Get the description of this variable provider."""
        return "Returns a list of stages associated with a specific agent"
    
    @classmethod
    def get_variable_parameters(cls) -> Dict[str, str]:
        """Get the parameters required by this variable provider."""
        return {
            "agent_id": "Optional. The ID of the agent to fetch stages for. If not provided, uses the current agent ID from context."
        }
    
    @classmethod
    def provide_variable(cls, params: Dict[str, str], context: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Fetch stages associated with a specific agent.
        
        Args:
            params: Dictionary containing parameters
                - agent_id: Optional. The ID of the agent to fetch stages for
            context: Dictionary containing the current context
                - agent_id: The ID of the current agent
        
        Returns:
            List of dictionaries containing stage information, or None if error occurs
        """
        # Get agent_id from params or context
        agent_id = params.get("agent_id")
        if not agent_id and context:
            agent_id = context.get("agent_id")
        
        if not agent_id:
            log.error("No agent_id provided in parameters or context")
            return None
            
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query to get stages associated with the agent
            cursor.execute("""
                SELECT 
                    s.stage_id,
                    s.stage_name,
                    s.stage_description,
                    s.stage_type,
                    s.created_at
                FROM stages s
                WHERE s.agent_id = %s
                ORDER BY s.created_at DESC
            """, (agent_id,))
            
            stages = []
            for row in cursor.fetchall():
                stages.append({
                    "stage_id": row[0],
                    "stage_name": row[1],
                    "stage_description": row[2],
                    "stage_type": row[3],
                    "created_at": row[4].isoformat() if row[4] else None
                })
            
            return stages
            
        except Exception as e:
            log.error(f"Error fetching agent stages: {str(e)}")
            return None
            
        finally:
            if conn:
                release_db_connection(conn)
    
    @classmethod
    def get_variable_example(cls) -> str:
        """Get an example of how to use this variable."""
        return """
        Example usage in template:
        # Using current agent from context
        {% for stage in agent_stages() %}
            Stage: {{ stage.stage_name }}
            Description: {{ stage.stage_description }}
            Type: {{ stage.stage_type }}
        {% endfor %}
        
        # Using specific agent ID
        {% for stage in agent_stages(agent_id="specific-agent-id") %}
            Stage: {{ stage.stage_name }}
            Description: {{ stage.stage_description }}
            Type: {{ stage.stage_type }}
        {% endfor %}
        """ 