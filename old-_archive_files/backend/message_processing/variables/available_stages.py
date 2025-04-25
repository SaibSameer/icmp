"""
Available stages variable provider.
"""
import logging
from ..template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider('available_stages')
def provide_available_stages(conn, business_id: str, **kwargs) -> str:
    """
    Get list of available stage names with descriptions.
    
    Args:
        conn: Database connection
        business_id: UUID of the business
        
    Returns:
        Formatted string with stage names and descriptions
    """
    try:
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
            log.info(f"No stages found for business_id: {business_id}")
            return "Default Conversation Stage"
            
        # Handle both tuple and dictionary row formats
        stage_info = []
        for stage in stages:
            if isinstance(stage, dict):
                # If using RealDictCursor, access by column name
                stage_name = stage['stage_name']
                stage_desc = stage['stage_description']
            else:
                # If using regular cursor, access by index
                stage_name = stage[0]
                stage_desc = stage[1]
                
            stage_info.append(f"{stage_name}: {stage_desc}")
                
        result = "\n".join(stage_info)
        log.info(f"Found stages for business_id {business_id}")
        return result
        
    except Exception as e:
        log.error(f"Error providing available_stages: {str(e)}", exc_info=True)
        return "Default Conversation Stage"