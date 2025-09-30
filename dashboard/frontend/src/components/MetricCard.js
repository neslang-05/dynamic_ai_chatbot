import React from 'react';

const MetricCard = ({ title, value, change, changeType, icon: Icon, color = "blue", trend }) => {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    green: "from-green-500 to-green-600", 
    yellow: "from-yellow-500 to-yellow-600",
    red: "from-red-500 to-red-600",
    purple: "from-purple-500 to-purple-600",
    orange: "from-orange-500 to-orange-600"
  };

  const backgroundClasses = {
    blue: "from-blue-50 to-blue-100",
    green: "from-green-50 to-green-100", 
    yellow: "from-yellow-50 to-yellow-100",
    red: "from-red-50 to-red-100",
    purple: "from-purple-50 to-purple-100",
    orange: "from-orange-50 to-orange-100"
  };

  const changeColor = changeType === 'positive' || (trend && trend.startsWith('+')) ? 'text-green-600' : 
                     changeType === 'negative' || (trend && trend.startsWith('-')) ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
      <div className={`bg-gradient-to-r ${backgroundClasses[color]} p-6 relative overflow-hidden`}>
        <div className="flex items-center justify-between relative z-10">
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
              {title}
            </p>
            <p className="text-3xl font-bold text-gray-900">
              {value}
            </p>
            {(change || trend) && (
              <div className={`flex items-center mt-3 text-sm font-semibold ${changeColor}`}>
                <span className="mr-1">
                  {changeType === 'positive' || (trend && trend.startsWith('+')) ? '↗️' : 
                   changeType === 'negative' || (trend && trend.startsWith('-')) ? '↘️' : '→'}
                </span>
                {change || trend}
              </div>
            )}
          </div>
          <div className={`p-4 rounded-2xl bg-gradient-to-r ${colorClasses[color]} text-white shadow-lg`}>
            {Icon && <Icon size={28} />}
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute -top-4 -right-4 w-24 h-24 bg-white opacity-10 rounded-full"></div>
        <div className="absolute -bottom-6 -left-6 w-16 h-16 bg-white opacity-5 rounded-full"></div>
      </div>
      
      {/* Bottom accent line */}
      <div className={`h-1 bg-gradient-to-r ${colorClasses[color]}`}></div>
    </div>
  );
};

export default MetricCard;