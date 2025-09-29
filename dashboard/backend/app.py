"""
Flask Dashboard Backend for Dynamic AI Chatbot
Provides analytics and monitoring endpoints for the dashboard UI.
"""
import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configuration
CHATBOT_API_URL = os.getenv('CHATBOT_API_URL', 'http://localhost:8000')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))

class DashboardDataService:
    """Service for fetching and processing dashboard data."""
    
    def __init__(self, chatbot_api_url: str):
        self.chatbot_api_url = chatbot_api_url
    
    def fetch_analytics_stats(self) -> Dict[str, Any]:
        """Fetch analytics stats from the main chatbot API."""
        try:
            response = requests.get(f"{self.chatbot_api_url}/analytics/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch analytics: {response.status_code}")
                return self._get_mock_analytics()
        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            return self._get_mock_analytics()
    
    def _get_mock_analytics(self) -> Dict[str, Any]:
        """Generate mock analytics data for demonstration."""
        return {
            "total_conversations": 1247,
            "total_messages": 8932,
            "average_conversation_length": 7.2,
            "intent_distribution": {
                "greeting": 234,
                "question": 456,
                "request": 287,
                "help": 156,
                "complaint": 89,
                "goodbye": 134,
                "unknown": 91
            },
            "sentiment_distribution": {
                "positive": 567,
                "neutral": 432,
                "negative": 248
            },
            "platform_distribution": {
                "web": 623,
                "slack": 234,
                "telegram": 198,
                "api": 192
            },
            "average_response_time_ms": 342.5,
            "user_satisfaction_rating": 4.2
        }
    
    def get_conversation_trends(self, days: int = 7) -> Dict[str, Any]:
        """Generate conversation trends data."""
        import random
        
        dates = []
        messages = []
        conversations = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            dates.append(date.strftime('%Y-%m-%d'))
            # Mock data with some variation
            base_messages = 100 + (i * 20)
            messages.append(base_messages + random.randint(-30, 50))
            conversations.append((base_messages // 7) + random.randint(-10, 15))
        
        return {
            "labels": dates,
            "messages": messages,
            "conversations": conversations
        }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for live dashboard updates."""
        import random
        
        return {
            "active_sessions": random.randint(15, 45),
            "messages_per_minute": random.randint(5, 25),
            "average_response_time": random.randint(200, 500),
            "server_status": "healthy",
            "uptime_hours": 72.5
        }
    
    def get_top_intents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top detected intents."""
        stats = self.fetch_analytics_stats()
        intent_dist = stats.get("intent_distribution", {})
        
        # Sort by count and take top N
        sorted_intents = sorted(intent_dist.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {
                "intent": intent,
                "count": count,
                "percentage": round((count / sum(intent_dist.values())) * 100, 1) if intent_dist else 0
            }
            for intent, count in sorted_intents
        ]

# Initialize data service
data_service = DashboardDataService(CHATBOT_API_URL)

# --- API Endpoints ---

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-backend"
    })

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """Get Key Performance Indicators."""
    stats = data_service.fetch_analytics_stats()
    
    kpis = {
        "total_users": stats.get("total_conversations", 0),
        "total_messages": stats.get("total_messages", 0),
        "avg_conversation_length": round(stats.get("average_conversation_length", 0), 1),
        "response_time_ms": round(stats.get("average_response_time_ms", 0), 1),
        "satisfaction_rating": stats.get("user_satisfaction_rating", 0),
        "positive_sentiment_percentage": round(
            (stats.get("sentiment_distribution", {}).get("positive", 0) /
             max(sum(stats.get("sentiment_distribution", {}).values()), 1)) * 100, 1
        )
    }
    
    return jsonify(kpis)

@app.route('/api/conversation-trends', methods=['GET'])
def get_conversation_trends():
    """Get conversation trends data for charts."""
    days = request.args.get('days', 7, type=int)
    trends = data_service.get_conversation_trends(days)
    return jsonify(trends)

@app.route('/api/sentiment-distribution', methods=['GET'])
def get_sentiment_distribution():
    """Get sentiment distribution for pie chart."""
    stats = data_service.fetch_analytics_stats()
    sentiment_dist = stats.get("sentiment_distribution", {})
    
    return jsonify({
        "labels": list(sentiment_dist.keys()),
        "data": list(sentiment_dist.values()),
        "colors": ["#10B981", "#F59E0B", "#EF4444"]  # Green, Yellow, Red
    })

@app.route('/api/intent-distribution', methods=['GET'])
def get_intent_distribution():
    """Get intent distribution for bar chart."""
    stats = data_service.fetch_analytics_stats()
    intent_dist = stats.get("intent_distribution", {})
    
    return jsonify({
        "labels": list(intent_dist.keys()),
        "data": list(intent_dist.values()),
        "backgroundColor": "#3B82F6"
    })

@app.route('/api/platform-usage', methods=['GET'])
def get_platform_usage():
    """Get platform usage distribution."""
    stats = data_service.fetch_analytics_stats()
    platform_dist = stats.get("platform_distribution", {})
    
    return jsonify({
        "labels": list(platform_dist.keys()),
        "data": list(platform_dist.values()),
        "colors": ["#8B5CF6", "#06B6D4", "#F97316", "#84CC16"]
    })

@app.route('/api/real-time-metrics', methods=['GET'])
def get_real_time_metrics():
    """Get real-time metrics for live updates."""
    metrics = data_service.get_real_time_metrics()
    return jsonify(metrics)

@app.route('/api/top-intents', methods=['GET'])
def get_top_intents():
    """Get top detected intents."""
    limit = request.args.get('limit', 5, type=int)
    top_intents = data_service.get_top_intents(limit)
    return jsonify(top_intents)

@app.route('/api/chatbot-health', methods=['GET'])
def get_chatbot_health():
    """Check the health of the main chatbot API."""
    try:
        response = requests.get(f"{CHATBOT_API_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "response_time": response.elapsed.total_seconds() * 1000,
                "chatbot_data": response.json()
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "unreachable",
            "error": str(e)
        }), 503

if __name__ == '__main__':
    logger.info(f"Starting Dashboard Backend on port {DASHBOARD_PORT}")
    logger.info(f"Chatbot API URL: {CHATBOT_API_URL}")
    app.run(host='0.0.0.0', port=DASHBOARD_PORT, debug=True)