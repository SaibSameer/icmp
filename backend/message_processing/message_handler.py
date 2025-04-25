"""
Message handler for processing incoming messages.

This module handles the orchestration of message processing,
utilizing the StageService and TemplateService to determine the
appropriate processing flow and apply templates.
"""

import logging
import uuid
import re
import json
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from backend.ai.llm_service import LLMService
from backend.db import get_db_connection, release_db_connection, execute_query
from backend.message_processing.template_variables import TemplateVariableProvider
from backend.message_processing.stage_service import StageService
from backend.message_processing.template_service import TemplateService
from backend.message_processing.data_extraction_service import DataExtractionService

log = logging.getLogger(__name__)

class MessageHandler:
    """
    Handler for processing incoming messages.
    
    Coordinates the message processing flow by working with various services
    to determine the current stage, apply appropriate templates, and generate responses.
    """
    
    # In-memory storage for process logs
    _process_logs = {}
    
    def __init__(self, db_pool, llm_service: LLMService = None):
        """
        Initialize the message handler.
        
        Args:
            db_pool: Database connection pool
            llm_service: Optional LLM service instance for generating responses
        """
        self.db_pool = db_pool
        self.llm_service = llm_service or LLMService()
        self.stage_service = StageService(db_pool)
        self.template_service = TemplateService()
        self.data_extraction_service = DataExtractionService(db_pool, self.llm_service)
    
    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        Args:
            message_data: Dictionary containing message data
            
        Returns:
            Dictionary containing the response
        """
        log_id = str(uuid.uuid4())
        processing_steps = []  # Initialize processing_steps at the start
        self._store_process_log(log_id, {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message_data': message_data
        })
        
        try:
            # Extract required fields
            business_id = message_data.get('business_id')
            user_id = message_data.get('user_id')
            content = message_data.get('content')
            conversation_id = message_data.get('conversation_id')
            api_key = message_data.get('api_key')
            owner_id = message_data.get('owner_id')
            
            # Validate required fields
            if not all([business_id, user_id, content]):
                self._store_process_log(log_id, {
                    'status': 'error',
                    'error': "Missing required fields: business_id, user_id, content",
                    'timestamp': datetime.now().isoformat()
                })
                return {
                    'success': False,
                    'error': "Missing required fields: business_id, user_id, content"
                }
            
            # Get a connection from the pool
            conn = self.db_pool.getconn()
            
            try:
                # --- Start Transaction ---
                # conn.autocommit is set to False by get_db_connection

                # Check if the conversation exists
                cursor = conn.cursor()
                if conversation_id:
                    # Verify the conversation exists
                    cursor.execute(
                        """
                        SELECT conversation_id FROM conversations WHERE conversation_id = %s
                        """,
                        (conversation_id,)
                    )
                    result = cursor.fetchone()
                    
                    if not result:
                        # Conversation doesn't exist, create it
                        log.info(f"Conversation {conversation_id} not found, creating it")
                        session_id = str(uuid.uuid4())
                        llm_call_id = str(uuid.uuid4())
                        
                        cursor.execute(
                            """
                            INSERT INTO conversations (
                                conversation_id, business_id, user_id, session_id, 
                                start_time, last_updated, status, llm_call_id
                            )
                            VALUES (%s, %s, %s, %s, NOW(), NOW(), 'active', %s)
                            """,
                            (conversation_id, business_id, user_id, session_id, llm_call_id)
                        )
                        log.info(f"Created conversation: {conversation_id}")
                    else:
                        log.info(f"Using existing conversation: {conversation_id}")
                else:
                    # No conversation_id provided, create a new one or find an existing one
                    conversation_id = self._create_conversation(conn, business_id, user_id)
                    log.info(f"Using conversation: {conversation_id}")
                
                # Get the llm_call_id for this conversation
                cursor.execute(
                    """
                    SELECT llm_call_id FROM conversations WHERE conversation_id = %s
                    """,
                    (conversation_id,)
                )
                result = cursor.fetchone()
                llm_call_id = result[0] if result else None
                
                # Always generate a new llm_call_id for each message to avoid context issues
                llm_call_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    UPDATE conversations SET llm_call_id = %s WHERE conversation_id = %s
                    """,
                    (llm_call_id, conversation_id)
                )
                
                log.info(f"Using llm_call_id {llm_call_id} for conversation {conversation_id}")
                
                # Get current stage and templates
                stage_result = self.get_stage_for_message(conn, user_id, conversation_id, business_id)
                current_stage, selection_template_id, extraction_template_id, response_template_id = stage_result
                
                # Build context for template substitution
                context = {
                    'user_message': content,
                    'business_id': business_id,
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'current_stage': current_stage,
                    'llm_call_id': llm_call_id
                }
                
                # Generate values for template variables
                variable_values = TemplateVariableProvider.generate_variable_values(
                    conn=conn,
                    business_id=business_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_content=content
                )
                context.update(variable_values)
                
                # Step 1: Stage Selection (Intent Detection) using previous stage's template
                stage_response = None
                if selection_template_id:
                    selection_template = self.template_service.get_template(conn, selection_template_id)
                    if selection_template:
                        applied_template = self.template_service.apply_template(selection_template, context)
                        selection_input = applied_template['content']
                        selection_system_prompt = applied_template.get('system_prompt', '')
                        
                        # Generate stage selection response using LLM
                        stage_response = self.llm_service.generate_response(
                            input_text=selection_input,
                            system_prompt=selection_system_prompt,
                            conversation_id=conversation_id,
                            agent_id=api_key,
                            call_type="intent",  # Specify this is an intent detection call
                            business_id=business_id,  # Add business_id for saving calls
                            llm_call_id=llm_call_id,  # Use the same llm_call_id for all calls
                            available_stages=self._get_available_stages(conn, business_id)  # Add available stages
                        )
                        
                        # Add intent detection step to processing steps
                        processing_steps.append({
                            'step': 'intent_detection',
                            'template_id': selection_template_id,
                            'template_name': selection_template.get('template_name', 'Unknown'),
                            'prompt': selection_input,
                            'response': stage_response,
                            'system_prompt': selection_system_prompt,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Use the stage response to update the conversation's stage
                        try:
                            # First, check if the response contains a stage name
                            if stage_response and len(stage_response.strip()) > 0:
                                log.info(f"Stage detection response: {stage_response}")
                                
                                # Query available stages to match against response
                                cursor = conn.cursor()
                                cursor.execute(
                                    """
                                    SELECT stage_id, stage_name 
                                    FROM stages 
                                    WHERE business_id = %s
                                    """,
                                    (business_id,)
                                )
                                available_stages = cursor.fetchall()
                                
                                # Enhanced matching - find the stage name in the response
                                detected_stage_id = None
                                stage_response_lower = stage_response.lower()
                                
                                # Method 1: Direct substring match (case insensitive)
                                for stage in available_stages:
                                    stage_id = stage[0]
                                    stage_name = stage[1].lower()
                                    
                                    if stage_name in stage_response_lower:
                                        detected_stage_id = stage_id
                                        log.info(f"Detected stage by direct match: {stage[1]} (ID: {stage_id})")
                                        break
                                
                                # Method 2: If no direct match, try to find stage name at word boundaries
                                if not detected_stage_id:
                                    for stage in available_stages:
                                        stage_id = stage[0]
                                        stage_name = stage[1].lower()
                                        
                                        # Look for stage name as a whole word
                                        pattern = r'\b' + re.escape(stage_name) + r'\b'
                                        if re.search(pattern, stage_response_lower):
                                            detected_stage_id = stage_id
                                            log.info(f"Detected stage by word boundary: {stage[1]} (ID: {stage_id})")
                                            break
                                
                                # Method 3: Check for stage names with confidence levels
                                if not detected_stage_id:
                                    # Look for patterns like "Stage: Discovery (90% confidence)"
                                    for stage in available_stages:
                                        stage_id = stage[0]
                                        stage_name = stage[1].lower()
                                        
                                        # Check for stage name followed by confidence indicator
                                        confidence_pattern = stage_name + r'.*?(\d+)[%\s]*(confidence|certainty)'
                                        match = re.search(confidence_pattern, stage_response_lower)
                                        if match:
                                            detected_stage_id = stage_id
                                            confidence = match.group(1)
                                            log.info(f"Detected stage with confidence: {stage[1]} ({confidence}%) (ID: {stage_id})")
                                            break
                                
                                # Log raw stage response for debugging
                                log.info(f"Raw stage detection response: {stage_response}")
                                
                                # If a stage was detected, update the conversation
                                if detected_stage_id:
                                    log.info(f"Updating conversation {conversation_id} stage to {detected_stage_id}")
                                    cursor = conn.cursor()
                                    cursor.execute(
                                        """
                                        UPDATE conversations 
                                        SET stage_id = %s, last_updated = NOW() 
                                        WHERE conversation_id = %s
                                        """,
                                        (detected_stage_id, conversation_id)
                                    )
                                    current_stage = detected_stage_id  # Update local variable
                                    log.info(f"Conversation {conversation_id} stage updated successfully.")
                                else:
                                    log.warning(f"No matching stage found for response: {stage_response}")
                        except Exception as stage_update_error:
                            log.error(f"Error updating stage based on LLM response: {stage_update_error}", exc_info=True)
                            # Do not commit here, let the main transaction handle it
                
                # Step 2: Data Extraction using new stage's template
                extracted_data = ""
                if extraction_template_id:
                    extraction_template = self.template_service.get_template(conn, extraction_template_id)
                    if extraction_template:
                        # Use the data extraction service instead of direct LLM call
                        extracted_data = self.data_extraction_service.extract_data(
                            message_content=content,
                            extraction_template_id=extraction_template_id,
                            business_id=business_id,
                            user_id=user_id,
                            conversation_id=conversation_id
                        )
                        
                        # Add data extraction step to processing steps
                        extraction_step = {
                            'step': 'data_extraction',
                            'template_id': extraction_template_id,
                            'template_name': extraction_template.get('template_name', 'Unknown'),
                            'extracted_data': extracted_data,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Get the extraction template content and system prompt for UI display
                        if extraction_template:
                            applied_template = self.template_service.apply_template(extraction_template, context)
                            extraction_input = applied_template.get('content', '')
                            extraction_system_prompt = applied_template.get('system_prompt', '')
                            
                            # Add these to the processing step
                            extraction_step['prompt'] = extraction_input
                            extraction_step['system_prompt'] = extraction_system_prompt
                            
                            # For the response, we'll convert the extracted_data to a formatted string
                            if isinstance(extracted_data, dict):
                                extraction_step['response'] = json.dumps(extracted_data, indent=2)
                            else:
                                extraction_step['response'] = str(extracted_data)
                        
                        # Add the extraction step to processing steps
                        processing_steps.append(extraction_step)
                        
                        # Add extracted data to context for response generation
                        context['extracted_data'] = extracted_data
                
                # Step 3: Response Generation using new stage's template
                # Prepare response input and system prompt
                response_input = content  # Default to original message content
                response_system_prompt = ""  # Default to empty system prompt
                
                # Get and apply response template if available
                if response_template_id:
                    response_template = self.template_service.get_template(conn, response_template_id)
                    if response_template:
                        applied_template = self.template_service.apply_template(response_template, context)
                        response_input = applied_template['content']
                        response_system_prompt = applied_template.get('system_prompt', '')
                
                # Generate final response
                final_response = self.llm_service.generate_response(
                    input_text=response_input,
                    system_prompt=response_system_prompt,
                    conversation_id=conversation_id,
                    agent_id=api_key,
                    call_type="response",  # Specify this is a response generation call
                    business_id=business_id,  # Add business_id for saving calls
                    llm_call_id=llm_call_id  # Use the same llm_call_id for all calls
                )
                
                # Add response generation step to processing steps
                processing_steps.append({
                    'step': 'response_generation',
                    'template_id': response_template_id,
                    'template_name': response_template.get('template_name', 'Unknown'),
                    'prompt': response_input,
                    'response': final_response,
                    'system_prompt': response_system_prompt,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Get and apply output template if available
                processed_output = final_response
                
                if response_template_id:
                    # Add LLM response to context
                    context['llm_response'] = final_response
                    
                    # IMPORTANT: We don't want to apply the template to the response that we store in the database
                    # Output template only applies to the contextual metadata seen in the UI/frontend
                    # We store the actual LLM response in the database
                    output_template = self.template_service.get_template(conn, response_template_id)
                    if output_template:
                        # Store the original final_response as what gets saved in the database
                        processed_output = final_response
                
                # Save user message and AI response to the database
                # Save user message first
                message_id = self._save_message(
                    conn, 
                    conversation_id=conversation_id,
                    content=content,
                    sender_type='user',
                    user_id=user_id
                )
                
                # Save AI response - using the actual LLM response (final_response), not the processed template
                response_message_id = self._save_message(
                    conn, 
                    conversation_id=conversation_id,
                    content=final_response,
                    sender_type='ai',
                    user_id=user_id
                )
                
                # Get current timestamp for response
                current_time = datetime.now()
                
                # --- Commit Transaction ---
                conn.commit()
                log.info(f"Transaction committed successfully for conversation {conversation_id}")

                # Store final success log after commit
                self._store_process_log(log_id, {
                    'status': 'completed',
                    'response': final_response,
                    'conversation_id': conversation_id,
                    'message_id': message_id,
                    'response_id': response_message_id,
                    'stage_id': current_stage,
                    'processing_steps': processing_steps,
                    'timestamp': current_time.isoformat()
                })
                
                # Return the response
                return {
                    "response": final_response,  # Return the actual LLM response not the processed template
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "response_id": response_message_id,
                    "created_at": current_time.isoformat(),
                    "process_log_id": log_id,
                    "success": True,
                    "processing_steps": processing_steps
                }
                
            except Exception as e:
                # --- Rollback Transaction ---
                log.error(f"Error during message processing for conversation {conversation_id}. Rolling back transaction. Error: {str(e)}", exc_info=True)
                if conn:
                    try:
                        conn.rollback()
                        log.info("Transaction rolled back successfully.")
                    except Exception as rb_err:
                        log.error(f"Error during rollback: {rb_err}", exc_info=True)
                
                # Store error log
                self._store_process_log(log_id, {
                    'status': 'error',
                    'error': str(e),
                    'processing_steps': processing_steps, # Log steps up to the error
                    'timestamp': datetime.now().isoformat()
                })
                
                # Return error response
                return {
                    'success': False,
                    'error': f"Error processing message: {str(e)}",
                    'process_log_id': log_id # Include log ID for debugging
                }
            
            finally:
                # Return the connection to the pool
                if conn:
                    self.db_pool.putconn(conn)
                    log.debug("Database connection returned to pool.")

        except Exception as outer_e: # Catch errors before getting connection
            log.error(f"Outer error in process_message: {str(outer_e)}", exc_info=True)
            self._store_process_log(log_id, {
                'status': 'error',
                'error': f"Outer error: {str(outer_e)}",
                'timestamp': datetime.now().isoformat()
            })
            return {
                'success': False,
                'error': f"Outer error: {str(outer_e)}",
                'process_log_id': log_id
            }
    
    def _create_conversation(self, conn, business_id: str, user_id: str) -> str:
        """
        Create a new conversation or find an existing active one for the user and business.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            
        Returns:
            UUID of the conversation (new or existing)
        """
        try:
            # First, check if there's an existing active conversation for this user and business
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT conversation_id, status 
                FROM conversations 
                WHERE business_id = %s AND user_id = %s
                ORDER BY last_updated DESC
                LIMIT 1
                """,
                (business_id, user_id)
            )
            
            result = cursor.fetchone()
            if result:
                conversation_id, status = result
                # If the conversation is active, use it
                if status == 'active':
                    log.info(f"Using existing active conversation: {conversation_id}")
                    
                    # Update the last_updated timestamp
                    cursor.execute(
                        """
                        UPDATE conversations 
                        SET last_updated = NOW() 
                        WHERE conversation_id = %s
                        """,
                        (conversation_id,)
                    )
                    
                    return conversation_id
                else:
                    # If the conversation is inactive, create a new one
                    log.info(f"Existing conversation {conversation_id} is inactive, creating new conversation")
            
            # Create a new conversation
            conversation_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())  # Generate a unique session ID
            llm_call_id = str(uuid.uuid4())  # Generate a unique LLM call ID
            
            cursor.execute(
                """
                INSERT INTO conversations (
                    conversation_id, business_id, user_id, session_id, 
                    start_time, last_updated, status, llm_call_id
                )
                VALUES (%s, %s, %s, %s, NOW(), NOW(), 'active', %s)
                """,
                (conversation_id, business_id, user_id, session_id, llm_call_id)
            )
            log.info(f"New conversation created in DB: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            log.error(f"Error creating conversation: {str(e)}")
            # Generate a new conversation ID even if there's an error
            return str(uuid.uuid4())
    
    def _save_message(self, conn, conversation_id: str, content: str, 
                     sender_type: str, user_id: str = None) -> str:
        """
        Save a message to the database.
        
        Args:
            conn: Database connection
            conversation_id: UUID of the conversation
            content: Message content
            sender_type: Type of sender ('user' or 'ai')
            user_id: UUID of the user (optional)
            
        Returns:
            UUID of the created message
        """
        try:
            message_id = str(uuid.uuid4())
            cursor = conn.cursor()
            
            # Get user_id from conversation if not provided
            if user_id is None:
                cursor.execute(
                    """
                    SELECT user_id FROM conversations WHERE conversation_id = %s
                    """,
                    (conversation_id,)
                )
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                else:
                    log.error(f"Could not find user_id for conversation {conversation_id}")
                    raise ValueError(f"Could not find user_id for conversation {conversation_id}")
            
            # Map 'assistant' to 'ai' for database compatibility
            if sender_type == 'assistant':
                sender_type = 'ai'
            
            # Save the message
            cursor.execute(
                """
                INSERT INTO messages (
                    message_id, conversation_id, user_id, message_content, 
                    sender_type, created_at
                )
                VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (message_id, conversation_id, user_id, content, sender_type)
            )
            log.info(f"Message saved: ID={message_id}, Conversation={conversation_id}, Sender={sender_type}")
            return message_id
        except Exception as e:
            log.error(f"Error saving message: {str(e)}")
            raise

    def get_stage_for_message(self, conn, user_id: str, conversation_id: str, business_id: str) -> Tuple[str, str, str, str]:
        """
        Get the appropriate stage for a message.
        
        Args:
            conn: Database connection
            user_id: UUID of the user
            conversation_id: UUID of the conversation
            business_id: UUID of the business
            
        Returns:
            Tuple containing (stage_id, selection_template_id, extraction_template_id, response_template_id)
        """
        try:
            cursor = conn.cursor()
            
            # First check if there's a stage set for this conversation
            cursor.execute(
                """
                SELECT stage_id FROM conversations 
                WHERE conversation_id = %s
                """,
                (conversation_id,)
            )
            result = cursor.fetchone()
            stage_id = result[0] if result and result[0] else None
            
            # If no stage is set, get the first stage for this business
            if not stage_id:
                cursor.execute(
                    """
                    SELECT stage_id FROM stages 
                    WHERE business_id = %s 
                    ORDER BY created_at ASC 
                    LIMIT 1
                    """,
                    (business_id,)
                )
                result = cursor.fetchone()
                if result:
                    stage_id = result[0]
                    # Update conversation with the new stage
                    cursor.execute(
                        """
                        UPDATE conversations 
                        SET stage_id = %s 
                        WHERE conversation_id = %s
                        """,
                        (stage_id, conversation_id)
                    )
            
            # Get template IDs for this stage
            if stage_id:
                cursor.execute(
                    """
                    SELECT stage_id, 
                           stage_selection_template_id, 
                           data_extraction_template_id, 
                           response_generation_template_id
                    FROM stages 
                    WHERE stage_id = %s
                    """,
                    (stage_id,)
                )
                result = cursor.fetchone()
                if result:
                    return (
                        result[0],  # stage_id
                        result[1],  # stage_selection_template_id
                        result[2],  # data_extraction_template_id
                        result[3]   # response_generation_template_id
                    )
            
            # If no stage found, return None values
            return None, None, None, None
            
        except Exception as e:
            log.error(f"Error getting stage for message: {str(e)}")
            return None, None, None, None 

    @classmethod
    def _store_process_log(cls, log_id: str, log_data: Dict[str, Any]) -> None:
        """Store a process log in the in-memory storage."""
        cls._process_logs[log_id] = log_data

    @classmethod
    def get_process_log(cls, log_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a process log by ID."""
        return cls._process_logs.get(log_id)

    @classmethod
    def get_recent_process_logs(cls, business_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent process logs for a business."""
        business_logs = [
            log for log in cls._process_logs.values()
            if log.get('business_id') == business_id
        ]
        return sorted(
            business_logs,
            key=lambda x: x.get('start_time', ''),
            reverse=True
        )[:limit]

    def _get_stage_name(self, conn, stage_id):
        """Get the name of a stage by its ID."""
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT stage_name FROM stages WHERE stage_id = %s
                """,
                (stage_id,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            return "Unknown Stage"
        except Exception as e:
            log.error(f"Error getting stage name: {str(e)}")
            return "Unknown Stage"

    def _get_available_stages(self, conn, business_id: str) -> List[str]:
        """
        Get list of available stage names for a business.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            
        Returns:
            List of stage names
        """
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT stage_name 
                FROM stages 
                WHERE business_id = %s
                ORDER BY created_at ASC
                """,
                (business_id,)
            )
            # Extract stage names from results
            stages = [row[0] for row in cursor.fetchall()]
            if not stages:
                # Include default stage if no stages found
                stages = ["Default Conversation Stage"]
            return stages
        except Exception as e:
            log.error(f"Error getting available stages: {str(e)}")
            return ["Default Conversation Stage"]

    def validate_stage_selection_response(self, response: str) -> str:
        """Validate and clean the stage selection response."""
        if not response:
            log.warning("Empty stage selection response, defaulting to 'not_sure'")
            return "not_sure"
        
        # Clean the response
        cleaned_response = response.strip().lower()
        log.debug(f"Cleaned stage selection response: '{cleaned_response}'")
        
        # List of valid stages with aliases
        valid_stages = {
            "default": ["default", "default conversation", "default stage", "initial"],
            "introduction": ["intro", "introduction", "greeting", "welcome"],
            "products": ["product", "products", "catalog", "offering"],
            "not_sure": ["not sure", "unclear", "unknown", "unsure"],
            "test": ["test", "testing", "debug"]
        }
        
        # Try to match the response against stage names and their aliases
        for stage, aliases in valid_stages.items():
            for alias in aliases:
                if alias in cleaned_response:
                    log.info(f"Matched stage '{stage}' via alias '{alias}' in response: '{cleaned_response}'")
                    return stage
        
        # If no match found, try to extract any stage-like words
        words = cleaned_response.split()
        for word in words:
            for stage, aliases in valid_stages.items():
                if any(alias.startswith(word) for alias in aliases):
                    log.info(f"Partial match found for stage '{stage}' from word '{word}'")
                    return stage
        
        # If still no match, check if response contains any stage-related keywords
        stage_keywords = {
            "default": ["conversation", "general", "basic"],
            "introduction": ["hello", "hi", "hey", "greet"],
            "products": ["buy", "purchase", "price", "cost"],
            "not_sure": ["help", "confused", "what", "how"],
            "test": ["check", "verify", "testing"]
        }
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in cleaned_response for keyword in keywords):
                log.info(f"Matched stage '{stage}' via keyword in response: '{cleaned_response}'")
                return stage
        
        # If no valid stage found, log extensively and return default
        log.warning(f"No valid stage match found in response: '{response}'")
        log.warning("Original response content length: %d", len(response))
        log.warning("Cleaned response content length: %d", len(cleaned_response))
        log.warning("Words in cleaned response: %s", words)
        
        return "not_sure"

    def _generate_conversation_summary(self, messages: List[Dict], business_id: str) -> str:
        """Generate a summary of the conversation using the LLM service."""
        try:
            # Format messages for summary generation
            formatted_messages = []
            for msg in messages:
                role = "assistant" if msg["is_from_agent"] else "user"
                formatted_messages.append({
                    "role": role,
                    "content": msg["content"]
                })
            
            # Generate summary using LLM service
            summary_prompt = """Please analyze this conversation and provide a structured summary with the following sections:
1. Overview: A brief summary of the main topic and purpose
2. Key Points: Important information discussed
3. Decisions: Any decisions made or agreements reached
4. Pending Items: Topics that need follow-up
5. Next Steps: Recommended actions
6. Sentiment: Overall tone of the conversation
7. Confidence Score: How confident you are in this summary (0-1)

Format the response as a JSON object with these exact keys."""

            summary = self.llm_service.generate_response(
                business_id=business_id,
                input_text=json.dumps(formatted_messages),
                system_prompt=summary_prompt,
                call_type="summary"
            )
            
            # Validate that the summary is valid JSON
            try:
                json.loads(summary)  # This will raise an error if the JSON is invalid
                return summary  # Return the JSON string if valid
            except json.JSONDecodeError:
                # If the summary is not valid JSON, create a basic structure
                basic_summary = {
                    "overview": "Unable to generate structured summary",
                    "key_points": [],
                    "decisions": [],
                    "pending_items": [],
                    "next_steps": [],
                    "sentiment": "neutral",
                    "confidence_score": 0.0
                }
                return json.dumps(basic_summary)
            
        except Exception as e:
            log.error(f"Error generating conversation summary: {str(e)}")
            return None

    def _update_conversation(self, conversation_id: str, business_id: str, user_id: str, 
                            content: str, is_from_agent: bool, stage_id: Optional[str] = None,
                            llm_call_id: Optional[str] = None) -> None:
        """Update conversation with new message and generate summary if needed."""
        conn = None
        try:
            conn = self.db_pool.getconn()
            cur = conn.cursor()
            
            # Save the message
            cur.execute("""
                INSERT INTO messages (conversation_id, business_id, user_id, content, is_from_agent)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING message_id
            """, (conversation_id, business_id, user_id, content, is_from_agent))
            
            # Update conversation's last_updated and status
            cur.execute("""
                UPDATE conversations 
                SET last_updated = CURRENT_TIMESTAMP,
                    status = 'active',
                    stage_id = COALESCE(%s, stage_id)
                WHERE conversation_id = %s
            """, (stage_id, conversation_id))
            
            # Get all messages for this conversation
            cur.execute("""
                SELECT content, is_from_agent
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at
            """, (conversation_id,))
            
            messages = [{"content": row[0], "is_from_agent": row[1]} for row in cur.fetchall()]
            
            # Generate summary if we have enough messages (e.g., every 5 messages)
            if len(messages) % 5 == 0:
                summary = self._generate_conversation_summary(messages, business_id)
                if summary:
                    # Store the summary as JSON
                    cur.execute("""
                        UPDATE conversations
                        SET conversation_summary = %s
                        WHERE conversation_id = %s
                    """, (summary, conversation_id))
            
            conn.commit()
            
        except Exception as e:
            log.error(f"Error updating conversation: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.db_pool.putconn(conn)