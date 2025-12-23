# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse

from langchat.adapters.logger import logger
from langchat.api.app import get_engine

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint - redirects to frontend"""
    return RedirectResponse(url="/frontend/")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.0.2",
    }


@router.post("/chat")
async def chat(
    query: str = Form(...),
    userId: str = Form(...),
    domain: str = Form(...),
    image: Optional[UploadFile] = File(
        default=None, description="Image file to upload", media_type="image/*"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Chat endpoint for processing user queries.

    Args:
        query: User query text
        userId: User ID
        domain: User domain
        image: Optional image file
        background_tasks: Background tasks

    Returns:
        JSON response with AI response
    """
    try:
        engine = get_engine()

        # Generate standalone question (can be enhanced with LLM)
        # For now, using query as standalone question
        standalone_question = query

        # Process chat
        result = await engine.chat(
            query=query,
            user_id=userId,
            domain=domain,
            standalone_question=standalone_question,
        )

        # Ensure result has the expected format
        if not isinstance(result, dict):
            result = {"response": str(result) if result else "No response received."}

        # Ensure response field exists
        if "response" not in result or not result.get("response"):
            result["response"] = "No response received."

        # Ensure status field exists
        if "status" not in result:
            result["status"] = "success"

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            content={
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                "userId": userId,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e),
            },
            status_code=500,
        )
