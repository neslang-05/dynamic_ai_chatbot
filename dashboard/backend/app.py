"""
Flask backend for Dynamic AI Chatbot Dashboard
Provides API endpoints for the React frontend dashboard
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the main src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from analytics import analytics
    from config import settings
    from models import Platform, Intent, Sentiment
except ImportError as e:
    print(f"Warning: Could not import main chatbot modules: {e}")
    analytics = None
    settings = None


# Configure logging
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'dashboard-backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DashboardAPI:
    """Dashboard API service for managing analytics and metrics."""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Configuration
        self.chatbot_api_url = os.getenv("CHATBOT_API_URL", "http://localhost:8000")
        self.dashboard_port = int(os.getenv("DASHBOARD_PORT", "5000"))
        
        # Setup routes
        self.setup_routes()
        
        logger.info("Dashboard API initialized")
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Dashboard health check endpoint."""
            return jsonify({
                "status": "healthy",
                "message": "Dashboard Backend is running",
                "timestamp": datetime.utcnow().isoformat(),
                "chatbot_api_url": self.chatbot_api_url
            })
        
        @self.app.route('/api/chatbot-health', methods=['GET'])
        def chatbot_health():
            """Check main chatbot API health."""
            try:
                response = requests.get(f"{self.chatbot_api_url}/health", timeout=5)
                if response.status_code == 200:
                    return jsonify({
                        "status": "healthy",
                        "chatbot_available": True,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    })
                else:
                    return jsonify({
                        "status": "unhealthy",
                        "chatbot_available": False,
                        "error": f"HTTP {response.status_code}"
                    }), 503
            except requests.RequestException as e:
                return jsonify({
                    "status": "unhealthy",
                    "chatbot_available": False,
                    "error": str(e)
                }), 503
        
        @self.app.route('/api/kpis', methods=['GET'])
        def get_kpis():
            """Get Key Performance Indicators."""
            try:
                # Try to get real data from analytics
                stats = self.get_analytics_stats()
                
                # Calculate KPIs from analytics data
                kpis = {
                    "total_users": self.calculate_total_users(stats),
                    "total_messages": stats.get("total_messages", 0),
                    "avg_conversation_length": stats.get("average_conversation_length", 0),
                    "response_time_ms": stats.get("average_response_time_ms", 350),
                    "satisfaction_rating": stats.get("user_satisfaction_rating", 4.1),
                    "positive_sentiment_percentage": self.calculate_positive_sentiment_percentage(stats)
                }
                
                return jsonify(kpis)
                
            except Exception as e:
                logger.error(f"Error getting KPIs: {e}")
                # Return mock data if real data fails
                return jsonify(self.get_mock_kpis())
        
        @self.app.route('/api/conversation-trends', methods=['GET'])
        def get_conversation_trends():
            """Get conversation trends over the last 7 days."""
            try:
                # Generate 7 days of data
                labels = []
                messages_data = []
                conversations_data = []
                
                for i in range(7):
                    date = datetime.now() - timedelta(days=6-i)
                    labels.append(date.strftime("%m/%d"))
                    
                    # Get daily stats (mock for now, could be enhanced with real historical data)
                    messages_data.append(self.get_daily_message_count(date))
                    conversations_data.append(self.get_daily_conversation_count(date))
                
                return jsonify({
                    "labels": labels,
                    "messages": messages_data,
                    "conversations": conversations_data
                })
                
            except Exception as e:
                logger.error(f"Error getting conversation trends: {e}")
                return jsonify(self.get_mock_conversation_trends())
        
        @self.app.route('/api/sentiment-distribution', methods=['GET'])
        def get_sentiment_distribution():
            """Get sentiment distribution data."""
            try:
                stats = self.get_analytics_stats()
                sentiment_dist = stats.get("sentiment_distribution", {})
                
                # Ensure all sentiment types are represented
                total_messages = sum(sentiment_dist.values()) or 1
                
                return jsonify({
                    "labels": ["Positive", "Negative", "Neutral"],
                    "data": [
                        sentiment_dist.get("positive", 0),
                        sentiment_dist.get("negative", 0),
                        sentiment_dist.get("neutral", 0)
                    ],
                    "percentages": [
                        round(sentiment_dist.get("positive", 0) / total_messages * 100, 1),
                        round(sentiment_dist.get("negative", 0) / total_messages * 100, 1),
                        round(sentiment_dist.get("neutral", 0) / total_messages * 100, 1)
                    ]
                })
                
            except Exception as e:
                logger.error(f"Error getting sentiment distribution: {e}")
                return jsonify(self.get_mock_sentiment_distribution())
        
        @self.app.route('/api/intent-distribution', methods=['GET'])
        def get_intent_distribution():
            """Get intent distribution data."""
            try:
                stats = self.get_analytics_stats()
                intent_dist = stats.get("intent_distribution", {})
                
                # Convert to lists for chart display
                labels = list(intent_dist.keys())
                data = list(intent_dist.values())
                
                # Sort by frequency
                sorted_items = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
                labels, data = zip(*sorted_items) if sorted_items else ([], [])
                
                return jsonify({
                    "labels": list(labels),
                    "data": list(data)
                })
                
            except Exception as e:
                logger.error(f"Error getting intent distribution: {e}")
                return jsonify(self.get_mock_intent_distribution())
        
        @self.app.route('/api/platform-usage', methods=['GET'])
        def get_platform_usage():
            """Get platform usage statistics."""
            try:
                stats = self.get_analytics_stats()
                platform_dist = stats.get("platform_distribution", {})
                
                # Convert to chart format
                labels = list(platform_dist.keys())
                data = list(platform_dist.values())
                
                return jsonify({
                    "labels": labels,
                    "data": data
                })
                
            except Exception as e:
                logger.error(f"Error getting platform usage: {e}")
                return jsonify(self.get_mock_platform_usage())
        
        @self.app.route('/api/real-time-metrics', methods=['GET'])
        def get_real_time_metrics():
            """Get real-time system metrics."""
            try:
                # Check chatbot health
                chatbot_healthy = self.is_chatbot_healthy()
                
                return jsonify({
                    "server_status": "healthy",
                    "chatbot_status": "healthy" if chatbot_healthy else "unhealthy",
                    "active_sessions": self.get_active_sessions_count(),
                    "uptime_hours": self.get_uptime_hours(),
                    "messages_per_minute": self.get_messages_per_minute(),
                    "average_response_time": self.get_current_response_time()
                })
                
            except Exception as e:
                logger.error(f"Error getting real-time metrics: {e}")
                return jsonify(self.get_mock_real_time_metrics())
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics stats from the main chatbot API or in-memory analytics."""
        try:
            # Try to get from main chatbot API first
            response = requests.get(f"{self.chatbot_api_url}/analytics/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            logger.warning("Could not connect to main chatbot API for analytics")
        
        # Fallback to in-memory analytics if available
        if analytics:
            return analytics.get_stats()
        
        # Return empty stats if nothing available
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "average_conversation_length": 0.0,
            "intent_distribution": {},
            "sentiment_distribution": {},
            "platform_distribution": {},
            "average_response_time_ms": 0.0,
            "user_satisfaction_rating": 0.0
        }
    
    def calculate_total_users(self, stats: Dict[str, Any]) -> int:
        """Calculate total unique users from stats."""
        # This is an estimate based on conversations
        total_conversations = stats.get("total_conversations", 0)
        # Assume average user has 1.5 conversations
        return max(1, int(total_conversations / 1.5))
    
    def calculate_positive_sentiment_percentage(self, stats: Dict[str, Any]) -> float:
        """Calculate positive sentiment percentage."""
        sentiment_dist = stats.get("sentiment_distribution", {})
        total = sum(sentiment_dist.values())
        if total == 0:
            return 0.0
        return round(sentiment_dist.get("positive", 0) / total * 100, 1)
    
    def is_chatbot_healthy(self) -> bool:
        """Check if the main chatbot API is healthy."""
        try:
            response = requests.get(f"{self.chatbot_api_url}/health", timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions (mock implementation)."""
        # In a real implementation, this would query the session store
        return 15
    
    def get_uptime_hours(self) -> float:
        """Get system uptime in hours (mock implementation)."""
        # In a real implementation, this would track actual uptime
        return 24.5
    
    def get_messages_per_minute(self) -> int:
        """Get current messages per minute rate."""
        # In a real implementation, this would calculate from recent message timestamps
        return 8
    
    def get_current_response_time(self) -> int:
        """Get current average response time in milliseconds."""
        # In a real implementation, this would track recent response times
        return 285
    
    def get_daily_message_count(self, date: datetime) -> int:
        """Get message count for a specific day (mock implementation)."""
        # In a real implementation, this would query historical data
        import random
        return random.randint(50, 200)
    
    def get_daily_conversation_count(self, date: datetime) -> int:
        """Get conversation count for a specific day (mock implementation)."""
        # In a real implementation, this would query historical data
        import random
        return random.randint(20, 80)
    
    # Mock data methods for fallback scenarios
    def get_mock_kpis(self) -> Dict[str, Any]:
        """Get mock KPI data for testing."""
        return {
            "total_users": 1247,
            "total_messages": 8932,
            "avg_conversation_length": 4.2,
            "response_time_ms": 285,
            "satisfaction_rating": 4.1,
            "positive_sentiment_percentage": 68.5
        }
    
    def get_mock_conversation_trends(self) -> Dict[str, List]:
        """Get mock conversation trends data."""
        return {
            "labels": ["09/24", "09/25", "09/26", "09/27", "09/28", "09/29", "09/30"],
            "messages": [120, 135, 98, 167, 143, 189, 156],
            "conversations": [45, 52, 38, 63, 54, 71, 59]
        }
    
    def get_mock_sentiment_distribution(self) -> Dict[str, Any]:
        """Get mock sentiment distribution data."""
        return {
            "labels": ["Positive", "Negative", "Neutral"],
            "data": [425, 89, 234],
            "percentages": [56.8, 11.9, 31.3]
        }
    
    def get_mock_intent_distribution(self) -> Dict[str, List]:
        """Get mock intent distribution data."""
        return {
            "labels": ["question", "greeting", "help", "request", "goodbye", "complaint"],
            "data": [342, 189, 156, 98, 87, 45]
        }
    
    def get_mock_platform_usage(self) -> Dict[str, List]:
        """Get mock platform usage data."""
        return {
            "labels": ["Web", "API", "Slack", "Telegram"],
            "data": [456, 234, 123, 89]
        }
    
    def get_mock_real_time_metrics(self) -> Dict[str, Any]:
        """Get mock real-time metrics data."""
        return {
            "server_status": "healthy",
            "chatbot_status": "healthy",
            "active_sessions": 15,
            "uptime_hours": 24.5,
            "messages_per_minute": 8,
            "average_response_time": 285
        }
    
    def run(self, debug=False):
        """Run the Flask application."""
        # Ensure logs directory exists
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        logger.info(f"Starting Dashboard Backend on port {self.dashboard_port}")
        logger.info(f"Chatbot API URL: {self.chatbot_api_url}")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.dashboard_port,
                debug=debug,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Failed to start Dashboard Backend: {e}")
            raise


def main():
    """Main entry point for the dashboard backend."""
    # Check if we're in development mode
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Create and run the dashboard API
    dashboard = DashboardAPI()
    dashboard.run(debug=debug_mode)


if __name__ == "__main__":
    main()
