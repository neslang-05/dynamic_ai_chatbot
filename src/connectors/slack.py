"""
Slack webhook connector for the Dynamic AI Chatbot.
"""
import hashlib
import hmac
import json
from typing import Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from models import ChatRequest, Platform
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SlackConnector:
    """Slack webhook connector."""
    
    def __init__(self):
        self.signing_secret = settings.slack_signing_secret
        self.bot_token = settings.slack_bot_token
    
    def verify_signature(self, request_body: bytes, timestamp: str, signature: str) -> bool:
        """Verify Slack request signature."""
        if not self.signing_secret:
            logger.warning("Slack signing secret not configured")
            return True  # Skip verification if not configured
        
        try:
            # Create signature string
            sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
            
            # Generate expected signature
            expected_signature = 'v0=' + hmac.new(
                self.signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying Slack signature: {e}")
            return False
    
    def parse_slack_event(self, payload: Dict[str, Any]) -> ChatRequest:
        """Parse Slack event into ChatRequest."""
        try:
            event = payload.get('event', {})
            
            # Extract message details
            text = event.get('text', '')
            user_id = event.get('user', 'unknown')
            channel_id = event.get('channel', 'unknown')
            
            # Create session ID from user and channel
            session_id = f"slack_{user_id}_{channel_id}"
            
            return ChatRequest(
                message=text,
                user_id=user_id,
                session_id=session_id,
                platform=Platform.SLACK,
                metadata={
                    'channel_id': channel_id,
                    'event_ts': event.get('ts'),
                    'team': payload.get('team_id')
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Slack event: {e}")
            raise HTTPException(status_code=400, detail="Invalid Slack event format")
    
    async def handle_webhook(self, request: Request) -> JSONResponse:
        """Handle Slack webhook request."""
        try:
            # Get request data
            request_body = await request.body()
            payload = json.loads(request_body.decode('utf-8'))
            
            # Verify signature if configured
            if self.signing_secret:
                timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
                signature = request.headers.get('X-Slack-Signature', '')
                
                if not self.verify_signature(request_body, timestamp, signature):
                    raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Handle URL verification
            if payload.get('type') == 'url_verification':
                return JSONResponse({'challenge': payload.get('challenge')})
            
            # Handle event
            if payload.get('type') == 'event_callback':
                event = payload.get('event', {})
                
                # Skip bot messages and DMs we don't want to handle
                if event.get('bot_id') or event.get('subtype'):
                    return JSONResponse({'status': 'ok'})
                
                # Parse and process message
                chat_request = self.parse_slack_event(payload)
                
                # Import here to avoid circular imports
                from api.dependencies import get_chat_manager
                chat_manager = get_chat_manager()
                
                # Process message
                response = await chat_manager.process_message(chat_request)
                
                # Send response back to Slack (this would need Slack Web API implementation)
                await self._send_slack_response(
                    channel=chat_request.metadata['channel_id'],
                    text=response.response
                )
                
                return JSONResponse({'status': 'ok'})
            
            return JSONResponse({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Error handling Slack webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _send_slack_response(self, channel: str, text: str):
        """Send response back to Slack."""
        # This is a placeholder - in production, you would use the Slack Web API
        # to send messages back to the channel
        logger.info(f"Would send to Slack channel {channel}: {text}")
        
        # Example implementation would use httpx to call Slack API:
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     await client.post(
        #         "https://slack.com/api/chat.postMessage",
        #         headers={"Authorization": f"Bearer {self.bot_token}"},
        #         json={"channel": channel, "text": text}
        #     )