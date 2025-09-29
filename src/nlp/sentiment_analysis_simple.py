"""
Simplified sentiment analysis for basic demo.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any

from models import Sentiment, SentimentType, EmotionType
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SentimentAnalyzer:
    """Simplified sentiment analysis using VADER only."""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        logger.info("Simplified SentimentAnalyzer initialized")
    
    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment from text."""
        try:
            # Get VADER sentiment scores
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Convert VADER scores to sentiment type
            compound = vader_scores['compound']
            if compound >= 0.05:
                sentiment = SentimentType.POSITIVE
                confidence = compound
            elif compound <= -0.05:
                sentiment = SentimentType.NEGATIVE
                confidence = abs(compound)
            else:
                sentiment = SentimentType.NEUTRAL
                confidence = 1.0 - abs(compound)
            
            # Simple emotion detection based on keywords
            emotion = self._detect_emotion(text)
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentType.NEUTRAL
    
    def _detect_emotion(self, text: str) -> EmotionType:
        """Simple emotion detection based on keywords."""
        text_lower = text.lower()
        
        # Joy keywords
        if any(word in text_lower for word in ['happy', 'joy', 'excited', 'love', 'amazing', 'wonderful']):
            return EmotionType.JOY
        
        # Anger keywords
        if any(word in text_lower for word in ['angry', 'furious', 'mad', 'hate', 'terrible', 'awful']):
            return EmotionType.ANGER
        
        # Sadness keywords
        if any(word in text_lower for word in ['sad', 'depressed', 'crying', 'disappointed', 'sorry']):
            return EmotionType.SADNESS
        
        # Fear keywords
        if any(word in text_lower for word in ['scared', 'afraid', 'worried', 'anxious', 'nervous']):
            return EmotionType.FEAR
        
        # Surprise keywords
        if any(word in text_lower for word in ['wow', 'amazing', 'surprised', 'unexpected']):
            return EmotionType.SURPRISE
        
        # Love keywords
        if any(word in text_lower for word in ['love', 'adore', 'cherish']):
            return EmotionType.LOVE
        
        return EmotionType.NEUTRAL