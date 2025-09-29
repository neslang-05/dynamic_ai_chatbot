"""
Intent recognition using BERT-based models.
"""
import re
from typing import Dict, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

from models import Intent, IntentType
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class IntentRecognizer:
    """BERT-based intent recognition system."""
    
    def __init__(self):
        self.model_name = settings.intent_model_name
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self.rules = self._load_intent_rules()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the BERT model for intent classification."""
        try:
            logger.info(f"Loading intent recognition model: {self.model_name}")
            
            # For now, we'll use a simple sentiment classifier as a placeholder
            # In production, you would fine-tune BERT on your intent dataset
            self.classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            logger.info("Intent recognition model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load intent recognition model: {e}")
            logger.info("Falling back to rule-based intent recognition")
            self.classifier = None
    
    def _load_intent_rules(self) -> Dict[IntentType, List[str]]:
        """Load rule-based intent patterns."""
        return {
            IntentType.GREETING: [
                r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
                r'\b(greetings|salutations)\b'
            ],
            IntentType.GOODBYE: [
                r'\b(bye|goodbye|see you|farewell|take care)\b',
                r'\b(talk to you later|ttyl|catch you later)\b'
            ],
            IntentType.QUESTION: [
                r'\b(what|when|where|why|how|who|which|can you tell me)\b',
                r'\?',
                r'\b(do you know|could you explain|help me understand)\b'
            ],
            IntentType.REQUEST: [
                r'\b(please|could you|would you|can you)\b',
                r'\b(i need|i want|i would like)\b'
            ],
            IntentType.HELP: [
                r'\b(help|assist|support)\b',
                r'\b(i don\'t understand|confused|lost)\b'
            ],
            IntentType.COMPLAINT: [
                r'\b(problem|issue|wrong|error|broken|not working)\b',
                r'\b(frustrated|annoyed|angry)\b'
            ],
            IntentType.COMPLIMENT: [
                r'\b(thank|thanks|great|awesome|excellent|good job)\b',
                r'\b(appreciate|grateful|helpful)\b'
            ]
        }
    
    async def recognize_intent(self, text: str) -> Intent:
        """Recognize intent from text using hybrid approach."""
        try:
            # First try rule-based recognition
            rule_intent = self._rule_based_intent(text)
            if rule_intent.confidence > 0.7:
                return rule_intent
            
            # If rule-based has low confidence, try ML model
            if self.classifier:
                ml_intent = await self._model_based_intent(text)
                # Combine rule-based and ML results
                if ml_intent.confidence > rule_intent.confidence:
                    return ml_intent
            
            return rule_intent
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return Intent(intent=IntentType.UNKNOWN, confidence=0.1)
    
    def _rule_based_intent(self, text: str) -> Intent:
        """Rule-based intent recognition."""
        text_lower = text.lower()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, patterns in self.rules.items():
            confidence = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
                    confidence += 0.3
            
            # Normalize confidence based on number of patterns
            if matches > 0:
                confidence = min(confidence, 1.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_type
        
        return Intent(intent=best_intent, confidence=best_confidence)
    
    async def _model_based_intent(self, text: str) -> Intent:
        """ML model-based intent recognition."""
        try:
            # This is a placeholder implementation
            # In production, you would use a fine-tuned BERT model for intent classification
            
            # For now, we'll map sentiment to basic intents
            results = self.classifier(text)
            
            # Simple mapping based on confidence
            confidence = results[0]['score'] if results else 0.1
            
            # Basic mapping logic (this would be replaced with proper intent classification)
            if 'question' in text.lower() or '?' in text:
                return Intent(intent=IntentType.QUESTION, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['help', 'assist']):
                return Intent(intent=IntentType.HELP, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['hello', 'hi', 'hey']):
                return Intent(intent=IntentType.GREETING, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['bye', 'goodbye']):
                return Intent(intent=IntentType.GOODBYE, confidence=min(confidence + 0.2, 1.0))
            else:
                return Intent(intent=IntentType.UNKNOWN, confidence=confidence)
                
        except Exception as e:
            logger.error(f"Error in model-based intent recognition: {e}")
            return Intent(intent=IntentType.UNKNOWN, confidence=0.1)