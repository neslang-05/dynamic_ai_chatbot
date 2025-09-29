"""
Advanced NLP processor for message analysis and response generation.
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
import numpy as np

# Optional imports - graceful fallback if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        pipeline, AutoModelForSequenceClassification
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    nltk = None
    NLTK_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Download required NLTK data if available
if NLTK_AVAILABLE:
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon')

    try:
        nltk.data.find('punkt')
    except LookupError:
        nltk.download('punkt')


class NLPProcessor:
    """
    Advanced NLP processor with sentiment analysis, entity recognition,
    and intelligent response generation capabilities.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self._load_models()
        
        # Initialize NLTK components if available
        if NLTK_AVAILABLE:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        else:
            self.sentiment_analyzer = None
        
        self.logger.info("NLP Processor initialized successfully")
    
    def _load_models(self):
        """Load required ML models."""
        try:
            if not TRANSFORMERS_AVAILABLE or not TORCH_AVAILABLE:
                self.logger.warning("Transformers or PyTorch not available, using fallback implementations")
                self._init_fallback_models()
                return
            
            # Load conversational model for response generation
            model_name = getattr(self.config, 'MODEL_NAME', 'microsoft/DialoGPT-medium')
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load sentence transformer for semantic similarity
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            else:
                self.sentence_model = None
            
            # Initialize emotion classifier
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("All NLP models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            # Fallback to basic implementations
            self._init_fallback_models()
    
    def _init_fallback_models(self):
        """Initialize fallback models if main models fail to load."""
        self.logger.warning("Using fallback NLP implementations")
        self.tokenizer = None
        self.model = None
        self.sentence_model = None
        self.emotion_classifier = None
    
    def analyze_message(self, message: str) -> Dict:
        """
        Perform comprehensive NLP analysis of user message.
        
        Returns:
            Dict containing sentiment, emotions, entities, intent, etc.
        """
        analysis = {
            "original_message": message,
            "cleaned_message": self._clean_text(message),
            "confidence": 0.5  # Base confidence
        }
        
        try:
            # Sentiment analysis
            analysis["sentiment"] = self._analyze_sentiment(message)
            
            # Emotion detection
            analysis["emotions"] = self._detect_emotions(message)
            
            # Entity extraction
            analysis["entities"] = self._extract_entities(message)
            
            # Intent classification
            analysis["intent"] = self._classify_intent(message)
            
            # Topic extraction
            analysis["topics"] = self._extract_topics(message)
            
            # Question detection
            analysis["is_question"] = self._is_question(message)
            
            # Complexity analysis
            analysis["complexity"] = self._analyze_complexity(message)
            
            # Update confidence based on analysis quality
            analysis["confidence"] = self._calculate_analysis_confidence(analysis)
            
        except Exception as e:
            self.logger.error(f"Error in message analysis: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def generate_response(self, message: str, context: Dict, 
                         similar_conversations: List, nlp_analysis: Dict) -> str:
        """
        Generate intelligent response using context and analysis.
        """
        try:
            # If we have the conversational model, use it
            if self.model and self.tokenizer:
                return self._generate_model_response(message, context, nlp_analysis)
            else:
                return self._generate_rule_based_response(message, context, nlp_analysis)
        
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(nlp_analysis)
    
    def _generate_model_response(self, message: str, context: Dict, nlp_analysis: Dict) -> str:
        """Generate response using the conversational AI model."""
        try:
            # Prepare conversation history for context
            chat_history_ids = None
            
            # Add context from conversation
            if context.get("recent_history"):
                # Build conversation context
                conversation_text = self._build_conversation_context(context["recent_history"])
                if conversation_text:
                    inputs = self.tokenizer.encode(
                        conversation_text + self.tokenizer.eos_token,
                        return_tensors='pt'
                    )
                    chat_history_ids = inputs
            
            # Encode the new user input
            new_user_input_ids = self.tokenizer.encode(
                message + self.tokenizer.eos_token, 
                return_tensors='pt'
            )
            
            # Concatenate with chat history if available
            if chat_history_ids is not None:
                bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
            else:
                bot_input_ids = new_user_input_ids
            
            # Generate response
            with torch.no_grad():
                chat_history_ids = self.model.generate(
                    bot_input_ids,
                    max_length=bot_input_ids.shape[-1] + 50,
                    num_beams=5,
                    no_repeat_ngram_size=3,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Clean up response
            response = self._clean_generated_response(response)
            
            # If response is empty or too short, use fallback
            if len(response.strip()) < 5:
                return self._generate_rule_based_response(message, context, nlp_analysis)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in model response generation: {e}")
            return self._generate_rule_based_response(message, context, nlp_analysis)
    
    def _generate_rule_based_response(self, message: str, context: Dict, nlp_analysis: Dict) -> str:
        """Generate response using rule-based approach."""
        sentiment = nlp_analysis.get("sentiment", {})
        emotions = nlp_analysis.get("emotions", [])
        is_question = nlp_analysis.get("is_question", False)
        intent = nlp_analysis.get("intent", "general")
        
        # Handle different intents and emotions
        if is_question:
            if "what" in message.lower() or "how" in message.lower():
                return self._get_informational_response(message, context)
            elif "why" in message.lower():
                return self._get_explanatory_response(message, context)
            else:
                return self._get_general_question_response(message, context)
        
        # Handle emotional responses
        if emotions:
            primary_emotion = emotions[0] if isinstance(emotions, list) else emotions
            if isinstance(primary_emotion, dict):
                emotion_label = primary_emotion.get("label", "").lower()
            else:
                emotion_label = str(primary_emotion).lower()
            
            if "sad" in emotion_label or "disappointment" in emotion_label:
                return "I'm sorry to hear you're feeling that way. Is there anything I can help you with?"
            elif "joy" in emotion_label or "happiness" in emotion_label:
                return "That's wonderful! I'm glad you're feeling positive. What's making you happy?"
            elif "anger" in emotion_label or "frustration" in emotion_label:
                return "I understand you might be frustrated. Let's see how I can help make things better."
        
        # Handle sentiment
        if sentiment.get("compound", 0) < -0.5:
            return "I sense you might be having a tough time. How can I help you today?"
        elif sentiment.get("compound", 0) > 0.5:
            return "You seem to be in a good mood! That's great to hear. What can I do for you?"
        
        # Default conversational responses
        responses = [
            "That's interesting! Can you tell me more about that?",
            "I see what you mean. What would you like to explore further?",
            "Thanks for sharing that with me. How can I help you today?",
            "I appreciate you talking with me. What's on your mind?",
            "That gives me something to think about. What else would you like to discuss?"
        ]
        
        # Select response based on message content
        import random
        return random.choice(responses)
    
    def _get_fallback_response(self, nlp_analysis: Dict) -> str:
        """Get fallback response when all else fails."""
        fallback_responses = [
            "I'm here to help! Could you please rephrase that?",
            "That's an interesting point. Can you elaborate?",
            "I want to make sure I understand correctly. Could you provide more details?",
            "Thanks for your message. How can I assist you better?",
            "I'm always learning from our conversations. What would you like to talk about?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text)
        
        return text
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using VADER or fallback."""
        try:
            if self.sentiment_analyzer:
                scores = self.sentiment_analyzer.polarity_scores(text)
                
                # Determine overall sentiment
                compound = scores['compound']
                if compound >= 0.05:
                    overall = 'positive'
                elif compound <= -0.05:
                    overall = 'negative'
                else:
                    overall = 'neutral'
                
                return {
                    'positive': scores['pos'],
                    'neutral': scores['neu'],
                    'negative': scores['neg'],
                    'compound': compound,
                    'overall': overall
                }
            else:
                # Basic sentiment analysis using keywords
                positive_words = ['happy', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'like', 'excited', 'joy']
                negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'angry', 'upset', 'frustrated', 'disappointed']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    overall = 'positive'
                    compound = 0.3
                elif neg_count > pos_count:
                    overall = 'negative'
                    compound = -0.3
                else:
                    overall = 'neutral'
                    compound = 0.0
                
                return {
                    'positive': pos_count / max(1, pos_count + neg_count),
                    'neutral': 0.5,
                    'negative': neg_count / max(1, pos_count + neg_count),
                    'compound': compound,
                    'overall': overall
                }
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {'overall': 'neutral', 'compound': 0.0}
    
    def _detect_emotions(self, text: str) -> List[Dict]:
        """Detect emotions in text."""
        try:
            if self.emotion_classifier:
                emotions = self.emotion_classifier(text)
                return emotions[:3]  # Top 3 emotions
            else:
                # Basic emotion detection based on keywords
                emotion_keywords = {
                    'joy': ['happy', 'glad', 'pleased', 'delighted', 'excited'],
                    'sadness': ['sad', 'unhappy', 'depressed', 'down', 'upset'],
                    'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
                    'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
                    'surprise': ['surprised', 'amazed', 'shocked', 'astonished']
                }
                
                detected = []
                text_lower = text.lower()
                for emotion, keywords in emotion_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        detected.append({'label': emotion, 'score': 0.7})
                
                return detected[:3]
        
        except Exception as e:
            self.logger.error(f"Error in emotion detection: {e}")
            return []
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities and important words."""
        try:
            # Simple entity extraction using patterns
            entities = []
            
            # Extract capitalized words (potential proper nouns)
            capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
            entities.extend(capitalized)
            
            # Extract numbers
            numbers = re.findall(r'\b\d+\b', text)
            entities.extend(numbers)
            
            # Extract potential time references
            time_patterns = re.findall(r'\b(?:today|tomorrow|yesterday|tonight|morning|afternoon|evening)\b', text.lower())
            entities.extend(time_patterns)
            
            return list(set(entities))  # Remove duplicates
        
        except Exception as e:
            self.logger.error(f"Error in entity extraction: {e}")
            return []
    
    def _classify_intent(self, text: str) -> str:
        """Classify user intent."""
        text_lower = text.lower()
        
        # Question patterns
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', '?']):
            return 'question'
        
        # Greeting patterns
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'
        
        # Help patterns
        if any(word in text_lower for word in ['help', 'assist', 'support', 'need help']):
            return 'help_request'
        
        # Goodbye patterns
        if any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            return 'goodbye'
        
        # Complaint patterns
        if any(word in text_lower for word in ['problem', 'issue', 'wrong', 'error', 'broken']):
            return 'complaint'
        
        return 'general'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        try:
            # Simple keyword-based topic extraction
            topics = []
            
            # Technology topics
            tech_keywords = ['computer', 'software', 'programming', 'code', 'app', 'website', 'technology']
            if any(word in text.lower() for word in tech_keywords):
                topics.append('technology')
            
            # Personal topics
            personal_keywords = ['family', 'friend', 'work', 'job', 'life', 'personal']
            if any(word in text.lower() for word in personal_keywords):
                topics.append('personal')
            
            # Business topics
            business_keywords = ['business', 'company', 'market', 'sales', 'profit', 'customer']
            if any(word in text.lower() for word in business_keywords):
                topics.append('business')
            
            # Health topics
            health_keywords = ['health', 'doctor', 'medicine', 'sick', 'hospital', 'treatment']
            if any(word in text.lower() for word in health_keywords):
                topics.append('health')
            
            return topics
        
        except Exception as e:
            self.logger.error(f"Error in topic extraction: {e}")
            return []
    
    def _is_question(self, text: str) -> bool:
        """Determine if text is a question."""
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose', 'whom']
        text_lower = text.lower().split()
        
        return any(word in question_words for word in text_lower[:3])  # Check first 3 words
    
    def _analyze_complexity(self, text: str) -> Dict:
        """Analyze text complexity."""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'complexity_score': min(1.0, len(words) / 20)  # Normalize to 0-1
        }
    
    def _calculate_analysis_confidence(self, analysis: Dict) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on available analysis
        if analysis.get("sentiment", {}).get("compound", 0) != 0:
            confidence += 0.1
        
        if analysis.get("emotions"):
            confidence += 0.1
        
        if analysis.get("entities"):
            confidence += 0.1
        
        if analysis.get("topics"):
            confidence += 0.1
        
        if analysis.get("intent") != "general":
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _build_conversation_context(self, recent_history: List) -> str:
        """Build conversation context from recent history."""
        context_parts = []
        for conv in recent_history[-3:]:  # Last 3 conversations
            if isinstance(conv, dict):
                user_msg = conv.get('user_message', '')
                bot_msg = conv.get('bot_response', '')
                if user_msg and bot_msg:
                    context_parts.append(f"User: {user_msg}")
                    context_parts.append(f"Bot: {bot_msg}")
        
        return ' '.join(context_parts)
    
    def _clean_generated_response(self, response: str) -> str:
        """Clean up generated response."""
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response.strip())
        
        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 5:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Ensure proper capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        return response
    
    def _get_informational_response(self, message: str, context: Dict) -> str:
        """Generate informational response."""
        responses = [
            "That's a great question! Based on what I know, here's what I can tell you...",
            "Let me help you with that information...",
            "I'd be happy to explain that to you...",
            "Here's what I understand about that topic..."
        ]
        import random
        return random.choice(responses)
    
    def _get_explanatory_response(self, message: str, context: Dict) -> str:
        """Generate explanatory response."""
        responses = [
            "That's an interesting question about the 'why' behind things...",
            "Let me break that down for you...",
            "The reasoning behind that is quite interesting...",
            "There are several factors that contribute to that..."
        ]
        import random
        return random.choice(responses)
    
    def _get_general_question_response(self, message: str, context: Dict) -> str:
        """Generate general question response."""
        responses = [
            "That's a thoughtful question. Let me consider that...",
            "I appreciate you asking that. Here's my perspective...",
            "That's something worth exploring together...",
            "Let me help you think through that..."
        ]
        import random
        return random.choice(responses)
    
    def get_sentence_embedding(self, text: str) -> np.ndarray:
        """Get sentence embedding for semantic similarity."""
        try:
            if self.sentence_model:
                embedding = self.sentence_model.encode(text)
                return embedding
            else:
                # Fallback: simple word count vector (very basic)
                words = text.lower().split()
                return np.array([len(words), len(set(words))])  # Basic features
        except Exception as e:
            self.logger.error(f"Error generating sentence embedding: {e}")
            return np.array([0.0, 0.0])