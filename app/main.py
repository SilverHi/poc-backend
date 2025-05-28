from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.api import agents, resources, config
from config import settings

# Create database tables
create_tables()

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(agents.router, prefix=f"{settings.api_v1_str}/agents", tags=["agents"])
app.include_router(resources.router, prefix=f"{settings.api_v1_str}/resources", tags=["resources"])
app.include_router(config.router, prefix=f"{settings.api_v1_str}/config", tags=["config"])


@app.get("/")
def read_root():
    """Root path"""
    return {
        "message": settings.project_name,
        "version": settings.version,
        "docs": "/docs",
        "openai_configured": settings.is_openai_configured
    }


@app.get("/health")
def health_check():
    """Health check"""
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