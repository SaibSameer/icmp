# backend/openai_helper.py
import openai
import logging
import os
from dotenv import load_dotenv
from backend.template_management import TemplateManager
from backend.database.db import get_db_connection, release_db_connection
from backend.config import Config

load_dotenv()

log = logging.getLogger(__name__)


def render_prompt(template_id: str, context: dict) -> str:
    """Generate ready-to-use prompt"""
    try:
        if template_id:
           return TemplateManager.render(template_id, context)
        return "Default prompt" #return default if there is no template ID
    except Exception as e:
        raise ValueError(f"Prompt rendering failed: {str(e)}")

def call_openai(prompt):
    """Call OpenAI API with the given prompt. Returns a mock response if the API call fails."""
    try:
        # Get the API key from environment variables
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            log.warning("OPENAI_API_KEY not set in environment variables. Using mock response.")
            return f"This is a mock response to: '{prompt[:50]}...'. API key not configured."
        
        # Check if the API key is properly formatted (should start with "sk-")
        if not api_key.startswith('sk-'):
            log.warning("OPENAI_API_KEY appears to be invalid (should start with 'sk-'). Using mock response.")
            return f"This is a mock response to: '{prompt[:50]}...'. API key format is invalid."
        
        # Create a client instance with the API key
        client = openai.OpenAI(api_key=api_key)
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Return the response content
        return response.choices[0].message.content
    except Exception as e:
        log.error(f"OpenAI API error: {str(e)}", exc_info=True)
        
        # Return a descriptive mock response for debugging
        return f"This is a mock response. The OpenAI API call failed with error: {str(e)[:100]}... Please check your API key and configuration."
#full file drafted by AI