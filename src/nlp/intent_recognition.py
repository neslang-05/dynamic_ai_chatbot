"""
Intent recognition using BERT-based models.
"""
import re
from typing import Dict, List

# Try to import transformers.pipeline; if unavailable, we'll fall back to rule-based only
try:
    from transformers import pipeline  # type: ignore
    _HAS_TRANSFORMERS = True
except Exception:
    pipeline = None
    _HAS_TRANSFORMERS = False

from models import IntentPrediction, IntentType
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

            # Attempt to load a text-classification model specified by settings
            # If not available or loading fails, fall back to rule-based recognition
            if not _HAS_TRANSFORMERS:
                logger.info("transformers package not available; using rule-based recognizer")
                self.classifier = None
                return

            if self.model_name:
                try:
                    self.classifier = pipeline(
                        "text-classification",
                        model=self.model_name,
                        return_all_scores=True
                    )
                    logger.info("Intent recognition model loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load intent model '{self.model_name}': {e}")
                    self.classifier = None
            else:
                logger.info("No intent model configured, using rule-based recognizer")
                self.classifier = None
            
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
    
    async def recognize_intent(self, text: str) -> IntentPrediction:
        """Recognize intent from text using hybrid approach."""
        try:
            # First try rule-based recognition
            rule_pred = self._rule_based_intent(text)
            if rule_pred.confidence > 0.7:
                return rule_pred
            
            # If rule-based has low confidence, try ML model
            if self.classifier:
                ml_pred = await self._model_based_intent(text)
                # Choose the prediction with higher confidence
                if ml_pred.confidence > rule_pred.confidence:
                    return ml_pred

            return rule_pred
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return IntentPrediction(intent=IntentType.UNKNOWN, confidence=0.1)
    
    def _rule_based_intent(self, text: str) -> IntentPrediction:
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

        return IntentPrediction(intent=best_intent, confidence=best_confidence)
    
    async def _model_based_intent(self, text: str) -> IntentPrediction:
        """ML model-based intent recognition."""
        try:
            # This is a placeholder implementation
            # In production, you would use a fine-tuned BERT model for intent classification
            
            # For now, we'll map sentiment to basic intents
            # Run classifier synchronously (HF pipelines are synchronous)
            results = self.classifier(text)

            # results may be a list of label/confidence dicts; pick the best score
            confidence = 0.1
            if results:
                # If return_all_scores=True, results is list of dicts
                if isinstance(results, list) and isinstance(results[0], dict):
                    # HuggingFace new format: [{'label': 'LABEL_0', 'score': 0.9}, ...]
                    best = max(results, key=lambda x: x.get('score', 0))
                    confidence = best.get('score', 0.1)
                elif isinstance(results, list) and isinstance(results[0], list):
                    # Sometimes pipelines return nested lists; flatten
                    flat = results[0]
                    best = max(flat, key=lambda x: x.get('score', 0))
                    confidence = best.get('score', 0.1)

            # Basic heuristic mapping from text to intents if classifier does not map to domain labels
            if 'question' in text.lower() or '?' in text:
                return IntentPrediction(intent=IntentType.QUESTION, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['help', 'assist']):
                return IntentPrediction(intent=IntentType.HELP, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['hello', 'hi', 'hey']):
                return IntentPrediction(intent=IntentType.GREETING, confidence=min(confidence + 0.2, 1.0))
            elif any(word in text.lower() for word in ['bye', 'goodbye']):
                return IntentPrediction(intent=IntentType.GOODBYE, confidence=min(confidence + 0.2, 1.0))
            else:
                return IntentPrediction(intent=IntentType.UNKNOWN, confidence=confidence)
                
        except Exception as e:
            logger.error(f"Error in model-based intent recognition: {e}")
            return IntentPrediction(intent=IntentType.UNKNOWN, confidence=0.1)