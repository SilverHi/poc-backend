from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.api import agents, resources, config
from config import settings

# 创建数据库表
create_tables()

# 创建FastAPI应用
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=settings.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agents.router, prefix=f"{settings.api_v1_str}/agents", tags=["agents"])
app.include_router(resources.router, prefix=f"{settings.api_v1_str}/resources", tags=["resources"])
app.include_router(config.router, prefix=f"{settings.api_v1_str}/config", tags=["config"])


@app.get("/")
def read_root():
    """根路径"""
    return {
        "message": settings.project_name,
        "version": settings.version,
        "docs": "/docs",
        "openai_configured": settings.is_openai_configured
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.version,
        "openai_configured": settings.is_openai_configured
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    ) 