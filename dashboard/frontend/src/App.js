import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  Clock, 
  TrendingUp, 
  Activity,
  Star
} from 'lucide-react';
import MetricCard from './components/MetricCard';
import ChartCard from './components/ChartCard';
import SystemHealth from './components/SystemHealth';
import apiClient from './api';

const App = () => {
  const [kpis, setKpis] = useState({});
  const [conversationTrends, setConversationTrends] = useState({});
  const [sentimentData, setSentimentData] = useState({});
  const [intentData, setIntentData] = useState({});
  const [platformData, setPlatformData] = useState({});
  const [realTimeMetrics, setRealTimeMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get the chatbot UI URL
  const getChatbotUrl = () => {
    const baseUrl = window.location.hostname === 'localhost' 
      ? 'http://localhost:8000'
      : `${window.location.protocol}//${window.location.hostname.replace('-3000', '-8000')}`;
    return `${baseUrl}/static/chatbot_secure.html`;
  };

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        kpiData,
        trendsData,
        sentimentDistribution,
        intentDistribution,
        platformUsage,
        realTimeData
      ] = await Promise.all([
        apiClient.get('/api/kpis'),
        apiClient.get('/api/conversation-trends'),
        apiClient.get('/api/sentiment-distribution'),
        apiClient.get('/api/intent-distribution'),
        apiClient.get('/api/platform-usage'),
        apiClient.get('/api/real-time-metrics')
      ]);

      setKpis(kpiData);
      setConversationTrends(trendsData);
      setSentimentData(sentimentDistribution);
      setIntentData(intentDistribution);
      setPlatformData(platformUsage);
      setRealTimeMetrics(realTimeData);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Chart data configurations
  const conversationTrendsChartData = {
    labels: conversationTrends.labels || [],
    datasets: [
      {
        label: 'Messages',
        data: conversationTrends.messages || [],
        borderColor: '#3B82F6',
        backgroundColor: '#3B82F6',
        tension: 0.4,
      },
      {
        label: 'Conversations',
        data: conversationTrends.conversations || [],
        borderColor: '#10B981',
        backgroundColor: '#10B981',
        tension: 0.4,
      },
    ],
  };

  const sentimentChartData = {
    labels: sentimentData.labels || [],
    datasets: [
      {
        data: sentimentData.data || [],
        backgroundColor: sentimentData.colors || ['#10B981', '#F59E0B', '#EF4444'],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const intentChartData = {
    labels: intentData.labels || [],
    datasets: [
      {
        label: 'Intent Count',
        data: intentData.data || [],
        backgroundColor: '#3B82F6',
        borderRadius: 4,
      },
    ],
  };

  const platformChartData = {
    labels: platformData.labels || [],
    datasets: [
      {
        data: platformData.data || [],
        backgroundColor: platformData.colors || ['#8B5CF6', '#06B6D4', '#F97316', '#84CC16'],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium">{error}</div>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🤖 AI Chatbot Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Real-time analytics and monitoring
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href={getChatbotUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
              >
                <MessageSquare size={16} />
                <span>Secure Chatbot UI</span>
              </a>
              <button
                onClick={fetchDashboardData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
          <MetricCard
            title="Total Users"
            value={kpis.total_users?.toLocaleString() || '0'}
            icon={Users}
            color="blue"
          />
          <MetricCard
            title="Total Messages"
            value={kpis.total_messages?.toLocaleString() || '0'}
            icon={MessageSquare}
            color="green"
          />
          <MetricCard
            title="Avg Conversation"
            value={`${kpis.avg_conversation_length || 0} msgs`}
            icon={TrendingUp}
            color="yellow"
          />
          <MetricCard
            title="Response Time"
            value={`${kpis.response_time_ms || 0}ms`}
            icon={Clock}
            color="purple"
          />
          <MetricCard
            title="Satisfaction"
            value={`${kpis.satisfaction_rating || 0}/5`}
            icon={Star}
            color="yellow"
          />
          <MetricCard
            title="Positive Sentiment"
            value={`${kpis.positive_sentiment_percentage || 0}%`}
            icon={Activity}
            color="green"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Conversation Trends */}
          <ChartCard
            title="Conversation Trends (7 Days)"
            type="line"
            data={conversationTrendsChartData}
            height={300}
          />

          {/* Sentiment Distribution */}
          <ChartCard
            title="Sentiment Distribution"
            type="doughnut"
            data={sentimentChartData}
            height={300}
          />

          {/* Intent Distribution */}
          <ChartCard
            title="Intent Distribution"
            type="bar"
            data={intentChartData}
            height={300}
          />

          {/* Platform Usage */}
          <ChartCard
            title="Platform Usage"
            type="pie"
            data={platformChartData}
            height={300}
          />
        </div>

        {/* System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <SystemHealth 
            data={{
              server_status: 'healthy',
              chatbot_status: realTimeMetrics.server_status || 'healthy',
              active_sessions: realTimeMetrics.active_sessions,
              uptime_hours: realTimeMetrics.uptime_hours
            }} 
          />
          
          {/* Real-time Metrics */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Real-time Metrics</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600">Messages/Min</div>
                  <div className="text-2xl font-bold text-blue-900">
                    {realTimeMetrics.messages_per_minute || 0}
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm text-green-600">Avg Response Time</div>
                  <div className="text-2xl font-bold text-green-900">
                    {realTimeMetrics.average_response_time || 0}ms
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-500">
            <p>Dynamic AI Chatbot Dashboard © 2025</p>
            <p className="text-sm mt-1">
              Last updated: {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;