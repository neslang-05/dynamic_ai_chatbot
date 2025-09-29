import React from 'react';

const MetricCard = ({ title, value, change, changeType, icon: Icon, color = "blue" }) => {
  const colorClasses = {
    blue: "from-blue-400 to-blue-600",
    green: "from-green-400 to-green-600", 
    yellow: "from-yellow-400 to-yellow-600",
    red: "from-red-400 to-red-600",
    purple: "from-purple-400 to-purple-600"
  };

  const changeColor = changeType === 'positive' ? 'text-green-600' : 
                     changeType === 'negative' ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow duration-300">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
              {title}
            </p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {value}
            </p>
            {change && (
              <p className={`text-sm mt-1 ${changeColor}`}>
                {changeType === 'positive' ? '↗' : changeType === 'negative' ? '↘' : '→'} {change}
              </p>
            )}
          </div>
          <div className={`p-3 rounded-full bg-gradient-to-r ${colorClasses[color]} text-white`}>
            {Icon && <Icon size={24} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricCard;