"""
Data extraction service for processing and extracting structured data from messages.

This module provides functionality for extracting specific types of data
from user messages based on predefined patterns or LLM-based extraction.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from backend.ai.llm_service import LLMService
from backend.db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

class DataExtractionService:
    """
    Service for extracting structured data from messages.
    
    This service provides methods for extracting specific types of data
    from user messages based on predefined patterns or LLM-based extraction.
    """
    
    def __init__(self, db_pool, llm_service: Optional[LLMService] = None):
        """
        Initialize the data extraction service.
        
        Args:
            db_pool: Database connection pool
            llm_service: Optional LLM service for advanced extraction
        """
        self.db_pool = db_pool
        self.llm_service = llm_service
    
    def extract_data(self, conn, extraction_template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from a message using a template.
        
        Args:
            conn: Database connection
            extraction_template_id: ID of the template to use for extraction
            context: Dictionary containing context data including:
                - message_content: The message to extract data from
                - business_id: ID of the business
                - user_id: ID of the user
                - conversation_id: ID of the conversation
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            # Get the extraction template
            template = self._get_extraction_template(conn, extraction_template_id)
            if not template:
                log.error(f"Extraction template {extraction_template_id} not found")
                return {"error": "Extraction template not found"}
            
            # Process the template with variable substitution
            processed_template = self._process_template(
                conn, template, context['business_id'], context['user_id'], 
                context['conversation_id'], context['message_content']
            )
            
            # Extract data using the appropriate method
            if self.llm_service:
                extracted_data = self._extract_with_llm(
                    context['message_content'], processed_template, context['business_id']
                )
            else:
                extracted_data = self._extract_with_patterns(
                    context['message_content'], processed_template
                )
            
            # Check for errors immediately after extraction
            if isinstance(extracted_data, dict) and 'error' in extracted_data:
                log.warning(f"Data extraction resulted in error: {extracted_data['error']}")
                # Return the error dictionary directly, possibly adding template info if needed
                extracted_data['_template_info'] = {
                    'template_id': extraction_template_id,
                    'template_content': template.get('content', ''),
                    'system_prompt': template.get('system_prompt', ''),
                    'processed_content': processed_template.get('content', ''),
                    'processed_system_prompt': processed_template.get('system_prompt', '')
                }
                return extracted_data
            
            # Store the extracted data
            self._store_extracted_data(
                conn, context['conversation_id'], template.get('template_type', 'general'),
                extracted_data
            )
            
            # Update user information if basic_info is present
            if isinstance(extracted_data, dict) and 'basic_info' in extracted_data:
                # Ensure basic_info is also a dictionary
                basic_info = extracted_data['basic_info']
                if isinstance(basic_info, dict):
                    from .user_update_service import UserUpdateService
                    user_service = UserUpdateService()
                    
                    # Map the extracted basic info to user fields
                    user_update_data = {}
                    
                    # Map full name or first/last name
                    if 'full_name' in basic_info and basic_info['full_name']:
                        names = basic_info['full_name'].split(' ', 1)
                        user_update_data['first_name'] = names[0]
                        user_update_data['last_name'] = names[1] if len(names) > 1 else ''
                    else:
                        if 'first_name' in basic_info and basic_info['first_name']:
                            user_update_data['first_name'] = basic_info['first_name']
                        if 'last_name' in basic_info and basic_info['last_name']:
                            user_update_data['last_name'] = basic_info['last_name']
                    
                    # Update user record if we have data
                    if user_update_data:
                        try:
                            # --- Add specific logging before the call ---
                            log.info(f"Attempting to update user {context['user_id']} with data: {user_update_data!r}") 
                            user_service.update_user(context['user_id'], user_update_data) 
                            log.info(f"Successfully updated user {context['user_id']}") 
                            # ----------------------------------------------
                        except Exception as e:
                            # --- Add more verbose error logging ---
                            log.error(f"Exception caught while calling user_service.update_user for user {context['user_id']}.")
                            log.exception(f"Error details: {e!r}") # Use log.exception to include stack trace
                            # --- Store the actual caught error, not the potentially misleading string ---
                            extracted_data['update_error'] = f"Failed update: {str(e)}" 
                            # --------------------------------------------------------------------
                else:
                    log.warning(f"'basic_info' key found but is not a dictionary: {type(basic_info)}. Skipping user update.")
            
            # --- FINAL CHECK before returning --- 
            final_return_value = extracted_data
            problematic_error_string = "unterminated string literal (detected at line 67) (user_update_service.py, line 67)"

            if isinstance(final_return_value, dict) and \
               final_return_value.get("error") == problematic_error_string:
                log.critical(f"!!! Intercepted problematic error string before returning: {final_return_value}")
                # Replace the misleading error with a more generic one
                final_return_value["error"] = "Data extraction failed due to an internal error (see logs for details)."
                log.critical(f"!!! Returning modified error dict: {final_return_value}")

            return final_return_value
            # --- END FINAL CHECK ---
                
        except Exception as e:
            # Log basic info first
            log.error(f"--- Exception caught in main extract_data handler ---")
            log.error(f"Exception Type: {type(e)}")
            try:
                # Try logging the repr safely
                log.error(f"Exception Repr: {e!r}")
            except Exception as log_repr_err:
                log.error(f"!!! Failed to get repr of exception: {log_repr_err}")
            try:
                # Try logging the str safely
                error_message = str(e)
                log.error(f"Exception Str: {error_message}")
            except Exception as log_str_err:
                log.error(f"!!! Failed to get str of exception: {log_str_err}")
                error_message = "Error getting exception string representation"

            # Explicitly create the error dictionary to return
            return_error = {"error": f"extract_data failed: {error_message!r}"}
            log.error(f"Returning error dictionary from main handler: {return_error}")
            return return_error
    
    def _get_extraction_template(self, conn, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an extraction template by ID.
        
        Args:
            conn: Database connection
            template_id: ID of the template
            
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
                return {
                    'template_id': row[0],
                    'template_name': row[1],
                    'template_type': row[2],
                    'content': row[3],
                    'system_prompt': row[4],
                    'business_id': row[5]
                }
            
            return None
            
        except Exception as e:
            log.error(f"Error retrieving template {template_id}: {str(e)}")
            return None
    
    def _process_template(self, conn, template: Dict[str, Any], business_id: str, 
                         user_id: str, conversation_id: str, message_content: str) -> Dict[str, Any]:
        """
        Process a template with variable substitution.
        
        Args:
            conn: Database connection
            template: Template data
            business_id: ID of the business
            user_id: ID of the user
            conversation_id: ID of the conversation
            message_content: Content of the message
            
        Returns:
            Processed template with variables substituted
        """
        from .template_variables import TemplateVariableProvider
        from .template_service import TemplateService
        
        # Build context using TemplateService
        context = TemplateService.build_context(
            conn=conn,
            business_id=business_id,
            user_id=user_id,
            conversation_id=conversation_id,
            message_content=message_content
        )
        
        # Apply template using TemplateService
        processed_template = TemplateService.apply_template(template, context)
        
        return processed_template
    
    def _extract_with_llm(self, message_content: str, template: Dict[str, Any], 
                         business_id: str) -> Dict[str, Any]:
        """
        Extract data using LLM-based extraction.
        
        Args:
            message_content: The message to extract from
            template: Processed template with content and system prompt
            business_id: ID of the business
            
        Returns:
            Dictionary with extracted data
        """
        response = None # Initialize response
        try:
            # Format the system prompt to include the template content
            formatted_system_prompt = f"{template['system_prompt']}\n\nExtract the following information:\n{template['content']}"
            
            # Log the extraction request for debugging
            log.info(f"Data extraction request: Message content: '{message_content[:100]}...' (truncated)")
            log.info(f"Data extraction template content: '{template['content'][:100]}...' (truncated)")
            log.info(f"Data extraction system prompt: '{template['system_prompt'][:100]}...' (truncated)")
            
            # Call the LLM - Wrap in try/except
            try:
                response = self.llm_service.generate_response(
                    input_text=message_content,
                    system_prompt=formatted_system_prompt,
                    business_id=business_id,
                    call_type="data_extraction"
                )
                log.info(f"LLM data extraction response: '{response[:100]}...' (truncated)")
            except Exception as llm_error:
                log.error(f"LLM service call failed during data extraction: {llm_error!r}")
                return {
                    "intent": "error",
                    "message_type": "error",
                    "error": f"LLM service error: {str(llm_error)}",
                    "prompt": template.get('content', 'Error: Template not available'),
                    "response": None # No response received
                }
            
            # Check if this is a greeting message
            greeting_patterns = [
                r'^hi\b', r'^hello\b', r'^hey\b', r'^greetings\b',
                r'^good\s+(morning|afternoon|evening)\b'
            ]
            is_greeting = any(re.match(pattern, message_content.lower()) for pattern in greeting_patterns)
            
            if is_greeting:
                result = {
                    "intent": "greeting",
                    "message_type": "greeting",
                    "raw_extraction": response,
                    "prompt": template['content'],
                    "response": response
                }
                return result
            
            # Parse the response as JSON
            try:
                extracted_data = json.loads(response)
                # Add prompt and response fields if parsing succeeds
                if isinstance(extracted_data, dict):
                    extracted_data["prompt"] = template.get('content', '')
                    extracted_data["response"] = response
                # Ensure it's a dict before returning
                return extracted_data if isinstance(extracted_data, dict) else {"raw_extraction": extracted_data}
                
            except json.JSONDecodeError:
                log.warning(f"Initial JSON parsing failed for LLM response: {response[:200]}...")
                # If not valid JSON, try to extract JSON from the text
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        extracted_data = json.loads(json_match.group(0))
                        # Add prompt and response fields
                        extracted_data["prompt"] = template['content']
                        extracted_data["response"] = response
                        return extracted_data
                    except json.JSONDecodeError:
                        log.error(f"Failed to parse JSON from LLM response: {response}")
                        return {
                            "intent": "unknown",
                            "message_type": "text",
                            "error": "LLM response was not valid JSON", # Specific error
                            "raw_extraction": response,
                            "prompt": template.get('content', ''),
                            "response": response
                        }
                else:
                    log.error(f"Failed to extract JSON from LLM response: {response}")
                    return {
                        "intent": "unknown",
                        "message_type": "text",
                        "error": "LLM response did not contain valid JSON", # Specific error
                        "raw_extraction": response,
                        "prompt": template.get('content', ''),
                        "response": response
                    }
        except Exception as e:
            # General exception handler for the whole method
            log.error(f"Unexpected error during LLM data extraction: {e!r}")
            # Safely format the error message
            error_message = repr(str(e)) # Use repr for safe representation
            return {
                "intent": "error",
                "message_type": "error",
                "error": f"Data extraction failed: {error_message}",
                "prompt": template.get('content', 'Error: Template not available'),
                "response": f"Error during extraction: {error_message}"
            }
    
    def _extract_with_patterns(self, message_content: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data using simple pattern matching rules.
        
        Args:
            message_content: The message to extract from
            template: Processed template with content
            
        Returns:
            Dictionary with extracted data
        """
        result = {}
        
        # Simple pattern: field_name: pattern
        pattern_lines = template['content'].strip().split('\n')
        for line in pattern_lines:
            if ':' in line:
                field_name, pattern = line.split(':', 1)
                field_name = field_name.strip()
                pattern = pattern.strip()
                
                # Try to find the pattern in the message
                match = re.search(pattern, message_content, re.IGNORECASE)
                if match:
                    result[field_name] = match.group(1) if match.groups() else match.group(0)
        
        return result
    
    def _store_extracted_data(self, conn, conversation_id: str, data_type: str, 
                             extracted_data: Dict[str, Any]) -> str:
        """
        Store extracted data in the database.
        
        Args:
            conn: Database connection
            conversation_id: ID of the conversation
            data_type: Type of data extracted
            extracted_data: Data to store
            
        Returns:
            ID of the stored extraction
        """
        try:
            cursor = conn.cursor()
            
            # Get the current stage ID from the conversation
            cursor.execute(
                """
                SELECT stage_id FROM conversations WHERE conversation_id = %s
                """,
                (conversation_id,)
            )
            
            result = cursor.fetchone()
            if not result or not result['stage_id']:
                log.warning(f"No current stage found for conversation {conversation_id}")
                return None
            
            stage_id = result['stage_id']
            
            # Insert the extracted data
            cursor.execute(
                """
                INSERT INTO extracted_data 
                (conversation_id, stage_id, data_type, extracted_data, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING extraction_id
                """,
                (conversation_id, stage_id, data_type, json.dumps(extracted_data), datetime.now())
            )
            
            extraction_id = cursor.fetchone()['extraction_id']
            conn.commit()
            
            return extraction_id
            
        except Exception as e:
            # --- Add detailed logging ---
            log.error(f"--- Exception caught in _store_extracted_data ---")
            log.error(f"Args: conversation_id={conversation_id!r}, data_type={data_type!r}")
            try:
                 # Try logging data safely (truncate if too long)
                 data_str = json.dumps(extracted_data)
                 log.error(f"Data attempted to store: {data_str[:200]}{'...' if len(data_str) > 200 else ''}")
            except Exception as log_data_err:
                 log.error(f"!!! Failed to serialize or log extracted_data: {log_data_err}")
            log.exception(f"Error details: {e!r}") # Log full stack trace
            # -----------------------------
            conn.rollback()
            # Still return None as before, but log details first
            return None
    
    def get_extracted_data(self, conversation_id: str, data_type: Optional[str] = None, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve extracted data for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            data_type: Optional filter by data type
            limit: Maximum number of records to return
            
        Returns:
            List of extracted data records
        """
        conn = self.db_pool.getconn()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT ed.extraction_id, ed.stage_id, ed.data_type, 
                       ed.extracted_data, ed.created_at, s.stage_name
                FROM extracted_data ed
                JOIN stages s ON ed.stage_id = s.stage_id
                WHERE ed.conversation_id = %s
            """
            
            params = [conversation_id]
            
            if data_type:
                query += " AND ed.data_type = %s"
                params.append(data_type)
                
            query += " ORDER BY ed.created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Format the results
            extracted_data = []
            for row in results:
                extracted_data.append({
                    'extraction_id': row['extraction_id'],
                    'stage_id': row['stage_id'],
                    'stage_name': row['stage_name'],
                    'data_type': row['data_type'],
                    'data': row['extracted_data'],
                    'created_at': row['created_at'].isoformat()
                })
            
            return extracted_data
            
        except Exception as e:
            log.error(f"Error retrieving extracted data: {str(e)}")
            return []
        finally:
            self.db_pool.putconn(conn)