"""
Utility functions and helpers for the dynamic AI chatbot.
"""
import re
import json
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove or replace problematic characters
    text = re.sub(r'[^\w\s\.,!?;:\-\'"()]+', '', text)
    
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract potential keywords from text."""
    if not text:
        return []
    
    # Simple keyword extraction
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out short words and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
        'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those'
    }
    
    keywords = [word for word in words 
                if len(word) >= min_length and word not in stop_words]
    
    return list(set(keywords))  # Remove duplicates


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using word overlap."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def generate_session_id(user_id: str = "default") -> str:
    """Generate a unique session ID."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{user_id}_{timestamp}_{random_suffix}"


def hash_text(text: str) -> str:
    """Generate a hash for text (useful for deduplication)."""
    return hashlib.md5(text.encode()).hexdigest()


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string back to datetime."""
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            # Try ISO format
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_user_input(text: str, max_length: int = 1000) -> Dict[str, Any]:
    """Validate user input and return validation results."""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'cleaned_text': text
    }
    
    if not text or not text.strip():
        result['valid'] = False
        result['errors'].append('Input cannot be empty')
        return result
    
    # Check length
    if len(text) > max_length:
        result['valid'] = False
        result['errors'].append(f'Input too long (max {max_length} characters)')
    
    # Clean text
    cleaned = clean_text(text)
    result['cleaned_text'] = cleaned
    
    # Check for potential issues
    if len(cleaned) < len(text) * 0.5:
        result['warnings'].append('Input contained many special characters that were removed')
    
    # Check for repeated characters (possible spam)
    if re.search(r'(.)\1{10,}', text):
        result['warnings'].append('Input contains repeated characters')
    
    return result


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string with fallback."""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default


def extract_questions(text: str) -> List[str]:
    """Extract questions from text."""
    # Simple question extraction
    sentences = re.split(r'[.!?]+', text)
    questions = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check if it's a question
        if (sentence.endswith('?') or 
            any(sentence.lower().startswith(qw) for qw in 
                ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose'])):
            questions.append(sentence)
    
    return questions


def analyze_text_complexity(text: str) -> Dict[str, float]:
    """Analyze text complexity metrics."""
    if not text:
        return {'word_count': 0, 'sentence_count': 0, 'avg_word_length': 0, 'complexity_score': 0}
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    word_count = len(words)
    sentence_count = len(sentences)
    
    # Calculate average word length
    if words:
        avg_word_length = sum(len(word) for word in words) / len(words)
    else:
        avg_word_length = 0
    
    # Calculate complexity score (0-1 scale)
    complexity_score = 0
    
    if word_count > 0:
        # Factors that increase complexity
        complexity_score += min(0.3, word_count / 100)  # Length factor
        complexity_score += min(0.3, avg_word_length / 15)  # Word length factor
        
        # Sentence structure factor
        if sentence_count > 0:
            avg_words_per_sentence = word_count / sentence_count
            complexity_score += min(0.2, avg_words_per_sentence / 30)
        
        # Vocabulary diversity
        unique_words = len(set(word.lower() for word in words))
        diversity_ratio = unique_words / word_count
        complexity_score += diversity_ratio * 0.2
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_word_length': round(avg_word_length, 2),
        'complexity_score': round(min(1.0, complexity_score), 3)
    }


def get_time_of_day() -> str:
    """Get current time of day category."""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'


def format_conversation_history(conversations: List[Dict], max_entries: int = 5) -> str:
    """Format conversation history for display."""
    if not conversations:
        return "No conversation history available."
    
    formatted_history = []
    recent_conversations = conversations[:max_entries]
    
    for conv in recent_conversations:
        timestamp = conv.get('timestamp', 'Unknown time')
        user_msg = truncate_text(conv.get('user_message', ''), 50)
        bot_msg = truncate_text(conv.get('bot_response', ''), 50)
        
        formatted_history.append(f"[{timestamp}]")
        formatted_history.append(f"User: {user_msg}")
        formatted_history.append(f"Bot: {bot_msg}")
        formatted_history.append("")
    
    return "\n".join(formatted_history)


def calculate_response_time(start_time: datetime, end_time: datetime = None) -> float:
    """Calculate response time in seconds."""
    if end_time is None:
        end_time = datetime.now()
    
    delta = end_time - start_time
    return delta.total_seconds()


def rate_limit_check(user_id: str, action: str, limit: int = 60, 
                    window_minutes: int = 1, storage: Dict = None) -> bool:
    """Simple rate limiting check."""
    if storage is None:
        # In a real implementation, this would use a proper storage backend
        if not hasattr(rate_limit_check, '_storage'):
            rate_limit_check._storage = {}
        storage = rate_limit_check._storage
    
    key = f"{user_id}_{action}"
    now = datetime.now()
    
    # Clean old entries
    cutoff_time = now - timedelta(minutes=window_minutes)
    if key in storage:
        storage[key] = [timestamp for timestamp in storage[key] if timestamp > cutoff_time]
    else:
        storage[key] = []
    
    # Check limit
    if len(storage[key]) >= limit:
        return False
    
    # Add current request
    storage[key].append(now)
    return True


def create_error_response(error_type: str, message: str, details: Dict = None) -> Dict:
    """Create standardized error response."""
    response = {
        'error': True,
        'error_type': error_type,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response


def create_success_response(data: Any, message: str = "Success") -> Dict:
    """Create standardized success response."""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }


def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """Setup a logger with standard configuration."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, level.upper()))
    return logger


def mask_sensitive_data(data: Dict, sensitive_keys: List[str] = None) -> Dict:
    """Mask sensitive data in dictionary for logging."""
    if sensitive_keys is None:
        sensitive_keys = ['password', 'token', 'key', 'secret', 'api_key']
    
    masked_data = {}
    for key, value in data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            masked_data[key] = '***masked***'
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value, sensitive_keys)
        else:
            masked_data[key] = value
    
    return masked_data


def health_check() -> Dict[str, Any]:
    """Perform basic health check."""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'N/A',  # Would be calculated from actual start time
        'version': '1.0.0'
    }


class PerformanceTimer:
    """Context manager for measuring performance."""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = calculate_response_time(self.start_time, self.end_time)
        
        if exc_type is None:
            self.logger.info(f"{self.operation_name} completed in {duration:.3f} seconds")
        else:
            self.logger.error(f"{self.operation_name} failed after {duration:.3f} seconds")
    
    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return calculate_response_time(self.start_time, self.end_time)
        return None