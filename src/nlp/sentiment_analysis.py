"""
Sentiment analysis and emotion detection.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from typing import Dict, Any

from models import Sentiment, SentimentType, EmotionType
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis and emotion detection system."""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.emotion_classifier = None
        self.sentiment_classifier = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment and emotion analysis models."""
        try:
            logger.info("Loading sentiment analysis models...")
            
            # Initialize VADER (rule-based sentiment)
            logger.info("VADER sentiment analyzer loaded")
            
            # Initialize transformer-based sentiment classifier
            try:
                self.sentiment_classifier = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                logger.info("Transformer-based sentiment classifier loaded")
            except Exception as e:
                logger.warning(f"Failed to load transformer sentiment model: {e}")
            
            # Initialize emotion classifier
            try:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    return_all_scores=True
                )
                logger.info("Emotion classifier loaded")
            except Exception as e:
                logger.warning(f"Failed to load emotion model: {e}")
                
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
    
    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment and emotion from text."""
        try:
            # Get VADER sentiment scores
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Get transformer-based sentiment if available
            transformer_sentiment = None
            if self.sentiment_classifier:
                transformer_sentiment = await self._get_transformer_sentiment(text)
            
            # Get emotion if available
            emotion = None
            if self.emotion_classifier:
                emotion = await self._get_emotion(text)
            
            # Combine results
            final_sentiment = self._combine_sentiment_results(vader_scores, transformer_sentiment)
            
            return Sentiment(
                sentiment=final_sentiment['sentiment'],
                confidence=final_sentiment['confidence'],
                emotion=emotion
            )
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return Sentiment(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.1
            )
    
    async def _get_transformer_sentiment(self, text: str) -> Dict[str, Any]:
        """Get sentiment from transformer model."""
        try:
            results = self.sentiment_classifier(text)
            
            # Map model labels to our sentiment types
            label_mapping = {
                'LABEL_0': SentimentType.NEGATIVE,
                'LABEL_1': SentimentType.NEUTRAL,
                'LABEL_2': SentimentType.POSITIVE,
                'NEGATIVE': SentimentType.NEGATIVE,
                'NEUTRAL': SentimentType.NEUTRAL,
                'POSITIVE': SentimentType.POSITIVE
            }
            
            best_result = max(results, key=lambda x: x['score'])
            sentiment = label_mapping.get(best_result['label'], SentimentType.NEUTRAL)
            
            return {
                'sentiment': sentiment,
                'confidence': best_result['score']
            }
            
        except Exception as e:
            logger.error(f"Error in transformer sentiment analysis: {e}")
            return {'sentiment': SentimentType.NEUTRAL, 'confidence': 0.1}
    
    async def _get_emotion(self, text: str) -> EmotionType:
        """Get emotion from text."""
        try:
            results = self.emotion_classifier(text)
            
            # Map model labels to our emotion types
            label_mapping = {
                'joy': EmotionType.JOY,
                'sadness': EmotionType.SADNESS,
                'anger': EmotionType.ANGER,
                'fear': EmotionType.FEAR,
                'surprise': EmotionType.SURPRISE,
                'love': EmotionType.LOVE,
                'neutral': EmotionType.NEUTRAL
            }
            
            best_result = max(results, key=lambda x: x['score'])
            emotion = label_mapping.get(best_result['label'].lower(), EmotionType.NEUTRAL)
            
            # Only return emotion if confidence is high enough
            if best_result['score'] > 0.6:
                return emotion
            else:
                return EmotionType.NEUTRAL
                
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return EmotionType.NEUTRAL
    
    def _combine_sentiment_results(self, vader_scores: Dict, transformer_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Combine VADER and transformer sentiment results."""
        
        # Convert VADER scores to sentiment type
        compound = vader_scores['compound']
        if compound >= 0.05:
            vader_sentiment = SentimentType.POSITIVE
            vader_confidence = compound
        elif compound <= -0.05:
            vader_sentiment = SentimentType.NEGATIVE
            vader_confidence = abs(compound)
        else:
            vader_sentiment = SentimentType.NEUTRAL
            vader_confidence = 1.0 - abs(compound)
        
        # If no transformer result, use VADER only
        if not transformer_result:
            return {
                'sentiment': vader_sentiment,
                'confidence': vader_confidence
            }
        
        # Combine results by averaging confidence
        if vader_sentiment == transformer_result['sentiment']:
            # Both agree, increase confidence
            combined_confidence = min((vader_confidence + transformer_result['confidence']) / 2 + 0.1, 1.0)
            return {
                'sentiment': vader_sentiment,
                'confidence': combined_confidence
            }
        else:
            # Disagree, use the one with higher confidence
            if vader_confidence > transformer_result['confidence']:
                return {
                    'sentiment': vader_sentiment,
                    'confidence': vader_confidence * 0.8  # Reduce confidence due to disagreement
                }
            else:
                return {
                    'sentiment': transformer_result['sentiment'],
                    'confidence': transformer_result['confidence'] * 0.8
                }