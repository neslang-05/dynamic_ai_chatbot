"""
Main entry point for the Dynamic AI Chatbot.
"""
import sys
from pathlib import Path
import uvicorn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from api.main import create_app
from config import settings
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info("Starting Dynamic AI Chatbot...")
        logger.info(f"Configuration: Host={settings.api_host}, Port={settings.api_port}")
        
        if settings.api_reload:
            # Use import string for reload mode
            uvicorn.run(
                "api.main:create_app",
                host=settings.api_host,
                port=settings.api_port,
                reload=True,
                log_level=settings.log_level.lower(),
                factory=True
            )
        else:
            # Create the application object for non-reload mode
            app = create_app()
            uvicorn.run(
                app,
                host=settings.api_host,
                port=settings.api_port,
                reload=False,
                log_level=settings.log_level.lower()
            )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()