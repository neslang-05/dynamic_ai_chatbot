import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ChartCard = ({ title, type, data, options = {}, height = 300 }) => {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: type === 'pie' || type === 'doughnut' ? undefined : {
      y: {
        beginAtZero: true,
        grid: {
          color: '#f3f4f6',
        },
      },
      x: {
        grid: {
          color: '#f3f4f6',
        },
      },
    },
    ...options,
  };

  const renderChart = () => {
    switch (type) {
      case 'line':
        return <Line data={data} options={defaultOptions} height={height} />;
      case 'bar':
        return <Bar data={data} options={defaultOptions} height={height} />;
      case 'pie':
        return <Pie data={data} options={defaultOptions} height={height} />;
      case 'doughnut':
        return <Doughnut data={data} options={defaultOptions} height={height} />;
      default:
        return <div>Chart type not supported</div>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="p-6">
        <div style={{ height: `${height}px` }}>
          {renderChart()}
        </div>
      </div>
    </div>
  );
};

export default ChartCard;