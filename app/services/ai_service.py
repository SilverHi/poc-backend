import asyncio
from typing import List, Optional
import openai
from config import settings


class AIService:
    """AI service for handling OpenAI API calls"""
    
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def get_client(self) -> openai.OpenAI:
        """
        Get OpenAI client instance
        
        This method can be overridden in internal network environments
        to provide custom client initialization logic (e.g., refresh token each time)
        
        Returns:
            openai.OpenAI: OpenAI client instance
        """
        # Always create a new client instance to support token refresh scenarios
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is not configured")
        
        # Create new client instance each time for internal network compatibility
        return openai.OpenAI(api_key=settings.openai_api_key)
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        try:
            # Don't cache the result, always check fresh
            return settings.openai_api_key is not None and settings.openai_api_key.strip() != ""
        except:
            return False
    
    def get_available_models(self) -> List[dict]:
        """Get list of available models"""
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "max_tokens": 4000,
                "description": "Fast and efficient model"
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "max_tokens": 8000,
                "description": "Most powerful model"
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "max_tokens": 128000,
                "description": "Latest GPT-4o model"
            }
        ]
    
    def _prepare_messages(self, system_prompt: str, user_input: str) -> List[dict]:
        """
        Prepare messages for OpenAI API with separate system and user roles
        
        Args:
            system_prompt: System prompt
            user_input: User input
            
        Returns:
            List[dict]: Messages formatted for OpenAI API
        """
        messages = []
        
        # Add system message if system prompt is provided
        if system_prompt and system_prompt.strip():
            messages.append({
                "role": "system", 
                "content": system_prompt
            })
        
        # Add user message
        messages.append({
            "role": "user", 
            "content": user_input
        })
        
        return messages

    async def execute_agent(
        self,
        system_prompt: str,
        user_input: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> tuple[str, List[str]]:
        """
        Execute AI agent
        
        Args:
            system_prompt: System prompt
            user_input: User input
            model: Model to use
            temperature: Temperature parameter
            max_tokens: Maximum tokens
            
        Returns:
            tuple[output, logs]: Output result and execution logs
        """
        if not self.is_configured():
            raise ValueError("OpenAI API is not configured. Please set OPENAI_API_KEY in environment variables.")
        
        # Use default values
        model = model or settings.openai_default_model
        temperature = temperature if temperature is not None else settings.openai_default_temperature
        max_tokens = max_tokens or settings.openai_default_max_tokens
        
        logs = [
            f"Starting AI agent...",
            f"Using model: {model}",
            f"Temperature: {temperature}",
            f"Max tokens: {max_tokens}",
            "Preparing messages with system and user roles...",
            "Calling OpenAI API...",
        ]
        
        try:
            # Prepare messages with separate system and user roles
            messages = self._prepare_messages(system_prompt, user_input)
            
            # Use get_client() method instead of direct self.client access
            client = self.get_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            output = response.choices[0].message.content
            logs.extend([
                "API call successful",
                f"Generated tokens: {response.usage.completion_tokens}",
                "Processing completed"
            ])
            
            return output, logs
            
        except Exception as e:
            error_msg = f"AI execution failed: {str(e)}"
            logs.append(error_msg)
            raise ValueError(error_msg) 