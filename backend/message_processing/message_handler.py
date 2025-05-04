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
from backend.message_processing.ai_control_service import ai_control_service

log = logging.getLogger(__name__)

class MessageHandler:
    """
    Handler for processing incoming messages.
    
    Coordinates the message processing flow by working with various services
    to determine the current stage, apply appropriate templates, and generate responses.
    """
    
    # In-memory storage for process logs
    _process_logs = {}
    
    # In-memory storage for stop flags per conversation
    _stop_flags = {}
    
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
    
    def stop_ai_responses(self, conversation_id: str) -> None:
        """
        Stop AI from generating responses for a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation to stop
        """
        self._stop_flags[conversation_id] = True
        log.info(f"AI responses stopped for conversation {conversation_id}")
    
    def resume_ai_responses(self, conversation_id: str) -> None:
        """
        Resume AI response generation for a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation to resume
        """
        self._stop_flags[conversation_id] = False
        log.info(f"AI responses resumed for conversation {conversation_id}")
    
    def is_ai_stopped(self, conversation_id: str) -> bool:
        """
        Check if AI responses are stopped for a conversation.
        
        Args:
            conversation_id: The ID of the conversation to check
            
        Returns:
            bool: True if AI responses are stopped, False otherwise
        """
        return self._stop_flags.get(conversation_id, False)
    
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
            # Validate required fields
            if not all([message_data.get('business_id'), 
                       message_data.get('user_id'), 
                       message_data.get('content')]):
                self._store_process_log(log_id, {
                    'status': 'error',
                    'error': "Missing required fields: business_id, user_id, content",
                    'timestamp': datetime.now().isoformat()
                })
                return {
                    'success': False,
                    'error': "Missing required fields: business_id, user_id, content"
                }

            # Check if AI responses are stopped for this user
            if ai_control_service.is_ai_stopped(None, message_data['user_id']):
                log.info(f"AI responses are stopped for user {message_data['user_id']}")
                return {
                    'success': True,
                    'response': None,
                    'conversation_id': None,
                    'message_id': None,
                    'response_id': None,
                    'process_log_id': log_id,
                    'processing_steps': processing_steps,
                    'ai_stopped': True
                }

            conn = self.db_pool.getconn()
            try:
                # Get or create conversation
                conversation_id = self._get_or_create_conversation(
                    conn, 
                    message_data['business_id'], 
                    message_data['user_id'],
                    message_data.get('conversation_id')
                )
                
                # Check if AI responses are stopped for this conversation
                if ai_control_service.is_ai_stopped(conversation_id, None):
                    log.info(f"AI responses are stopped for conversation {conversation_id}")
                    return {
                        'success': True,
                        'response': None,
                        'conversation_id': conversation_id,
                        'message_id': None,
                        'response_id': None,
                        'process_log_id': log_id,
                        'processing_steps': processing_steps,
                        'ai_stopped': True
                    }

                # If we have a conversation_id in the message data, check if it's different from the one we got
                if message_data.get('conversation_id') and message_data['conversation_id'] != conversation_id:
                    # Check if AI is stopped for the original conversation
                    if ai_control_service.is_ai_stopped(message_data['conversation_id'], None):
                        log.info(f"AI responses are stopped for original conversation {message_data['conversation_id']}")
                        return {
                            'success': True,
                            'response': None,
                            'conversation_id': message_data['conversation_id'],
                            'message_id': None,
                            'response_id': None,
                            'process_log_id': log_id,
                            'processing_steps': processing_steps,
                            'ai_stopped': True
                        }
                
                # Generate a new llm_call_id for this message
                llm_call_id = str(uuid.uuid4())
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE conversations SET llm_call_id = %s WHERE conversation_id = %s
                    """,
                    (llm_call_id, conversation_id)
                )
                conn.commit()
                log.info(f"Using llm_call_id {llm_call_id} for conversation {conversation_id}")
                
                # Get current stage and templates
                stage_info = self.stage_service.get_stage_for_message(
                    conn,
                    message_data['business_id'],
                    message_data['user_id'],
                    conversation_id
                )
                
                if not stage_info:
                    self._store_process_log(log_id, {
                        'status': 'error',
                        'error': "No valid stage found for message",
                        'timestamp': datetime.now().isoformat()
                    })
                    return {
                        'success': False,
                        'error': "No valid stage found for message"
                    }
                
                stage_id, selection_template_id, extraction_template_id, response_template_id = stage_info
                
                # Build context for template substitution
                context = {
                    'business_id': message_data['business_id'],
                    'user_id': message_data['user_id'],
                    'conversation_id': conversation_id,
                    'message_content': message_data['content'],
                    'stage_id': stage_id,
                    'llm_call_id': llm_call_id
                }
                
                # Generate values for template variables
                variable_values = TemplateVariableProvider.generate_variable_values(
                    conn=conn,
                    business_id=message_data['business_id'],
                    user_id=message_data['user_id'],
                    conversation_id=conversation_id,
                    message_content=message_data['content']
                )
                context.update(variable_values)
                
                # Step 1: Stage Selection (Intent Detection)
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
                            business_id=message_data['business_id'],
                            call_type="intent",
                            llm_call_id=llm_call_id,
                            available_stages=self._get_available_stages(conn, message_data['business_id'])
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
                        if stage_response and len(stage_response.strip()) > 0:
                            log.info(f"Stage detection response: {stage_response}")
                            
                            # Query available stages to match against response
                            cursor.execute(
                                """
                                SELECT stage_id, stage_name 
                                FROM stages 
                                WHERE business_id = %s
                                """,
                                (message_data['business_id'],)
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
                            
                            if detected_stage_id:
                                # Update conversation with new stage
                                cursor.execute(
                                    """
                                    UPDATE conversations 
                                    SET stage_id = %s 
                                    WHERE conversation_id = %s
                                    """,
                                    (detected_stage_id, conversation_id)
                                )
                                conn.commit()
                                log.info(f"Updated conversation {conversation_id} to stage {detected_stage_id}")
                                
                                # Get new templates for the detected stage
                                stage_info = self.stage_service.get_stage_for_message(
                                    conn,
                                    message_data['business_id'],
                                    message_data['user_id'],
                                    conversation_id
                                )
                                if stage_info:
                                    stage_id, selection_template_id, extraction_template_id, response_template_id = stage_info
                                    log.info(f"Updated stage info: stage_id={stage_id}, templates={[selection_template_id, extraction_template_id, response_template_id]}")
                
                # Step 2: Data Extraction
                if extraction_template_id:
                    extraction_template = self.template_service.get_template(conn, extraction_template_id)
                    if extraction_template:
                        applied_template = self.template_service.apply_template(extraction_template, context)
                        extraction_input = applied_template['content']
                        extraction_system_prompt = applied_template.get('system_prompt', '')
                        
                        # Extract data using LLM
                        extracted_data = self.llm_service.generate_response(
                            input_text=extraction_input,
                            system_prompt=extraction_system_prompt,
                            conversation_id=conversation_id,
                            business_id=message_data['business_id'],
                            call_type="extraction",
                            llm_call_id=llm_call_id
                        )
                        
                        # Add data extraction step to processing steps
                        processing_steps.append({
                            'step': 'data_extraction',
                            'template_id': extraction_template_id,
                            'template_name': extraction_template.get('template_name', 'Unknown'),
                            'prompt': extraction_input,
                            'response': extracted_data,
                            'system_prompt': extraction_system_prompt,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Update context with extracted data
                        try:
                            extracted_data_dict = json.loads(extracted_data)
                            context.update(extracted_data_dict)
                            log.info(f"Updated context with extracted data: {extracted_data_dict}")
                        except json.JSONDecodeError:
                            log.warning(f"Could not parse extracted data as JSON: {extracted_data}")
                
                # Step 3: Response Generation
                if not response_template_id:
                    self._store_process_log(log_id, {
                        'status': 'error',
                        'error': "No response template found",
                        'timestamp': datetime.now().isoformat()
                    })
                    return {
                        'success': False,
                        'error': "No response template found"
                    }
                
                # Save messages
                message_id = self._save_message(
                    conn,
                    conversation_id,
                    message_data['content'],
                    message_data.get('sender_type', 'user'),  # Use sender_type from message_data if provided
                    message_data['user_id']
                )
                
                # Only generate and save AI response if the message is from a regular user
                sender_type = message_data.get('sender_type', 'user')
                if sender_type == 'user':  # Only generate response for user messages
                    response_template = self.template_service.get_template(conn, response_template_id)
                    if not response_template:
                        self._store_process_log(log_id, {
                            'status': 'error',
                            'error': "Response template not found",
                            'timestamp': datetime.now().isoformat()
                        })
                        return {
                            'success': False,
                            'error': "Response template not found"
                        }
                    
                    applied_template = self.template_service.apply_template(response_template, context)
                    response_input = applied_template['content']
                    response_system_prompt = applied_template.get('system_prompt', '')
                    
                    # Generate response using LLM
                    response = self.llm_service.generate_response(
                        input_text=response_input,
                        system_prompt=response_system_prompt,
                        conversation_id=conversation_id,
                        business_id=message_data['business_id'],
                        call_type="response",
                        llm_call_id=llm_call_id
                    )
                    
                    # Add response generation step to processing steps
                    processing_steps.append({
                        'step': 'response_generation',
                        'template_id': response_template_id,
                        'template_name': response_template.get('template_name', 'Unknown'),
                        'prompt': response_input,
                        'response': response,
                        'system_prompt': response_system_prompt,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Save AI response
                    response_id = self._save_message(
                        conn,
                        conversation_id,
                        response,
                        'assistant'
                    )
                else:
                    response = None
                    response_id = None
                
                # Update conversation timestamp
                self._update_conversation_timestamp(conn, conversation_id)
                
                # Commit the transaction
                conn.commit()
                
                # Store final success log
                self._store_process_log(log_id, {
                    'status': 'completed',
                    'response': response,
                    'conversation_id': conversation_id,
                    'message_id': message_id,
                    'response_id': response_id,
                    'stage_id': stage_id,
                    'processing_steps': processing_steps,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'response': response,
                    'conversation_id': conversation_id,
                    'message_id': message_id,
                    'response_id': response_id,
                    'process_log_id': log_id,
                    'processing_steps': processing_steps
                }
                
            except Exception as e:
                log.error(f"Error processing message: {str(e)}", exc_info=True)
                self._store_process_log(log_id, {
                    'status': 'error',
                    'error': str(e),
                    'processing_steps': processing_steps,
                    'timestamp': datetime.now().isoformat()
                })
                return {
                    'success': False,
                    'error': str(e),
                    'process_log_id': log_id
                }
            
            finally:
                self.db_pool.putconn(conn)

        except Exception as outer_e:
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
    
    def _get_or_create_conversation(self, conn, business_id: str, user_id: str, 
                                  conversation_id: Optional[str] = None) -> str:
        """Get existing conversation or create a new one."""
        cursor = conn.cursor()
        
        try:
            # First, check if the user exists
            cursor.execute(
                """
                SELECT user_id FROM users WHERE user_id = %s
                """,
                (user_id,)
            )
            if not cursor.fetchone():
                # User doesn't exist, create them
                cursor.execute(
                    """
                    INSERT INTO users (
                        user_id, first_name, last_name, email, created_at
                    )
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (user_id, 'NEW', 'User', f'auto-{user_id}@example.com')
                )
                log.info(f"Created new user: {user_id}")
            
            if conversation_id:
                # Verify the conversation exists
                cursor.execute(
                    """
                    SELECT conversation_id FROM conversations WHERE conversation_id = %s
                    """,
                    (conversation_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    return conversation_id
                else:
                    log.info(f"Conversation {conversation_id} not found, creating new one")
            
            # Create a new conversation
            new_conversation_id = str(uuid.uuid4())
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
                (new_conversation_id, business_id, user_id, session_id, llm_call_id)
            )
            
            log.info(f"Created new conversation: {new_conversation_id}")
            return new_conversation_id
            
        except Exception as e:
            log.error(f"Error in _get_or_create_conversation: {str(e)}")
            raise
    
    def _save_message(self, conn, conversation_id: str, content: str, 
                     sender_type: str, user_id: str = None) -> str:
        """Save a message to the database."""
        cursor = conn.cursor()
        message_id = str(uuid.uuid4())
        try:
            cursor.execute(
                """
                INSERT INTO messages (message_id, conversation_id, message_content, sender_type, user_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING message_id
                """,
                (message_id, conversation_id, content, sender_type, user_id)
            )
            message_id = cursor.fetchone()[0]
            log.info(f"Saved message {message_id} for conversation {conversation_id}")
            return message_id
        except Exception as e:
            log.error(f"Error saving message: {str(e)}")
            raise
    
    def _update_conversation_timestamp(self, conn, conversation_id: str) -> None:
        """Update the conversation's last updated timestamp."""
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE conversations
            SET last_updated = CURRENT_TIMESTAMP
            WHERE conversation_id = %s
            """,
            (conversation_id,)
        )
    
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