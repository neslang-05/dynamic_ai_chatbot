import React from 'react';

const StatusIndicator = ({ status, label }) => {
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'online':
      case 'active':
        return 'bg-green-500';
      case 'warning':
      case 'degraded':
        return 'bg-yellow-500';
      case 'unhealthy':
      case 'offline':
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`}></div>
      <span className="text-sm font-medium text-gray-700">
        {label}: <span className="capitalize">{status}</span>
      </span>
    </div>
  );
};

const SystemHealth = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <StatusIndicator 
            status={data.server_status || 'unknown'} 
            label="Dashboard Server" 
          />
          <StatusIndicator 
            status={data.chatbot_status || 'unknown'} 
            label="Chatbot API" 
          />
          
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Active Sessions</div>
              <div className="text-2xl font-bold text-gray-900">
                {data.active_sessions || 0}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Uptime</div>
              <div className="text-2xl font-bold text-gray-900">
                {data.uptime_hours ? `${data.uptime_hours}h` : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;