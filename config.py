import os
import json
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "sqlite:///./data/app.db"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_default_model: str = "gpt-3.5-turbo"
    openai_default_temperature: float = 0.7
    openai_default_max_tokens: int = 1000
    
    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "POC Backend"
    version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            # Handle JSON strings for list fields
            if field_name == 'backend_cors_origins':
                try:
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    # If not valid JSON, split by comma
                    return [url.strip() for url in raw_val.split(',') if url.strip()]
            return cls.json_loads(raw_val)

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.openai_api_key is not None and self.openai_api_key.strip() != ""
    
    @property
    def database_dir(self) -> str:
        """Get database directory"""
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            return os.path.dirname(db_path)
        return "data"


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.database_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)

# Print configuration status (for debugging)
if settings.debug:
    print(f"🔧 Configuration loaded:")
    print(f"   - Database: {settings.database_url}")
    print(f"   - OpenAI configured: {settings.is_openai_configured}")
    print(f"   - Upload directory: {settings.upload_dir}")
    print(f"   - CORS origins: {settings.backend_cors_origins}")
    print(f"   - Debug mode: {settings.debug}") 