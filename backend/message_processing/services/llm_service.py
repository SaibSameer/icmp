from typing import Dict, Any, Optional
import os
import json
import time
from ..core.errors import LLMServiceError, RateLimitError

class LLMService:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.api_key = os.getenv('LLM_API_KEY')
        self.api_endpoint = os.getenv('LLM_API_ENDPOINT', 'https://api.openai.com/v1')
        self.model = os.getenv('LLM_MODEL', 'gpt-4')
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '60'))
        self.rate_limit_tokens = int(os.getenv('RATE_LIMIT_TOKENS_PER_MINUTE', '40000'))
        
        # Initialize rate limiting state
        self.request_count = 0
        self.token_count = 0
        self.last_reset = time.time()

    async def generate_response(
        self,
        prompt: str,
        message_content: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate response using LLM with rate limiting."""
        await self._check_rate_limits()
        
        try:
            # Prepare the request
            request_data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': message_content}
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature
            }
            
            # Add context if provided
            if context:
                request_data['messages'].append({
                    'role': 'system',
                    'content': f"Context: {json.dumps(context)}"
                })
            
            # Make API request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json=request_data
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("Rate limit exceeded", service="llm")
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Update rate limiting counters
                    self._update_rate_limits(result)
                    
                    # Log the request
                    await self._log_request(prompt, message_content, result)
                    
                    return result['choices'][0]['message']['content']
                    
        except Exception as e:
            if isinstance(e, RateLimitError):
                raise
            raise LLMServiceError(f"Error generating response: {str(e)}", model=self.model)

    async def _check_rate_limits(self) -> None:
        """Check if we're within rate limits."""
        current_time = time.time()
        if current_time - self.last_reset >= 60:
            # Reset counters every minute
            self.request_count = 0
            self.token_count = 0
            self.last_reset = current_time
        
        if self.request_count >= self.rate_limit_requests:
            raise RateLimitError(
                f"Request rate limit exceeded: {self.rate_limit_requests} requests per minute",
                service="llm"
            )
        
        if self.token_count >= self.rate_limit_tokens:
            raise RateLimitError(
                f"Token rate limit exceeded: {self.rate_limit_tokens} tokens per minute",
                service="llm"
            )

    def _update_rate_limits(self, response: Dict[str, Any]) -> None:
        """Update rate limiting counters."""
        self.request_count += 1
        if 'usage' in response:
            self.token_count += response['usage'].get('total_tokens', 0)

    async def _log_request(
        self,
        prompt: str,
        message_content: str,
        response: Dict[str, Any]
    ) -> None:
        """Log LLM request to database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO llm_calls (
                        prompt,
                        message_content,
                        response,
                        model,
                        tokens_used,
                        created_at
                    ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
                    """,
                    prompt,
                    message_content,
                    json.dumps(response),
                    self.model,
                    response.get('usage', {}).get('total_tokens', 0)
                )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error logging LLM request: {str(e)}")

    async def get_available_models(self) -> list:
        """Get list of available models."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_endpoint}/models",
                    headers={'Authorization': f'Bearer {self.api_key}'}
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return [model['id'] for model in result['data']]
        except Exception as e:
            raise LLMServiceError(f"Error getting available models: {str(e)}", model=self.model)

    async def validate_model(self, model: str) -> bool:
        """Validate if a model is available and accessible."""
        try:
            available_models = await self.get_available_models()
            return model in available_models
        except Exception as e:
            raise LLMServiceError(f"Error validating model: {str(e)}", model=model) 