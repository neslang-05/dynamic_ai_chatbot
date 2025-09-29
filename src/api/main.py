"""
FastAPI application for the Dynamic AI Chatbot.
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import traceback
from typing import Dict, Any
from pathlib import Path

from models import ChatRequest, ChatResponse
from api.chat import ChatManager
from api.dependencies import get_chat_manager
from auth.router import router as auth_router
from auth.repository import user_repository
from connectors.slack import SlackConnector
from connectors.telegram import TelegramConnector
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Dynamic AI Chatbot",
        description="A modular, API-driven chatbot with advanced NLP capabilities",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files (for demo.html and other static assets)
    project_root = Path(__file__).parent.parent.parent
    app.mount("/static", StaticFiles(directory=str(project_root)), name="static")
    
    # Include authentication router
    app.include_router(auth_router)
    
    # Initialize connectors
    slack_connector = SlackConnector()
    telegram_connector = TelegramConnector()
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "message": "Dynamic AI Chatbot is running"}
    
    # Main chat endpoint
    @app.post("/chat", response_model=ChatResponse)
    async def chat(
        request: ChatRequest,
        chat_manager: ChatManager = Depends(get_chat_manager)
    ):
        """Process a chat message and return bot response."""
        try:
            logger.info(f"Processing chat request from user {request.user_id}")
            response = await chat_manager.process_message(request)
            return response
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise HTTPException(status_code=500, detail="Failed to process message")
    
    # Webhook endpoints
    @app.post("/webhook/slack")
    async def slack_webhook(request: Request):
        """Slack webhook endpoint."""
        try:
            return await slack_connector.handle_webhook(request)
        except Exception as e:
            logger.error(f"Error in Slack webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    @app.post("/webhook/telegram")
    async def telegram_webhook(request: Request):
        """Telegram webhook endpoint."""
        try:
            return await telegram_connector.handle_webhook(request)
        except Exception as e:
            logger.error(f"Error in Telegram webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    # Session management endpoints
    @app.get("/session/{session_id}")
    async def get_session(
        session_id: str,
        chat_manager: ChatManager = Depends(get_chat_manager)
    ):
        """Get session information."""
        try:
            session = await chat_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            return session
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get session")
    
    @app.delete("/session/{session_id}")
    async def delete_session(
        session_id: str,
        chat_manager: ChatManager = Depends(get_chat_manager)
    ):
        """Delete a session."""
        try:
            await chat_manager.delete_session(session_id)
            return {"message": "Session deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete session")
    
    # Analytics endpoints
    @app.get("/analytics/stats")
    async def get_analytics_stats(
        chat_manager: ChatManager = Depends(get_chat_manager)
    ):
        """Get conversation analytics stats."""
        try:
            stats = await chat_manager.get_analytics_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting analytics stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to get analytics")
    
    logger.info("FastAPI application created successfully")
    
    # Initialize database indexes on startup
    @app.on_event("startup")
    async def startup_event():
        try:
            await user_repository.create_indexes()
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Could not create database indexes: {e}")
            logger.info("Application will continue without database indexes - they will be created when needed")

    return app