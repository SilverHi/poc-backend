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
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.client is not None and settings.openai_api_key is not None
    
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
                "id": "gpt-4",
                "name": "GPT-4",
                "max_tokens": 8000,
                "description": "Most powerful model"
            },
            {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "max_tokens": 128000,
                "description": "Latest GPT-4 model"
            }
        ]
    
    def _combine_prompts(self, system_prompt: str, user_input: str) -> str:
        """
        Combine system prompt and user input into a single prompt
        
        Args:
            system_prompt: System prompt
            user_input: User input
            
        Returns:
            str: Combined prompt
        """
        combined_prompt = f"""You are an AI assistant. Please strictly follow the role settings and instructions below to answer user questions:

【Role Settings and Instructions】
{system_prompt}

【User Question】
{user_input}

Please provide a professional answer to the user's question based on the above role settings:"""
        
        return combined_prompt

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
            "Combining system prompt and user input...",
            "Calling OpenAI API...",
        ]
        
        try:
            # Combine system prompt and user input
            combined_prompt = self._combine_prompts(system_prompt, user_input)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": combined_prompt}
                ],
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