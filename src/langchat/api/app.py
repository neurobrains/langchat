"""
FastAPI application setup for LangChat API.
"""

from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine, set_api_server_mode
from langchat.logger import logger

# Global engine instance
_engine: Optional[LangChatEngine] = None
_config: Optional[LangChatConfig] = None
_app: Optional[FastAPI] = None


def create_app(
    config: Optional[LangChatConfig] = None,
    auto_generate_interface: bool = True,
    auto_generate_docker: bool = True,
) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        config: LangChat configuration. If None, uses default.

    Returns:
        FastAPI application instance
    """
    global _engine, _config

    _config = config or LangChatConfig.from_env()

    # Set API server mode to disable console panel output
    set_api_server_mode(True)

    _engine = LangChatEngine(config=_config)

    app = FastAPI(title="LangChat API", version="0.0.2")

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
                    from langchat.utils.interface_generator import (
                        generate_chat_interface,
                    )

                    api_url = (
                        f"http://localhost:{_config.server_port}"
                        if _config
                        else "http://localhost:8000"
                    )
                    generate_chat_interface(output_path="chat_interface.html", api_url=api_url)
                    logger.info("Chat interface auto-generated: chat_interface.html")
                except Exception as e:
                    logger.warning(f"Failed to auto-generate chat interface: {str(e)}")

            # Auto-generate Dockerfile, .dockerignore, and requirements.txt
            if auto_generate_docker:
                try:
                    from langchat.utils.docker_generator import (
                        generate_dockerfile,
                        generate_dockerignore,
                        generate_requirements_txt,
                    )

                    port = _config.server_port if _config else 8000

                    # Generate Dockerfile
                    generate_dockerfile(output_path="Dockerfile", port=port)
                    logger.info(f"Dockerfile auto-generated with port {port}")

                    # Generate .dockerignore
                    generate_dockerignore(output_path=".dockerignore")
                    logger.info(".dockerignore auto-generated")

                    # Generate requirements.txt from setup.py
                    generate_requirements_txt(output_path="requirements.txt", setup_path="setup.py")
                    logger.info("requirements.txt auto-generated from setup.py")
                except Exception as e:
                    logger.warning(f"Failed to auto-generate Docker files: {str(e)}")

            logger.info("LangChat API started successfully")
            logger.info(f"Server running at: http://localhost:{_config.server_port}")
            logger.info(f"API endpoint: http://localhost:{_config.server_port}/chat")
            logger.info(f"Frontend interface: http://localhost:{_config.server_port}/frontend")
        except Exception as e:
            logger.error(f"Error initializing API: {str(e)}")

    # Import routes
    from langchat.api import routes

    # Include routers
    app.include_router(routes.router)

    global _app
    _app = app
    return app


def get_app() -> FastAPI:
    """
    Get the FastAPI application instance.
    Must be called after create_app().

    Returns:
        FastAPI application instance
    """
    if _app is None:
        raise RuntimeError("App not initialized. Call create_app() first.")
    return _app


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
