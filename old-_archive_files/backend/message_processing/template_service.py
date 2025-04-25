"""
Template service for message processing.

This module handles the retrieval and application of templates used in 
the different stages of message processing.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set

# Import the variable provider system
from .template_variables import TemplateVariableProvider

# Import standard variables to ensure they're registered
from . import standard_variables

log = logging.getLogger(__name__)

class TemplateService:
    """
    Service for managing and applying templates during message processing.
    
    Handles template retrieval, variable substitution, and context building
    for the different stages of message processing.
    """
    
    @staticmethod
    def get_template(conn, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a template by ID.
        
        Args:
            conn: Database connection
            template_id: UUID of the template
            
        Returns:
            Template data as a dictionary or None if not found
        """
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT template_id, template_name, template_type, content, 
                       system_prompt, business_id
                FROM templates
                WHERE template_id = %s
                """,
                (template_id,)
            )
            
            row = cursor.fetchone()
            if row:
                template_id, template_name, template_type, content, system_prompt, business_id = row
                
                # Extract variables from template content
                variables = TemplateVariableProvider.extract_variables_from_template(content)
                system_variables = TemplateVariableProvider.extract_variables_from_template(system_prompt or '')
                
                # Combine all unique variables
                all_variables = variables.union(system_variables)
                
                return {
                    'template_id': template_id,
                    'template_name': template_name,
                    'template_type': template_type,
                    'content': content,
                    'system_prompt': system_prompt or '',
                    'business_id': business_id,
                    'variables': list(all_variables)
                }
            
            return None
            
        except Exception as e:
            log.error(f"Error retrieving template {template_id}: {str(e)}")
            return None
    
    @staticmethod
    def apply_template(template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply template with variable substitution.
        
        Args:
            template: Template object with content and metadata
            context: Context dictionary with variable values
            
        Returns:
            Dictionary with processed template content and system prompt
        """
        try:
            content = template['content']
            system_prompt = template.get('system_prompt', '')
            
            # Get variables from template if available, otherwise extract them
            variables = set(template.get('variables', []))
            if not variables:
                content_vars = TemplateVariableProvider.extract_variables_from_template(content)
                system_vars = TemplateVariableProvider.extract_variables_from_template(system_prompt)
                variables = content_vars.union(system_vars)
            
            # Apply variable substitution
            if content and variables:
                # Log variable info for debugging
                log.debug(f"Template variables: {variables}")
                log.debug(f"Context keys: {context.keys()}")
                
                # Process each variable
                for var_name in variables:
                    # Get the variable value from context
                    var_value = context.get(var_name, f"[Missing: {var_name}]")
                    var_value_str = str(var_value)
                    
                    # Replace double curly braces first (to avoid conflicts)
                    double_placeholder = f"{{{{{var_name}}}}}"
                    if double_placeholder in content:
                        content = content.replace(double_placeholder, var_value_str)
                        
                    if system_prompt and double_placeholder in system_prompt:
                        system_prompt = system_prompt.replace(double_placeholder, var_value_str)
                    
                    # Then replace single curly braces
                    single_placeholder = f"{{{var_name}}}"
                    if single_placeholder in content:
                        content = content.replace(single_placeholder, var_value_str)
                        
                    if system_prompt and single_placeholder in system_prompt:
                        system_prompt = system_prompt.replace(single_placeholder, var_value_str)
            
            return {
                'content': content,
                'system_prompt': system_prompt
            }
            
        except Exception as e:
            log.error(f"Error applying template: {str(e)}")
            return {
                'content': template.get('content', ''),
                'system_prompt': template.get('system_prompt', '')
            }
    
    @staticmethod
    def build_context(conn, business_id: str, user_id: str, conversation_id: str, message_content: str) -> Dict[str, Any]:
        """
        Build context for template substitution.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            conversation_id: UUID of the conversation
            message_content: Content of the current message
            
        Returns:
            Dictionary containing context variables
        """
        try:
            # Get business and user info for basic context
            cursor = conn.cursor()
            
            # Get business info
            cursor.execute(
                """
                SELECT business_name, business_description 
                FROM businesses 
                WHERE business_id = %s
                """,
                (business_id,)
            )
            result = cursor.fetchone()
            business_name = result['business_name'] if result else ''
            business_description = result['business_description'] if result else ''
            
            # Get user info
            cursor.execute(
                """
                SELECT first_name, last_name, email 
                FROM users 
                WHERE user_id = %s
                """,
                (user_id,)
            )
            result = cursor.fetchone()
            user_info = {
                'first_name': result['first_name'] if result else '',
                'last_name': result['last_name'] if result else '',
                'email': result['email'] if result else ''
            }
            
            # Get conversation history
            cursor.execute(
                """
                SELECT message_content, sender_type, created_at 
                FROM messages 
                WHERE conversation_id = %s 
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            messages = cursor.fetchall()
            
            # Build conversation history
            conversation_history = []
            for msg in messages:
                conversation_history.append({
                    'content': msg['message_content'],
                    'sender': msg['sender_type'],
                    'timestamp': msg['created_at'].isoformat() if msg['created_at'] else ''
                })
            
            # Build basic context
            context = {
                'business': {
                    'name': business_name,
                    'description': business_description
                },
                'user': user_info,
                'conversation': {
                    'id': conversation_id,
                    'history': conversation_history
                },
                'current_message': message_content,
                'user_message': message_content
            }
            
            # Generate dynamic variable values using the provider system
            dynamic_variables = TemplateVariableProvider.generate_variable_values(
                conn=conn,
                business_id=business_id,
                user_id=user_id,
                conversation_id=conversation_id,
                message_content=message_content
            )
            
            # Merge dynamic variables with basic context
            context.update(dynamic_variables)
            
            return context
            
        except Exception as e:
            log.error(f"Error building context: {str(e)}")
            # Return minimal context on error
            basic_context = {
                'business': {'name': '', 'description': ''},
                'user': {'first_name': '', 'last_name': '', 'email': ''},
                'conversation': {'id': conversation_id, 'history': []},
                'current_message': message_content
            }
            
            # Try to get at least the critical variables even in error case
            try:
                critical_vars = {'stage_list', 'summary_of_last_conversations', 'N'}
                error_vars = TemplateVariableProvider.generate_variable_values(
                    conn=conn,
                    business_id=business_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_content=message_content,
                    template_vars=critical_vars
                )
                basic_context.update(error_vars)
            except Exception as inner_e:
                log.error(f"Error generating critical variables: {str(inner_e)}")
                # Set fallback values
                basic_context.update({
                    'stage_list': '[]',
                    'summary_of_last_conversations': 'Error retrieving conversation history',
                    'N': '0'
                })
                
            return basic_context