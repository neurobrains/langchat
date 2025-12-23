# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING

import uvicorn

from langchat.api.app import create_app

if TYPE_CHECKING:
    from langchat.config import LangChatConfig


def run(
    host: str = "0.0.0.0",
    port: int = 8000,
    config: LangChatConfig | None = None,
    llm_provider: str | None = None,
    llm_api_key: str | None = None,
) -> None:
    """
    Run LangChat FastAPI server with a single call.

    Example:
        from langchat.server import run
        run(llm_provider="gemini", llm_api_key="...")
    """
    app = create_app(
        config=config,
        llm_provider=llm_provider,
        llm_api_key=llm_api_key,
    )
    uvicorn.run(app, host=host, port=port)


