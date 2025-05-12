"""
Template management system for handling message templates.
"""

import logging
from typing import Dict, Any, Optional
from backend.database.db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

class TemplateManager:
    """Manages message templates and their rendering."""
    
    @staticmethod
    def render(template_id: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_id: UUID of the template to render
            context: Dictionary of variables to use in rendering
            
        Returns:
            Rendered template string
            
        Raises:
            ValueError: If template not found or rendering fails
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get template content
            cursor.execute(
                """
                SELECT content
                FROM templates
                WHERE template_id = %s
                """,
                (template_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"Template not found: {template_id}")
                
            template_content = result[0]
            
            # Simple variable replacement
            # TODO: Implement more sophisticated template engine
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in template_content:
                    template_content = template_content.replace(placeholder, str(value))
            
            return template_content
            
        except Exception as e:
            log.error(f"Error rendering template {template_id}: {str(e)}")
            raise ValueError(f"Template rendering failed: {str(e)}")
        finally:
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def get_template(template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template details by ID.
        
        Args:
            template_id: UUID of the template
            
        Returns:
            Dictionary with template details or None if not found
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT template_id, name, content, business_id, created_at
                FROM templates
                WHERE template_id = %s
                """,
                (template_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return {
                'template_id': str(result[0]),
                'name': result[1],
                'content': result[2],
                'business_id': str(result[3]),
                'created_at': result[4].isoformat()
            }
            
        except Exception as e:
            log.error(f"Error getting template {template_id}: {str(e)}")
            return None
        finally:
            if conn:
                release_db_connection(conn) 