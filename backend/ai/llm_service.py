"""
LLM Service for handling language model interactions.

This module provides functionality for interacting with language models,
including generating responses, managing conversations, and handling
various types of LLM calls.
"""

import logging
import json
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
from backend.db import get_db_connection, release_db_connection, CONNECTION_POOL

log = logging.getLogger(__name__)

class LLMService:
    """
    Service for generating responses using language models.
    
    Provides methods for generating responses using various language models,
    with support for different agents and conversation contexts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Optional API key for the language model service
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            log.warning("No API key provided for LLM service")
        else:
            self.client = OpenAI(api_key=self.api_key)
        # Store for conversation histories - only used for response generation
        self._conversation_store: Dict[str, List[Dict[str, str]]] = {}
        
        # Initialize database connection pool
        self.db_pool = CONNECTION_POOL
        log.info("LLMService initialized with database connection pool")
        
        # Log database connection pool status
        try:
            conn = self.db_pool.getconn()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    log.info("Database connection pool is working correctly")
                else:
                    log.error("Database connection pool test query failed")
            else:
                log.error("Failed to get connection from pool during initialization")
        except Exception as e:
            log.error(f"Error testing database connection pool: {str(e)}", exc_info=True)
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def _save_llm_call(self, business_id: str, input_text: str, response: str, 
                      system_prompt: str, call_type: str, conversation_id: str = None,
                      llm_call_id: Optional[str] = None) -> None:
        """
        Save an LLM call to the database.
        
        Args:
            business_id: UUID of the business
            input_text: Input text sent to the LLM
            response: Response received from the LLM
            system_prompt: System prompt used for the call
            call_type: Type of call (e.g., 'intent', 'extraction', 'response')
            conversation_id: UUID of the conversation (optional)
            llm_call_id: Optional LLM call ID to use for tracking (if provided, will be used for all calls in the conversation)
        """
        # Validate required fields
        if not business_id:
            log.error("Cannot save LLM call: business_id is required")
            return
            
        # Clean up input_text if it's "[Missing: message]"
        if input_text == "[Missing: message]":
            input_text = "No input text provided"
            log.warning("Input text was [Missing: message], using default text")
            
        if not input_text:
            input_text = "Empty input"
            log.warning("Input text was empty, using default text")
            
        if not response:
            log.error("Cannot save LLM call: response is required")
            return
            
        conn = None
        cursor = None
        try:
            log.info(f"Saving LLM call: type={call_type}, conversation_id={conversation_id}, llm_call_id={llm_call_id}")
            log.debug(f"Input text: {input_text[:100]}...")  # Log first 100 chars of input
            log.debug(f"Response: {response[:100]}...")  # Log first 100 chars of response
            
            conn = get_db_connection()
            if not conn:
                log.error("Failed to get database connection")
                return
                
            cursor = conn.cursor()
            
            # Always generate a new call_id for each LLM call
            call_id = str(uuid.uuid4())
            log.info(f"Generated new call_id for LLM call: {call_id}")
            
            # If conversation_id is provided, update the conversation's llm_call_id
            # This is used for tracking purposes but doesn't affect the individual call IDs
            # Note: This is now managed in the message_handler to prevent reusing the same llm_call_id
            
            # Insert new record with the unique call_id
            cursor.execute(
                """
                INSERT INTO llm_calls (
                    call_id, business_id, input_text, response, 
                    system_prompt, call_type, timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (call_id, business_id, input_text, response, system_prompt, call_type)
            )
            log.info(f"Created new LLM call record with call_id: {call_id}")
            
            # Commit all changes in a single transaction
            conn.commit()
            log.info(f"Successfully saved LLM call with call_id: {call_id}")
            log.info(f"Saved LLM call with call_type={call_type}, conversation_id={conversation_id}")
                
        except Exception as e:
            log.error(f"Error saving LLM call: {str(e)}", exc_info=True)
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    log.error(f"Error rolling back transaction: {str(rollback_error)}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    log.error(f"Error closing cursor: {str(e)}")
            if conn:
                try:
                    release_db_connection(conn)
                except Exception as e:
                    log.error(f"Error releasing connection: {str(e)}")
    
    def generate_response(self, input_text: str, system_prompt: str = "", 
                         conversation_id: Optional[str] = None,
                         agent_id: Optional[str] = None,
                         call_type: str = "response",
                         available_stages: Optional[List[str]] = None,
                         business_id: Optional[str] = None,
                         llm_call_id: Optional[str] = None) -> str:
        """
        Generate a response using the OpenAI language model.
        
        Args:
            input_text: The input text to generate a response for
            system_prompt: Optional system prompt to guide the model
            conversation_id: Optional conversation ID for context
            agent_id: Optional agent ID to use for response generation
            call_type: Type of call - "intent", "extraction", or "response"
            available_stages: List of available stage names for intent detection
            business_id: UUID of the business (required for saving calls)
            llm_call_id: Optional LLM call ID to use for tracking (if provided, will be used for all calls in the conversation)
            
        Returns:
            The generated response text
        """
        try:
            # Log the request
            log.info(f"Generating {call_type} response for conversation {conversation_id}, agent {agent_id}")
            
            if not self.api_key:
                log.error("No OpenAI API key available")
                return "Error: OpenAI API key not configured"
            
            # Prepare the messages for the API
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                # Default system prompts based on call type
                if call_type == "intent":
                    intent_prompt = (
                        "You are a stage classifier. Your task is to select ONE stage name from the available stages list "
                        "that best matches the user's message. You must ONLY respond with the exact stage name - no other text. "
                        "If unsure, choose 'Default Conversation Stage'."
                    )
                    messages.append({"role": "system", "content": intent_prompt})
                elif call_type == "extraction":
                    messages.append({"role": "system", "content": "You are a data extractor. Extract key information from the input in a structured format."})
                else:
                    messages.append({"role": "system", "content": "You are a helpful assistant."})
            
            # Only include conversation history for response generation
            if call_type == "response" and conversation_id:
                # Fetch conversation history from database
                conn = self.db_pool.getconn()
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT message_content, sender_type = 'ai' as is_from_ai
                        FROM messages
                        WHERE conversation_id = %s
                        ORDER BY created_at ASC
                        LIMIT 10
                    """, (conversation_id,))
                    
                    history = cursor.fetchall()
                    for msg in history:
                        role = "assistant" if msg[1] else "user"
                        messages.append({"role": role, "content": msg[0]})
                    
                    log.info(f"Included {len(history)} messages from conversation history for {conversation_id}")
                finally:
                    self.db_pool.putconn(conn)
            
            # For intent detection, format the input to include available stages
            if call_type == "intent" and available_stages:
                formatted_input = (
                    f"Available stages:\n"
                    f"{', '.join(available_stages)}\n\n"
                    f"User message: {input_text}\n\n"
                    f"Select exactly one stage name from the above list."
                )
                messages.append({"role": "user", "content": formatted_input})
            else:
                # Add the current user message as is for other call types
                messages.append({"role": "user", "content": input_text})
            
            # Set temperature based on call type
            temperature = 0.0 if call_type == "intent" else 0.3 if call_type == "extraction" else 0.7
            
            # Call the OpenAI API
            log.info(f"Calling OpenAI API for {call_type} with temperature {temperature}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can adjust to gpt-4 or other models
                messages=messages,
                temperature=temperature,  # Lower temperature for more deterministic responses
                max_tokens=500
            )
            
            # Extract the response text
            assistant_message = response.choices[0].message.content
            log.info(f"Received response from OpenAI API for {call_type} (length: {len(assistant_message)})")
            
            # Save the call to the database if business_id is available
            if business_id:
                try:
                    # If business_id is not provided but conversation_id is, try to get business_id from the conversation
                    if not business_id and conversation_id:
                        conn = self.db_pool.getconn()
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                SELECT business_id FROM conversations WHERE conversation_id = %s
                                """,
                                (conversation_id,)
                            )
                            result = cursor.fetchone()
                            if result and result[0]:
                                business_id = result[0]
                                log.info(f"Retrieved business_id {business_id} from conversation {conversation_id}")
                        finally:
                            self.db_pool.putconn(conn)
                    
                    if business_id:
                        # Always save the LLM call with a unique call_id
                        self._save_llm_call(
                            business_id=business_id,
                            input_text=input_text,
                            response=assistant_message,
                            system_prompt=system_prompt,
                            call_type=call_type,
                            conversation_id=conversation_id,
                            llm_call_id=llm_call_id
                        )
                        log.info(f"Saved LLM call with call_type={call_type}, conversation_id={conversation_id}")
                    else:
                        log.warning("Could not determine business_id for saving LLM call")
                except Exception as e:
                    log.error(f"Failed to save LLM call: {str(e)}", exc_info=True)
                    # Continue execution even if saving fails
            else:
                log.warning(f"Not saving LLM call: business_id is required but not provided")
            
            # For intent detection, ensure we only return the stage name
            if call_type == "intent":
                # Clean up the response to only include the stage name
                assistant_message = assistant_message.strip().split('\n')[0].strip()
                # Remove any common prefixes/suffixes that might be added
                assistant_message = assistant_message.replace('Stage:', '').replace('stage:', '').strip()
                assistant_message = assistant_message.split('(')[0].strip()  # Remove confidence levels if present
                
                # Validate the response is one of the available stages
                if available_stages and assistant_message not in available_stages:
                    assistant_message = "Default Conversation Stage"
            
            return assistant_message
                
        except Exception as e:
            log.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear the conversation history for a given conversation ID.
        
        Args:
            conversation_id: The ID of the conversation to clear
        """
        if conversation_id in self._conversation_store:
            del self._conversation_store[conversation_id]
            log.info(f"Cleared conversation history for {conversation_id}")