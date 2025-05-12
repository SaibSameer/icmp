"""
LLM Service for handling AI model interactions.
"""

import logging
import os
from typing import Dict, Any, Optional
import openai
from datetime import datetime

log = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Language Learning Models."""
    
    def __init__(self, db_pool):
        """
        Initialize the LLM service.
        
        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.api_key = os.getenv('LLM_API_KEY')
        self.api_endpoint = os.getenv('LLM_API_ENDPOINT', 'https://api.openai.com/v1')
        self.model = os.getenv('LLM_MODEL', 'gpt-4')
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        
        # Configure OpenAI client
        openai.api_key = self.api_key
        openai.api_base = self.api_endpoint
        
        log.info(f"LLM Service initialized with model: {self.model}")
    
    async def generate_response(
        self,
        template: str,
        message_content: str,
        extracted_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            template: Response template
            message_content: User's message content
            extracted_data: Optional extracted data from the message
            
        Returns:
            Generated response text
        """
        try:
            # Prepare the prompt
            prompt = self._prepare_prompt(template, message_content, extracted_data)
            
            # Generate response
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract and return the response
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            log.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def _prepare_prompt(
        self,
        template: str,
        message_content: str,
        extracted_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Prepare the prompt for the LLM.
        
        Args:
            template: Response template
            message_content: User's message content
            extracted_data: Optional extracted data
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Template: {template}\n"
        prompt += f"User Message: {message_content}\n"
        
        if extracted_data:
            prompt += f"Extracted Data: {extracted_data}\n"
        
        prompt += "Please generate a response based on the template and context above."
        return prompt
    
    async def validate_response(self, response: str) -> bool:
        """
        Validate the generated response.
        
        Args:
            response: Generated response to validate
            
        Returns:
            True if response is valid, False otherwise
        """
        if not response or len(response.strip()) == 0:
            return False
            
        # Add any additional validation rules here
        return True 