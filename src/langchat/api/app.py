"""
FastAPI application setup for LangChat API.
"""

import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine

logger = logging.getLogger(__name__)

# Global engine instance
_engine: LangChatEngine = None
_config: LangChatConfig = None


def create_app(config: LangChatConfig = None, auto_generate_interface: bool = True, auto_generate_docker: bool = True) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config: LangChat configuration. If None, uses default.
    
    Returns:
        FastAPI application instance
    """
    global _engine, _config
    
    _config = config or LangChatConfig.from_env()
    _engine = LangChatEngine(config=_config)
    
    app = FastAPI(title="LangChat API", version="0.0.1")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize engine on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        try:
            # Auto-generate chat interface
            if auto_generate_interface:
                try:
                    from langchat.utils.interface_generator import generate_chat_interface
                    api_url = f"http://localhost:{_config.server_port}" if _config else "http://localhost:8000"
                    generate_chat_interface(
                        output_path="chat_interface.html",
                        api_url=api_url
                    )
                    logger.info("Chat interface auto-generated: chat_interface.html")
                except Exception as e:
                    logger.warning(f"Failed to auto-generate chat interface: {str(e)}")
            
            # Auto-generate Dockerfile, .dockerignore, and requirements.txt
            if auto_generate_docker:
                try:
                    from langchat.utils.docker_generator import (
                        generate_dockerfile,
                        generate_dockerignore,
                        generate_requirements_txt
                    )
                    port = _config.server_port if _config else 8000
                    
                    # Generate Dockerfile
                    generate_dockerfile(
                        output_path="Dockerfile",
                        port=port
                    )
                    logger.info(f"Dockerfile auto-generated with port {port}")
                    
                    # Generate .dockerignore
                    generate_dockerignore(output_path=".dockerignore")
                    logger.info(".dockerignore auto-generated")
                    
                    # Generate requirements.txt from setup.py
                    generate_requirements_txt(
                        output_path="requirements.txt",
                        setup_path="setup.py"
                    )
                    logger.info("requirements.txt auto-generated from setup.py")
                except Exception as e:
                    logger.warning(f"Failed to auto-generate Docker files: {str(e)}")
            
            logger.info("LangChat API started successfully")
        except Exception as e:
            logger.error(f"Error initializing API: {str(e)}")
    
    # Import routes
    from langchat.api import routes
    
    # Include routers
    app.include_router(routes.router)
    
    return app


def get_app() -> FastAPI:
    """
    Get the FastAPI application instance.
    Must be called after create_app().
    
    Returns:
        FastAPI application instance
    """
    if _engine is None:
        raise RuntimeError("App not initialized. Call create_app() first.")
    return _engine


def get_engine() -> LangChatEngine:
    """
    Get the LangChat engine instance.
    Must be called after create_app().
    
    Returns:
        LangChatEngine instance
    """
    if _engine is None:
        raise RuntimeError("Engine not initialized. Call create_app() first.")
    return _engine


def get_config() -> LangChatConfig:
    """
    Get the LangChat configuration instance.
    Must be called after create_app().
    
    Returns:
        LangChatConfig instance
    """
    if _config is None:
        raise RuntimeError("Config not initialized. Call create_app() first.")
    return _config