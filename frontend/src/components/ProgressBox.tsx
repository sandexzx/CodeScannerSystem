import React from 'react';

interface ProgressBoxProps {
  current: number;
  total: number;
  className?: string;
}

export const ProgressBox: React.FC<ProgressBoxProps> = ({ current, total, className = '' }) => {
  const progress = Math.min(100, (current / total) * 100);
  const isComplete = current === total;

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 w-full ${className}`}>
      <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-3">
        <span>Отсканировано: {current}</span>
        <span>Вместимость: {total}</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
        <div 
          className={`h-2.5 rounded-full transition-all duration-300 ${
            isComplete ? 'bg-green-500' : 'bg-primary-500'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}; 