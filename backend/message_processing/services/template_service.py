"""
Template Service

This module provides template management functionality, including template creation,
retrieval, and processing.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from ..errors import (
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
    DatabaseError
)

logger = logging.getLogger(__name__)

class TemplateService:
    """Manages message templates."""
    
    def __init__(self, db_pool, redis_manager):
        """Initialize template service.
        
        Args:
            db_pool: Database connection pool
            redis_manager: Redis state manager
        """
        self.db_pool = db_pool
        self.redis_manager = redis_manager
        
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template data
            
        Raises:
            TemplateNotFoundError: If template not found
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                SELECT t.*, b.name as business_name
                FROM templates t
                JOIN businesses b ON t.business_id = b.business_id
                WHERE t.template_id = %s
                """,
                (template_id,)
            )
            
            template = cursor.fetchone()
            if not template:
                raise TemplateNotFoundError(f"Template {template_id} not found")
                
            return dict(template)
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to get template: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def process_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Process template with variables.
        
        Args:
            template_id: Template ID
            variables: Variables to use in template
            
        Returns:
            Processed template content
            
        Raises:
            TemplateNotFoundError: If template not found
            TemplateError: If processing fails
        """
        try:
            # Get template
            template = self.get_template(template_id)
            
            # Get template content
            content = template['content']
            
            # Replace variables
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in content:
                    content = content.replace(placeholder, str(var_value))
            
            return content
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error processing template {template_id}: {str(e)}")
            raise TemplateError(f"Failed to process template: {str(e)}")
    
    def list_templates(self, business_id: str) -> List[Dict[str, Any]]:
        """List templates for business.
        
        Args:
            business_id: Business ID
            
        Returns:
            List of templates
            
        Raises:
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                SELECT t.*, b.name as business_name
                FROM templates t
                JOIN businesses b ON t.business_id = b.business_id
                WHERE t.business_id = %s
                ORDER BY t.created_at DESC
                """,
                (business_id,)
            )
            
            templates = cursor.fetchall()
            return [dict(t) for t in templates]
            
        except Exception as e:
            logger.error(f"Error listing templates for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to list templates: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def create_template(self, business_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new template.
        
        Args:
            business_id: Business ID
            template_data: Template data
            
        Returns:
            Created template data
            
        Raises:
            TemplateValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Validate template data
            if not template_data.get('name') or not template_data.get('content'):
                raise TemplateValidationError("Template name and content are required")
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                INSERT INTO templates (
                    template_id, business_id, name, content, variables,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, NOW(), NOW()
                ) RETURNING *
                """,
                (
                    template_data.get('template_id'),
                    business_id,
                    template_data['name'],
                    template_data['content'],
                    template_data.get('variables', [])
                )
            )
            
            template = cursor.fetchone()
            conn.commit()
            
            return dict(template)
            
        except TemplateValidationError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating template: {str(e)}")
            raise DatabaseError(f"Failed to create template: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update template.
        
        Args:
            template_id: Template ID
            template_data: Template data to update
            
        Returns:
            Updated template data
            
        Raises:
            TemplateNotFoundError: If template not found
            TemplateValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Check if template exists
            self.get_template(template_id)
            
            # Validate template data
            if not template_data.get('name') or not template_data.get('content'):
                raise TemplateValidationError("Template name and content are required")
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                UPDATE templates
                SET name = %s,
                    content = %s,
                    variables = %s,
                    updated_at = NOW()
                WHERE template_id = %s
                RETURNING *
                """,
                (
                    template_data['name'],
                    template_data['content'],
                    template_data.get('variables', []),
                    template_id
                )
            )
            
            template = cursor.fetchone()
            conn.commit()
            
            return dict(template)
            
        except TemplateNotFoundError:
            raise
        except TemplateValidationError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error updating template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to update template: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def delete_template(self, template_id: str) -> None:
        """Delete template.
        
        Args:
            template_id: Template ID
            
        Raises:
            TemplateNotFoundError: If template not found
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Check if template exists
            self.get_template(template_id)
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM templates WHERE template_id = %s",
                (template_id,)
            )
            
            conn.commit()
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete template: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn) 