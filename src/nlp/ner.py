"""
Named Entity Recognition (NER) using spaCy and transformers.
"""
import re
from typing import List, Dict, Any
from transformers import pipeline

from models import Entity
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NamedEntityRecognizer:
    """Named Entity Recognition system."""
    
    def __init__(self):
        self.ner_pipeline = None
        self.patterns = self._load_patterns()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the NER model."""
        try:
            logger.info("Loading NER model...")
            
            # Use a pre-trained NER model from transformers
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            
            logger.info("NER model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            logger.info("Falling back to pattern-based NER")
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for entity extraction."""
        return {
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
                r'\+\d{1,3}\s*\d{3,14}'
            ],
            'url': [
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            ],
            'money': [
                r'\$\d+(?:\.\d{2})?',
                r'\d+(?:\.\d{2})?\s*(?:dollars?|usd|€|euros?|£|pounds?)'
            ],
            'date': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
            ],
            'time': [
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?\b'
            ]
        }
    
    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from text."""
        try:
            entities = []
            
            # Try transformer-based NER first
            if self.ner_pipeline:
                transformer_entities = await self._extract_with_transformer(text)
                entities.extend(transformer_entities)
            
            # Add pattern-based entities
            pattern_entities = self._extract_with_patterns(text)
            entities.extend(pattern_entities)
            
            # Remove duplicates and merge overlapping entities
            entities = self._merge_entities(entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return []
    
    async def _extract_with_transformer(self, text: str) -> List[Entity]:
        """Extract entities using transformer model."""
        try:
            results = self.ner_pipeline(text)
            entities = []
            
            for result in results:
                entity = Entity(
                    type=result['entity_group'].lower(),
                    value=result['word'],
                    confidence=result['score'],
                    start=result['start'],
                    end=result['end']
                )
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in transformer-based NER: {e}")
            return []
    
    def _extract_with_patterns(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns."""
        entities = []
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        type=entity_type,
                        value=match.group(),
                        confidence=0.9,  # High confidence for pattern matches
                        start=match.start(),
                        end=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities and remove duplicates."""
        if not entities:
            return entities
        
        # Sort entities by start position
        entities.sort(key=lambda x: x.start)
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # Check for overlap
            if next_entity.start <= current.end and next_entity.start >= current.start:
                # Overlapping entities - keep the one with higher confidence
                if next_entity.confidence > current.confidence:
                    current = next_entity
                # If same confidence, keep the longer one
                elif next_entity.confidence == current.confidence:
                    if (next_entity.end - next_entity.start) > (current.end - current.start):
                        current = next_entity
            else:
                # No overlap, add current to merged list
                merged.append(current)
                current = next_entity
        
        # Add the last entity
        merged.append(current)
        
        return merged