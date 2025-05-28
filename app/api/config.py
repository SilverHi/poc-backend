from fastapi import APIRouter, HTTPException, status
from app.schemas.config import OpenAIConfig, OpenAIConfigUpdate
from app.services.ai_service import AIService
from config import settings

router = APIRouter()
ai_service = AIService()


@router.get("/openai", response_model=OpenAIConfig)
def get_openai_config():
    """Get OpenAI configuration"""
    models = ai_service.get_available_models()
    
    return OpenAIConfig(
        models=models,
        default_model=settings.openai_default_model,
        default_temperature=settings.openai_default_temperature,
        default_max_tokens=settings.openai_default_max_tokens,
        is_configured=ai_service.is_configured(),
        has_api_key=settings.openai_api_key is not None
    )


@router.post("/openai")
def update_openai_config(config_data: OpenAIConfigUpdate):
    """Update OpenAI configuration"""
    try:
        # Note: In production environment, configuration should be saved to database or config file
        # This is just a demonstration, actual implementation needs persistent storage
        
        if config_data.api_key:
            # API key should be stored securely here
            pass
        
        if config_data.default_model:
            # Update default model
            pass
        
        if config_data.default_temperature is not None:
            # Update default temperature
            pass
        
        if config_data.default_max_tokens:
            # Update default max tokens
            pass
        
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration update failed: {str(e)}"
        ) 