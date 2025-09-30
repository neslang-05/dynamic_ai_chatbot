import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Activity,
  Star,
  Monitor,
  Shield,
  Zap
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
      <div className="dashboard-container flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
          <p className="mt-6 text-white text-lg font-medium">Loading Professional Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container flex items-center justify-center">
        <div className="text-center bg-white rounded-professional p-8 shadow-professional">
          <div className="text-red-600 text-lg font-semibold mb-4">{error}</div>
          <button 
            onClick={fetchDashboardData}
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="dashboard-title">
              🤖 AI Chatbot Analytics
            </h1>
            <p className="dashboard-subtitle">
              Enterprise-Grade Real-time Monitoring & Intelligence
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <a
              href={getChatbotUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex items-center space-x-2"
            >
              <Shield size={18} />
              <span>Secure Interface</span>
            </a>
            <button
              onClick={fetchDashboardData}
              className="bg-white/20 hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-professional transition-all duration-200 flex items-center space-x-2"
            >
              <Activity size={18} />
              <span>Refresh Data</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {/* KPI Metrics */}
        <div className="metrics-grid">
          <MetricCard
            title="Total Conversations"
            value={kpis.total_messages?.toLocaleString() || '0'}
            icon={MessageSquare}
            color="navy"
            trend="+12%"
          />
          <MetricCard
            title="Active Users"
            value={kpis.total_users?.toLocaleString() || '0'}
            icon={Users}
            color="green"
            trend="+8%"
          />
          <MetricCard
            title="Average Response"
            value={`${kpis.response_time_ms || 0}ms`}
            icon={Zap}
            color="purple"
            trend="-15ms"
          />
          <MetricCard
            title="Satisfaction Score"
            value={`${kpis.satisfaction_rating || 0}/5`}
            icon={Star}
            color="yellow"
            trend="+0.3"
          />
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Activity className="mr-2 text-green-600" size={20} />
                System Performance
              </h3>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Positive Sentiment</span>
                  <span className="font-semibold text-green-600">{kpis.positive_sentiment_percentage || 0}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Response Accuracy</span>
                  <span className="font-semibold text-blue-600">94.2%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Uptime</span>
                  <span className="font-semibold text-green-600">99.9%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Monitor className="mr-2 text-blue-600" size={20} />
                Real-time Status
              </h3>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Server Status</span>
                  <span className="status-indicator status-online">Online</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Active Sessions</span>
                  <span className="font-semibold text-blue-600">{realTimeMetrics.active_sessions || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Queue Length</span>
                  <span className="font-semibold text-gray-600">0</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <TrendingUp className="mr-2 text-green-600" size={20} />
                Today's Metrics
              </h3>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Messages Today</span>
                  <span className="font-semibold text-blue-600">{realTimeMetrics.messages_today || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">New Users</span>
                  <span className="font-semibold text-green-600">{realTimeMetrics.new_users_today || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Peak Hour</span>
                  <span className="font-semibold text-gray-600">14:00-15:00</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="charts-grid">
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