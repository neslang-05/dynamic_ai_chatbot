"""
Configuration management for the dynamic AI chatbot.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration management class for the chatbot."""
    
    def __init__(self, env_file: Optional[str] = None):
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Chatbot settings
        self.CHATBOT_NAME = os.getenv('CHATBOT_NAME', 'DynamicAI')
        self.MODEL_NAME = os.getenv('MODEL_NAME', 'microsoft/DialoGPT-medium')
        
        # Conversation settings
        self.MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', '10'))
        self.CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
        
        # Learning settings
        self.LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))
        
        # Server settings
        self.API_PORT = int(os.getenv('API_PORT', '8000'))
        self.WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
        
        # Database settings
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot_memory.db')
        
        # Logging settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Model settings
        self.USE_GPU = os.getenv('USE_GPU', 'False').lower() == 'true'
        self.MAX_RESPONSE_LENGTH = int(os.getenv('MAX_RESPONSE_LENGTH', '100'))
        self.TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
        
        # Learning system settings
        self.ENABLE_LEARNING = os.getenv('ENABLE_LEARNING', 'True').lower() == 'true'
        self.MIN_LEARNING_CONFIDENCE = float(os.getenv('MIN_LEARNING_CONFIDENCE', '0.6'))
        
        # Memory management
        self.CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', '30'))
        self.MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '1000'))
        
        # Security settings
        self.API_KEY = os.getenv('API_KEY', '')
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
        
        # Feature flags
        self.ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'True').lower() == 'true'
        self.ENABLE_EMOTION_DETECTION = os.getenv('ENABLE_EMOTION_DETECTION', 'True').lower() == 'true'
        self.ENABLE_ENTITY_EXTRACTION = os.getenv('ENABLE_ENTITY_EXTRACTION', 'True').lower() == 'true'
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('chatbot.log')
            ]
        )
    
    def get_model_config(self) -> dict:
        """Get model-specific configuration."""
        return {
            'model_name': self.MODEL_NAME,
            'max_length': self.MAX_RESPONSE_LENGTH,
            'temperature': self.TEMPERATURE,
            'use_gpu': self.USE_GPU
        }
    
    def get_database_config(self) -> dict:
        """Get database configuration."""
        return {
            'url': self.DATABASE_URL,
            'cleanup_days': self.CLEANUP_DAYS,
            'max_history': self.MAX_CONVERSATION_HISTORY
        }
    
    def get_learning_config(self) -> dict:
        """Get learning system configuration."""
        return {
            'enabled': self.ENABLE_LEARNING,
            'learning_rate': self.LEARNING_RATE,
            'min_confidence': self.MIN_LEARNING_CONFIDENCE,
            'confidence_threshold': self.CONFIDENCE_THRESHOLD
        }
    
    def get_feature_flags(self) -> dict:
        """Get feature flag configuration."""
        return {
            'sentiment_analysis': self.ENABLE_SENTIMENT_ANALYSIS,
            'emotion_detection': self.ENABLE_EMOTION_DETECTION,
            'entity_extraction': self.ENABLE_ENTITY_EXTRACTION
        }
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        try:
            # Check required settings
            if not self.CHATBOT_NAME:
                raise ValueError("CHATBOT_NAME is required")
            
            if not self.MODEL_NAME:
                raise ValueError("MODEL_NAME is required")
            
            # Check numeric ranges
            if not (0.0 <= self.CONFIDENCE_THRESHOLD <= 1.0):
                raise ValueError("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
            
            if not (0.0 <= self.LEARNING_RATE <= 1.0):
                raise ValueError("LEARNING_RATE must be between 0.0 and 1.0")
            
            if not (0.0 <= self.TEMPERATURE <= 2.0):
                raise ValueError("TEMPERATURE must be between 0.0 and 2.0")
            
            if self.MAX_HISTORY_LENGTH < 1:
                raise ValueError("MAX_HISTORY_LENGTH must be at least 1")
            
            if self.API_PORT < 1 or self.API_PORT > 65535:
                raise ValueError("API_PORT must be between 1 and 65535")
            
            if self.WEB_PORT < 1 or self.WEB_PORT > 65535:
                raise ValueError("WEB_PORT must be between 1 and 65535")
            
            return True
            
        except ValueError as e:
            logging.error(f"Configuration validation error: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"""
Dynamic AI Chatbot Configuration:
- Chatbot Name: {self.CHATBOT_NAME}
- Model: {self.MODEL_NAME}
- Max History: {self.MAX_HISTORY_LENGTH}
- Confidence Threshold: {self.CONFIDENCE_THRESHOLD}
- Learning Rate: {self.LEARNING_RATE}
- API Port: {self.API_PORT}
- Web Port: {self.WEB_PORT}
- Database: {self.DATABASE_URL}
- Log Level: {self.LOG_LEVEL}
- Learning Enabled: {self.ENABLE_LEARNING}
"""