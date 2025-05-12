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
    auth_requirement='business_key'
)
def provide_agent_stages(conn, agent_id: str = None, **kwargs) -> Optional[List[Dict]]:
    """
    Fetch stages associated with a specific agent.
    
    Args:
        conn: Database connection
        agent_id: Optional. The ID of the agent to fetch stages for. If not provided, uses the current agent ID from context.
        **kwargs: Additional context parameters
        
    Returns:
        List of dictionaries containing stage information, or None if error occurs
    """
    if not agent_id:
        log.error("No agent_id provided")
        return None
        
    try:
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