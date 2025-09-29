"""
FastAPI server for the dynamic AI chatbot.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import logging
import os
import sys
from datetime import datetime
import uvicorn

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.core.engine import ChatbotEngine
from chatbot.utils.config import Config
from chatbot.utils.helpers import (
    validate_user_input, rate_limit_check, create_success_response,
    create_error_response, PerformanceTimer, health_check
)


# Pydantic models for API
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_id: str = Field(default="api_user", description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ChatResponse(BaseModel):
    response: str
    confidence: float
    session_id: str
    timestamp: str
    context_used: int
    similar_found: int


class ConversationStats(BaseModel):
    session_id: Optional[str]
    message_count: int
    context_keywords: int
    duration_minutes: float


class UserPreferences(BaseModel):
    user_id: str
    preferences: Dict


# Initialize FastAPI app
app = FastAPI(
    title="Dynamic AI Chatbot API",
    description="Intelligent, multi-platform AI chatbot with self-learning capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
config = None
chatbot_engine = None
active_sessions = {}

# Rate limiting storage (in production, use Redis or similar)
rate_limit_storage = {}


def get_chatbot_engine():
    """Dependency to get chatbot engine."""
    global chatbot_engine
    if not chatbot_engine:
        raise HTTPException(status_code=500, detail="Chatbot engine not initialized")
    return chatbot_engine


@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot engine on startup."""
    global config, chatbot_engine
    
    try:
        config = Config()
        if not config.validate_config():
            raise Exception("Configuration validation failed")
        
        chatbot_engine = ChatbotEngine(config)
        logging.info("🚀 Chatbot API server started successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize chatbot: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global active_sessions
    
    # End all active sessions
    for session_id in active_sessions:
        try:
            chatbot_engine.end_conversation()
        except:
            pass
    
    logging.info("👋 Chatbot API server shutting down")


@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the web interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dynamic AI Chatbot</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Arial', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center;
            }
            .chat-container { 
                width: 90%; 
                max-width: 800px; 
                height: 80vh; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex; 
                flex-direction: column;
                overflow: hidden;
            }
            .chat-header { 
                background: #667eea; 
                color: white; 
                padding: 20px; 
                text-align: center;
                font-size: 1.5em;
                font-weight: bold;
            }
            .chat-messages { 
                flex: 1; 
                overflow-y: auto; 
                padding: 20px;
                background: #f8f9fa;
            }
            .message { 
                margin: 10px 0; 
                padding: 12px 16px; 
                border-radius: 15px; 
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message { 
                background: #667eea; 
                color: white; 
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            .bot-message { 
                background: #e3f2fd; 
                color: #333;
                border-bottom-left-radius: 5px;
            }
            .chat-input { 
                display: flex; 
                padding: 20px;
                background: white;
                border-top: 1px solid #eee;
            }
            .chat-input input { 
                flex: 1; 
                padding: 12px 16px; 
                border: 2px solid #ddd; 
                border-radius: 25px; 
                outline: none;
                font-size: 1em;
            }
            .chat-input input:focus { 
                border-color: #667eea; 
            }
            .chat-input button { 
                margin-left: 10px; 
                padding: 12px 24px; 
                background: #667eea; 
                color: white; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer;
                font-size: 1em;
                transition: background 0.3s;
            }
            .chat-input button:hover { 
                background: #5a6fd8; 
            }
            .confidence-indicator {
                font-size: 0.8em;
                color: #666;
                margin-top: 5px;
            }
            .loading {
                color: #666;
                font-style: italic;
            }
            .error-message {
                background: #ffebee !important;
                color: #c62828 !important;
                border-left: 4px solid #c62828;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                🤖 Dynamic AI Chatbot
            </div>
            <div class="chat-messages" id="messages">
                <div class="message bot-message">
                    Hello! I'm your Dynamic AI assistant. I can help you with questions, have conversations, and learn from our interactions. How can I help you today?
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Type your message here..." 
                       onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            const messagesContainer = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            let sessionId = null;
            const userId = 'web_user_' + Math.random().toString(36).substr(2, 9);

            function addMessage(content, isUser, confidence = null, error = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                
                if (error) {
                    messageDiv.className += ' error-message';
                }
                
                messageDiv.innerHTML = content;
                
                if (!isUser && confidence !== null && !error) {
                    const confidenceDiv = document.createElement('div');
                    confidenceDiv.className = 'confidence-indicator';
                    const emoji = confidence >= 0.8 ? '🟢' : confidence >= 0.6 ? '🟡' : '🔴';
                    confidenceDiv.textContent = `Confidence: ${(confidence * 100).toFixed(1)}% ${emoji}`;
                    messageDiv.appendChild(confidenceDiv);
                }
                
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function showLoading() {
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message bot-message loading';
                loadingDiv.id = 'loading';
                loadingDiv.textContent = 'Thinking...';
                messagesContainer.appendChild(loadingDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function hideLoading() {
                const loading = document.getElementById('loading');
                if (loading) {
                    loading.remove();
                }
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                messageInput.value = '';
                showLoading();

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            user_id: userId,
                            session_id: sessionId
                        })
                    });

                    const data = await response.json();
                    hideLoading();

                    if (data.success) {
                        const responseData = data.data;
                        sessionId = responseData.session_id;
                        addMessage(responseData.response, false, responseData.confidence);
                    } else {
                        addMessage(`Error: ${data.message}`, false, null, true);
                    }
                } catch (error) {
                    hideLoading();
                    addMessage(`Connection error: ${error.message}`, false, null, true);
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            // Focus input on page load
            messageInput.focus();
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/health", response_model=Dict)
async def health_check_endpoint():
    """Health check endpoint."""
    return health_check()


@app.post("/api/chat", response_model=Dict)
async def chat_endpoint(
    chat_request: ChatMessage,
    background_tasks: BackgroundTasks,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Main chat endpoint."""
    try:
        # Rate limiting
        if not rate_limit_check(
            chat_request.user_id, 
            "chat", 
            limit=config.RATE_LIMIT_PER_MINUTE,
            storage=rate_limit_storage
        ):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Validate input
        validation = validate_user_input(chat_request.message)
        if not validation['valid']:
            return create_error_response(
                "validation_error", 
                '; '.join(validation['errors'])
            )
        
        # Start or resume conversation
        if chat_request.session_id and chat_request.session_id in active_sessions:
            engine.current_session_id = chat_request.session_id
        else:
            session_id = engine.start_conversation(chat_request.user_id)
            active_sessions[session_id] = {
                'user_id': chat_request.user_id,
                'created_at': datetime.now()
            }
        
        # Process message with performance tracking
        with PerformanceTimer("Chat processing"):
            response_data = engine.process_message(
                validation['cleaned_text'],
                chat_request.user_id
            )
        
        # Schedule cleanup of old sessions in background
        background_tasks.add_task(cleanup_old_sessions)
        
        return create_success_response(response_data)
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        return create_error_response("server_error", "An internal error occurred")


@app.get("/api/conversation/stats/{user_id}")
async def get_conversation_stats(
    user_id: str,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Get conversation statistics for a user."""
    try:
        stats = engine.conversation_memory.get_user_conversation_stats(user_id)
        return create_success_response(stats)
    except Exception as e:
        logging.error(f"Error getting conversation stats: {e}")
        return create_error_response("server_error", str(e))


@app.get("/api/conversation/history/{user_id}")
async def get_conversation_history(
    user_id: str,
    limit: int = 10,
    days: int = 7,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Get conversation history for a user."""
    try:
        history = engine.conversation_memory.get_recent_conversations(
            user_id, limit, days
        )
        return create_success_response(history)
    except Exception as e:
        logging.error(f"Error getting conversation history: {e}")
        return create_error_response("server_error", str(e))


@app.get("/api/learning/insights")
async def get_learning_insights(
    user_id: Optional[str] = None,
    days: int = 30,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Get learning insights and analytics."""
    try:
        insights = engine.learning_system.get_learning_insights(user_id, days)
        return create_success_response(insights)
    except Exception as e:
        logging.error(f"Error getting learning insights: {e}")
        return create_error_response("server_error", str(e))


@app.get("/api/user/preferences/{user_id}")
async def get_user_preferences(
    user_id: str,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Get learned preferences for a user."""
    try:
        preferences = engine.learning_system.get_user_preferences(user_id)
        return create_success_response(preferences)
    except Exception as e:
        logging.error(f"Error getting user preferences: {e}")
        return create_error_response("server_error", str(e))


@app.post("/api/conversation/end/{session_id}")
async def end_conversation(
    session_id: str,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """End a conversation session."""
    try:
        if session_id in active_sessions:
            engine.current_session_id = session_id
            engine.end_conversation()
            del active_sessions[session_id]
            
            return create_success_response({"message": "Conversation ended successfully"})
        else:
            return create_error_response("not_found", "Session not found")
            
    except Exception as e:
        logging.error(f"Error ending conversation: {e}")
        return create_error_response("server_error", str(e))


@app.get("/api/analytics/trends")
async def get_conversation_trends(
    user_id: Optional[str] = None,
    days: int = 30,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Get conversation trends and analytics."""
    try:
        trends = engine.conversation_memory.get_conversation_trends(user_id, days)
        return create_success_response(trends)
    except Exception as e:
        logging.error(f"Error getting conversation trends: {e}")
        return create_error_response("server_error", str(e))


@app.get("/api/search/conversations")
async def search_conversations(
    query: str,
    user_id: Optional[str] = None,
    limit: int = 10,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Search conversations by content."""
    try:
        if not query.strip():
            return create_error_response("validation_error", "Search query cannot be empty")
        
        results = engine.conversation_memory.search_conversations(query, user_id, limit)
        return create_success_response(results)
    except Exception as e:
        logging.error(f"Error searching conversations: {e}")
        return create_error_response("server_error", str(e))


@app.delete("/api/admin/cleanup")
async def cleanup_old_data(
    days: int = 30,
    engine: ChatbotEngine = Depends(get_chatbot_engine)
):
    """Admin endpoint to cleanup old conversation data."""
    try:
        engine.conversation_memory.cleanup_old_conversations(days)
        return create_success_response({"message": f"Cleaned up data older than {days} days"})
    except Exception as e:
        logging.error(f"Error in cleanup: {e}")
        return create_error_response("server_error", str(e))


def cleanup_old_sessions():
    """Background task to cleanup old inactive sessions."""
    global active_sessions
    
    cutoff_time = datetime.now() - timedelta(hours=1)  # 1 hour timeout
    
    sessions_to_remove = [
        session_id for session_id, data in active_sessions.items()
        if data['created_at'] < cutoff_time
    ]
    
    for session_id in sessions_to_remove:
        try:
            del active_sessions[session_id]
        except KeyError:
            pass
    
    if sessions_to_remove:
        logging.info(f"Cleaned up {len(sessions_to_remove)} old sessions")


def main(host: str = "0.0.0.0", port: int = None, reload: bool = False):
    """Run the FastAPI server."""
    if port is None:
        port = config.API_PORT if config else 8000
    
    uvicorn.run(
        "chatbot.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main(reload=True)