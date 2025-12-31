# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable, Optional, Union

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from langchat.adapters.logger import logger
from langchat.core.engine import LangChatEngine, set_api_server_mode

# Global engine instance
_engine: Optional[LangChatEngine] = None
_app: Optional[FastAPI] = None


def create_lifespan(
    auto_generate_interface: bool = True,
    auto_generate_docker: bool = True,
    llm=None,
    vector_db=None,
    db=None,
    reranker=None,
    prompt_template: Optional[str] = None,
    standalone_question_prompt: Optional[str] = None,
    verbose: Optional[bool] = None,
    max_chat_history: int = 20,
    port: int = 8000,
):
    """
    Create lifespan context manager for FastAPI application.
    Handles startup and shutdown events.

    Args:
        auto_generate_interface: Whether to auto-generate chat interface
        auto_generate_docker: Whether to auto-generate Docker files
        llm: LLM provider instance (required)
        vector_db: Vector database adapter (required)
        db: Database adapter for history storage (required)
        reranker: Reranker adapter (optional)
        prompt_template: System prompt template (optional)
        standalone_question_prompt: Standalone question prompt (optional)
        verbose: Enable verbose logging (optional)
        max_chat_history: Maximum chat history to keep (default: 20)
        port: Server port number (default: 8000)
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Lifespan context manager for FastAPI application.
        Handles startup and shutdown events.
        """
        global _engine

        # Set API server mode to disable console panel output
        set_api_server_mode(True)

        _engine = LangChatEngine(
            llm=llm,
            vector_db=vector_db,
            db=db,
            reranker=reranker,
            prompt_template=prompt_template,
            standalone_question_prompt=standalone_question_prompt,
            verbose=verbose,
            max_chat_history=max_chat_history,
        )

        # Startup logic
        try:
            # Auto-generate Dockerfile, .dockerignore, and requirements.txt
            if auto_generate_docker:
                try:
                    from langchat.core.utils.docker_generator import (
                        generate_dockerfile,
                        generate_dockerignore,
                        generate_requirements_txt,
                    )

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
            logger.info(f"Server running at: http://localhost:{port}")
            logger.info(f"API endpoint: http://localhost:{port}/chat")
            logger.info(f"Frontend interface: http://localhost:{port}/frontend")
        except Exception as e:
            logger.error(f"Error initializing API: {str(e)}")

        yield

        # Shutdown logic (if needed in the future)
        logger.info("LangChat API shutting down")

    return lifespan


def _get_ui_dist_dir() -> Path:
    """
    Resolve UI dist directory relative to the installed `langchat` package.
    Layout: src/langchat/core/ui/dist
    """
    pkg_dir = Path(__file__).resolve().parents[1]  # .../langchat/api -> .../langchat
    return pkg_dir / "core" / "ui" / "dist"


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
            "UI dist folder not found at src/langchat/core/ui/dist. "
            "Run `cd src/langchat/core/ui && npm install && npm run build`."
        )

        @app.get("/frontend", include_in_schema=False)
        @app.get("/frontend/", include_in_schema=False)
        async def _frontend_missing():
            return PlainTextResponse(
                "UI not built. Run: cd src/langchat/core/ui && npm install && npm run build",
                status_code=503,
            )

        return

    if assets_dir.exists():
        app.mount(
            "/frontend/assets",
            StaticFiles(directory=str(assets_dir)),
            name="frontend-assets",
        )

    # Serve other static files at the dist root (favicon, manifest, logo, etc)
    @app.get("/frontend", include_in_schema=False)
    @app.get("/frontend/", include_in_schema=False)
    async def _frontend_index():
        if index_file.exists():
            return FileResponse(index_file)
        return PlainTextResponse("UI build is missing index.html in core/ui/dist", status_code=500)

    @app.get("/frontend/{path:path}", include_in_schema=False)
    async def _frontend_spa(path: str):
        candidate = dist_dir / path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        if index_file.exists():
            return FileResponse(index_file)
        return PlainTextResponse("UI build is missing index.html in core/ui/dist", status_code=500)


def create_app(
    auto_generate_interface: bool = False,
    auto_generate_docker: bool = False,
    llm=None,
    vector_db=None,
    db=None,
    reranker=None,
    prompt_template: Optional[str] = None,
    standalone_question_prompt: Optional[str] = None,
    verbose: Optional[bool] = None,
    max_chat_history: int = 20,
    custom_routes: Optional[list[Union[APIRouter, Callable]]] = None,
    port: int = 8000,
) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        auto_generate_interface: Whether to auto-generate chat interface
        auto_generate_docker: Whether to auto-generate Docker files
        llm: LLM provider instance (required)
        vector_db: Vector database adapter (required)
        db: Database adapter for history storage (required)
        reranker: Reranker adapter (optional)
        prompt_template: System prompt template (optional)
        standalone_question_prompt: Standalone question prompt (optional)
        verbose: Enable verbose logging (optional)
        max_chat_history: Maximum chat history to keep (default: 20)
        custom_routes: Optional list of APIRouter instances to add before UI routes
        port: Server port number for logging and Dockerfile generation (default: 8000)

    Returns:
        FastAPI application instance (you can add more routes after creation using app.add_api_route() or app.include_router())

    Example:
        ```python
        from fastapi import APIRouter

        # Option 1: Add routes via custom_routes parameter
        custom_router = APIRouter()
        @custom_router.post("/custom")
        async def custom_endpoint():
            return {"message": "Hello"}

        app = create_app(..., custom_routes=[custom_router])

        # Option 2: Add routes after creation (recommended)
        app = create_app(...)
        @app.post("/custom")
        async def custom_endpoint():
            return {"message": "Hello"}
        ```
    """
    global _engine

    app = FastAPI(
        title="LangChat API",
        version="0.0.2",
        lifespan=create_lifespan(
            auto_generate_interface=auto_generate_interface,
            auto_generate_docker=auto_generate_docker,
            llm=llm,
            vector_db=vector_db,
            db=db,
            reranker=reranker,
            prompt_template=prompt_template,
            standalone_question_prompt=standalone_question_prompt,
            verbose=verbose,
            max_chat_history=max_chat_history,
            port=port,
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

    # Include default routers
    app.include_router(routes.router)

    # Add custom routes if provided (before UI mounting to avoid conflicts)
    if custom_routes:
        for route in custom_routes:
            if isinstance(route, APIRouter):
                app.include_router(route)
            else:
                logger.warning(
                    f"Custom route {route} should be an APIRouter instance. "
                    "Use app.add_api_route() or app.include_router() after create_app() instead."
                )

    # Serve the Vite UI (ui/dist) at /frontend
    # UI routes are added last to avoid conflicts with custom POST routes
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
