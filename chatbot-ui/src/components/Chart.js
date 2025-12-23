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
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import './Chart.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ChartComponent = ({ chartData }) => {
  if (!chartData || !chartData.type) {
    return null;
  }

  const { type, data, options } = chartData;

  // Parse callback functions from strings
  const parseOptions = (opts) => {
    if (!opts) return {};
    
    const parsed = JSON.parse(JSON.stringify(opts));
    
    // Parse y-axis tick callback if it's a string
    if (parsed.scales?.y?.ticks?.callback && typeof parsed.scales.y.ticks.callback === 'string') {
      try {
        const callbackStr = parsed.scales.y.ticks.callback;
        // Extract function body from "function(...) { ... }" string
        const match = callbackStr.match(/function\s*\([^)]*\)\s*\{([\s\S]*)\}/);
        if (match) {
          // eslint-disable-next-line no-new-func
          parsed.scales.y.ticks.callback = new Function('value', 'index', 'values', match[1]);
        }
      } catch (e) {
        console.error('Failed to parse y-axis callback:', e);
        delete parsed.scales.y.ticks.callback;
      }
    }
    
    // Parse tooltip callbacks if they're strings
    if (parsed.plugins?.tooltip?.callbacks) {
      const callbacks = parsed.plugins.tooltip.callbacks;
      
      // Parse label callback
      if (callbacks.label && typeof callbacks.label === 'string') {
        try {
          const callbackStr = callbacks.label;
          const match = callbackStr.match(/function\s*\([^)]*\)\s*\{([\s\S]*)\}/);
          if (match) {
            // eslint-disable-next-line no-new-func
            callbacks.label = new Function('context', match[1]);
          }
        } catch (e) {
          console.error('Failed to parse tooltip label callback:', e);
          delete callbacks.label;
        }
      }
      
      // Parse title callback
      if (callbacks.title && typeof callbacks.title === 'string') {
        try {
          const callbackStr = callbacks.title;
          const match = callbackStr.match(/function\s*\([^)]*\)\s*\{([\s\S]*)\}/);
          if (match) {
            // eslint-disable-next-line no-new-func
            callbacks.title = new Function('context', match[1]);
          }
        } catch (e) {
          console.error('Failed to parse tooltip title callback:', e);
          delete callbacks.title;
        }
      }
    }
    
    return parsed;
  };

  const parsedOptions = parseOptions(options);

  const renderChart = () => {
    switch (type) {
      case 'line':
        return <Line data={data} options={parsedOptions} />;
      case 'bar':
        return <Bar data={data} options={parsedOptions} />;
      case 'doughnut':
        return <Doughnut data={data} options={parsedOptions} />;
      default:
        return <div>Unsupported chart type: {type}</div>;
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        {renderChart()}
      </div>
    </div>
  );
};

export default ChartComponent;
