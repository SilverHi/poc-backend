from fastapi import APIRouter, HTTPException, status
from app.schemas.config import OpenAIConfig, OpenAIConfigUpdate
from app.services.ai_service import AIService
from config import settings

router = APIRouter()
ai_service = AIService()


@router.get("/openai", response_model=OpenAIConfig)
def get_openai_config():
    """获取OpenAI配置"""
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
    """更新OpenAI配置"""
    try:
        # 注意：在生产环境中，这里应该将配置保存到数据库或配置文件
        # 目前只是演示，实际应用中需要实现持久化存储
        
        if config_data.api_key:
            # 这里应该安全地存储API密钥
            pass
        
        if config_data.default_model:
            # 更新默认模型
            pass
        
        if config_data.default_temperature is not None:
            # 更新默认温度
            pass
        
        if config_data.default_max_tokens:
            # 更新默认最大tokens
            pass
        
        return {"message": "配置更新成功"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"配置更新失败: {str(e)}"
        ) 