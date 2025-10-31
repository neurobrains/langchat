"""
FastAPI routes for LangChat API.
"""

import logging
import asyncio
import os
from typing import Optional
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timezone

from langchat.api.app import get_engine, get_config
from langchat.api.models import QueryRequest, Feedback

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint - redirects to frontend"""
    return RedirectResponse(url="/frontend")


@router.get("/frontend")
async def frontend():
    """Serve the chat interface HTML"""
    try:
        # Try to read the generated chat interface
        interface_path = "chat_interface.html"
        if os.path.exists(interface_path):
            with open(interface_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            # Generate interface on the fly if not exists
            from langchat.utils.interface_generator import generate_chat_interface
            config = get_config()
            api_url = f"http://localhost:{config.server_port}" if config else "http://localhost:8000"
            generate_chat_interface(
                output_path=interface_path,
                api_url=api_url
            )
            with open(interface_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return HTMLResponse(
            content=f"<html><body><h1>Error loading interface</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.0.1"
    }


@router.post("/chat")
async def chat(
    query: str = Form(...),
    userId: str = Form(...),
    domain: str = Form(...),
    image: Optional[UploadFile] = File(default=None, description="Image file to upload", media_type="image/*"),
    background_tasks: BackgroundTasks = BackgroundTasks()
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
            standalone_question=standalone_question
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return JSONResponse(
            content={
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                "userId": userId,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e)
            },
            status_code=500
        )


@router.post("/feedback")
async def feedback(feedback_data: Feedback):
    """
    Feedback endpoint for collecting user feedback.
    
    Args:
        feedback_data: Feedback data model
    
    Returns:
        JSON response with status
    """
    try:
        engine = get_engine()
        
        # Save feedback to database
        engine.id_manager.insert_with_retry("feedback", {
            "timestamp": feedback_data.timestamp,
            "type": feedback_data.type,
            "user_id": feedback_data.userId,
            "domain": feedback_data.domain,
            "response": feedback_data.response,
            "feedback_text": feedback_data.feedback or "",
            "rating": 1 if feedback_data.type == "like" else 0
        })
        
        return JSONResponse(content={
            "status": "success",
            "message": "Feedback saved successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Failed to save feedback",
                "error": str(e)
            },
            status_code=500
        )
