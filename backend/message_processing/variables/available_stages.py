"""
Variable provider for available conversation stages.

This module provides functionality to retrieve and format available conversation stages
for a business from the database.
"""

from typing import Dict, Any, List
from .base_provider import BaseVariableProvider
from .database_utils import DatabaseUtils
from backend.message_processing.template_variables import TemplateVariableProvider
import logging

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'available_stages',
    description='Returns a list of available conversation stages for a business',
    auth_requirement='business_key'
)
def provide_available_stages(conn, business_id: str, **kwargs) -> str:
    """
    Generate a formatted list of available stages for a business.
    
    Args:
        conn: Database connection
        business_id: ID of the business
        
    Returns:
        Formatted string with available stages
    """
    try:
        if not conn:
            log.error("No database connection provided")
            return "Error: No database connection"
            
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT stage_name, stage_description
            FROM stages 
            WHERE business_id = %s
            ORDER BY stage_name
            """,
            (business_id,)
        )
        
        stages = cursor.fetchall()
        if not stages:
            return "No stages available"
            
        result = []
        for stage in stages:
            name = stage['stage_name'] or "Unnamed Stage"
            desc = stage['stage_description'] or "No description available"
            result.append(f"{name}: {desc}")
            
        return "\n".join(result)
    except Exception as e:
        log.error(f"Error providing available_stages: {str(e)}", exc_info=True)
        return "Error retrieving available stages"