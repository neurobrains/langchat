# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine, set_api_server_mode
from langchat.logger import logger

# Global engine instance
_engine: Optional[LangChatEngine] = None
_config: Optional[LangChatConfig] = None
_app: Optional[FastAPI] = None


def create_lifespan(
    auto_generate_interface: bool = True,
    auto_generate_docker: bool = True,
):
    """
    Create lifespan context manager for FastAPI application.
    Handles startup and shutdown events.

    Args:
        auto_generate_interface: Whether to auto-generate chat interface
        auto_generate_docker: Whether to auto-generate Docker files
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Lifespan context manager for FastAPI application.
        Handles startup and shutdown events.
        """
        global _engine, _config

        _config = _config or LangChatConfig.from_env()

        # Set API server mode to disable console panel output
        set_api_server_mode(True)

        _engine = LangChatEngine(config=_config)

        # Startup logic
        try:
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

        yield

        # Shutdown logic (if needed in the future)
        logger.info("LangChat API shutting down")

    return lifespan


def _get_ui_dist_dir() -> Path:
    """
    Resolve UI dist directory relative to the installed `langchat` package.
    Layout: src/langchat/ui/dist
    """
    pkg_dir = Path(__file__).resolve().parents[1]  # .../langchat/api -> .../langchat
    return pkg_dir / "ui" / "dist"


def _mount_ui(app: FastAPI) -> None:
    """
    Serve the built Vite UI from ui/dist at /frontend.
    - /frontend/ -> index.html
    - /frontend/assets/* -> static assets
    - /frontend/{path} -> SPA fallback to index.html if file doesn't exist
    """
    dist_dir = _get_ui_dist_dir()
    index_file = dist_dir / "index.html"
    assets_dir = dist_dir / "assets"

    if not dist_dir.exists():
        logger.warning(
            "UI dist folder not found at src/langchat/ui/dist. "
            "Run `cd src/langchat/ui && npm install && npm run build`."
        )

        @app.get("/frontend", include_in_schema=False)
        @app.get("/frontend/", include_in_schema=False)
        async def _frontend_missing():
            return PlainTextResponse(
                "UI not built. Run: cd src/langchat/ui && npm install && npm run build",
                status_code=503,
            )

        return

    if assets_dir.exists():
        app.mount(
            "/frontend/assets",
            StaticFiles(directory=str(assets_dir)),
            name="frontend-assets",
        )

    # Serve other static files at the dist root (favicon, manifest, etc)
    @app.get("/frontend", include_in_schema=False)
    @app.get("/frontend/", include_in_schema=False)
    async def _frontend_index():
        if index_file.exists():
            return FileResponse(index_file)
        return PlainTextResponse("UI build is missing index.html in ui/dist", status_code=500)

    @app.get("/frontend/{path:path}", include_in_schema=False)
    async def _frontend_spa(path: str):
        candidate = dist_dir / path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        if index_file.exists():
            return FileResponse(index_file)
        return PlainTextResponse("UI build is missing index.html in ui/dist", status_code=500)


def create_app(
    config: Optional[LangChatConfig] = None,
    auto_generate_interface: bool = False,
    auto_generate_docker: bool = False,
    llm_provider: Optional[str] = None,
    llm_api_key: Optional[str] = None,
) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        config: LangChat configuration. If None, uses default.
        auto_generate_interface: Whether to auto-generate chat interface
        auto_generate_docker: Whether to auto-generate Docker files

    Returns:
        FastAPI application instance
    """
    global _engine, _config

    _config = config or LangChatConfig.from_env()

    # Convenience overrides (avoid requiring callers to build LangChatConfig manually)
    if llm_provider:
        _config.llm_provider = llm_provider
    if llm_api_key:
        provider = (_config.llm_provider or "auto").strip().lower()
        if provider == "auto":
            provider = "openai"
            _config.llm_provider = provider
        if provider == "openai":
            _config.openai_api_keys = [llm_api_key]
        elif provider == "gemini":
            _config.gemini_api_keys = [llm_api_key]
        elif provider == "anthropic":
            _config.anthropic_api_keys = [llm_api_key]
        else:
            raise ValueError(
                f"Unknown llm_provider: {_config.llm_provider!r} (expected auto/openai/gemini/anthropic)"
            )

    app = FastAPI(
        title="LangChat API",
        version="0.0.2",
        lifespan=create_lifespan(
            auto_generate_interface=auto_generate_interface,
            auto_generate_docker=auto_generate_docker,
        ),
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import routes
    from langchat.api import routes

    # Include routers
    app.include_router(routes.router)

    # Serve the Vite UI (ui/dist) at /frontend
    _mount_ui(app)

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
