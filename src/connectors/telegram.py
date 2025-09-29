"""
Telegram webhook connector for the Dynamic AI Chatbot.
"""
import json
from typing import Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from models import ChatRequest, Platform
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramConnector:
    """Telegram webhook connector."""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
    
    def parse_telegram_update(self, payload: Dict[str, Any]) -> ChatRequest:
        """Parse Telegram update into ChatRequest."""
        try:
            message = payload.get('message', {})
            
            # Extract message details
            text = message.get('text', '')
            user = message.get('from', {})
            chat = message.get('chat', {})
            
            user_id = str(user.get('id', 'unknown'))
            chat_id = str(chat.get('id', 'unknown'))
            
            # Create session ID from user and chat
            session_id = f"telegram_{user_id}_{chat_id}"
            
            return ChatRequest(
                message=text,
                user_id=user_id,
                session_id=session_id,
                platform=Platform.TELEGRAM,
                metadata={
                    'chat_id': chat_id,
                    'message_id': message.get('message_id'),
                    'username': user.get('username'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'chat_type': chat.get('type')
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Telegram update: {e}")
            raise HTTPException(status_code=400, detail="Invalid Telegram update format")
    
    async def handle_webhook(self, request: Request) -> JSONResponse:
        """Handle Telegram webhook request."""
        try:
            # Get request data
            request_body = await request.body()
            payload = json.loads(request_body.decode('utf-8'))
            
            # Check if it's a message update
            if 'message' not in payload:
                return JSONResponse({'status': 'ok'})
            
            message = payload['message']
            
            # Skip non-text messages
            if 'text' not in message:
                return JSONResponse({'status': 'ok'})
            
            # Parse and process message
            chat_request = self.parse_telegram_update(payload)
            
            # Import here to avoid circular imports
            from api.dependencies import get_chat_manager
            chat_manager = get_chat_manager()
            
            # Process message
            response = await chat_manager.process_message(chat_request)
            
            # Send response back to Telegram
            await self._send_telegram_response(
                chat_id=chat_request.metadata['chat_id'],
                text=response.response
            )
            
            return JSONResponse({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Error handling Telegram webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _send_telegram_response(self, chat_id: str, text: str):
        """Send response back to Telegram."""
        # This is a placeholder - in production, you would use the Telegram Bot API
        logger.info(f"Would send to Telegram chat {chat_id}: {text}")
        
        # Example implementation would use httpx to call Telegram API:
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     await client.post(
        #         f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
        #         json={"chat_id": chat_id, "text": text}
        #     )