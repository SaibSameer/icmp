"""
Service for generating and managing conversation summaries.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

log = logging.getLogger(__name__)

class ConversationSummaryService:
    """Service for generating and managing conversation summaries."""
    
    def __init__(self, template_path: str = None):
        """
        Initialize the conversation summary service.
        
        Args:
            template_path: Path to the template file. If None, uses default path.
        """
        if template_path is None:
            template_path = Path(__file__).parent.parent / 'templates' / 'conversation_summary_template.txt'
        
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found at {template_path}")
            
        with open(self.template_path, 'r') as f:
            self.template = f.read()
    
    def generate_summary(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary for a conversation.
        
        Args:
            conversation_data: Dictionary containing conversation information:
                - business_name: Name of the business
                - user_name: Name of the user
                - conversation_id: UUID of the conversation
                - start_time: Start time of the conversation
                - last_updated: Last update time of the conversation
                - conversation_history: List of messages in the conversation
                
        Returns:
            Dictionary containing the structured summary
        """
        try:
            # Format the conversation history
            formatted_history = self._format_conversation_history(
                conversation_data.get('conversation_history', [])
            )
            
            # Prepare the prompt
            prompt = self.template.format(
                business_name=conversation_data.get('business_name', 'Unknown Business'),
                user_name=conversation_data.get('user_name', 'Unknown User'),
                conversation_id=conversation_data.get('conversation_id', 'Unknown'),
                start_time=conversation_data.get('start_time', 'Unknown'),
                last_updated=conversation_data.get('last_updated', 'Unknown'),
                conversation_history=formatted_history
            )
            
            # Import here to avoid circular imports
            from backend.ai.llm_service import LLMService
            
            # Initialize LLM service
            llm_service = LLMService()
            
            # Call LLM service to generate summary
            summary_response = llm_service.generate_response(
                business_id=conversation_data.get('business_id'),
                input_text=formatted_history,
                system_prompt=prompt,
                call_type="summary"
            )
            
            # Parse JSON response
            try:
                summary = json.loads(summary_response)
                return summary
            except json.JSONDecodeError as e:
                log.error(f"Error parsing summary JSON: {str(e)}")
                # Return a fallback summary
                return {
                    "overview": "Unable to generate structured summary",
                    "key_points": [],
                    "decisions": [],
                    "pending_items": [],
                    "next_steps": [],
                    "sentiment": "neutral",
                    "confidence_score": 0.0
                }
            
        except Exception as e:
            log.error(f"Error generating conversation summary: {str(e)}")
            raise
    
    def _format_conversation_history(self, messages: list) -> str:
        """
        Format conversation messages into a readable string.
        
        Args:
            messages: List of message dictionaries with 'sender' and 'content' keys
            
        Returns:
            Formatted string of the conversation
        """
        formatted_messages = []
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            formatted_messages.append(f"{sender} ({timestamp}): {content}")
        
        return "\n".join(formatted_messages)
    
    def save_summary(self, conn, conversation_id: str, summary: Dict[str, Any]) -> bool:
        """
        Save the generated summary to the database.
        
        Args:
            conn: Database connection
            conversation_id: UUID of the conversation
            summary: Dictionary containing the summary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE conversations 
                SET conversation_summary = %s
                WHERE conversation_id = %s
                """,
                (json.dumps(summary), conversation_id)
            )
            conn.commit()
            return True
            
        except Exception as e:
            log.error(f"Error saving conversation summary: {str(e)}")
            conn.rollback()
            return False