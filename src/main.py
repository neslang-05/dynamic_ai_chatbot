"""
Main entry point for the Dynamic AI Chatbot.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from api.main import create_app
from config import settings
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


async def main():
    """Main application entry point."""
    try:
        logger.info("Starting Dynamic AI Chatbot...")
        logger.info(f"Configuration: Host={settings.api_host}, Port={settings.api_port}")
        
        # Create and run the application
        app = create_app()
        
        import uvicorn
        await uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload,
            log_level=settings.log_level.lower()
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())