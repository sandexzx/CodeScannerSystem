import { Fragment } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

import { useEffect, useState } from 'react';

interface HistoryItem {
  'Box Number': number;
  'Code': string;
  'Timestamp': string;
}

export const History = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('http://localhost:5001/api/history')
      .then(res => {
        if (!res.ok) throw new Error('Ошибка загрузки истории');
        return res.json();
      })
      .then(setHistory)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Sort history by timestamp in reverse chronological order
  const sortedHistory = [...history].sort((a, b) => {
    const dateA = new Date(a.Timestamp);
    const dateB = new Date(b.Timestamp);
    return dateB.getTime() - dateA.getTime();
  });

  // Group history by date
  const groupedHistory = sortedHistory.reduce((acc, item) => {
    const timestamp = item.Timestamp;
    const date = timestamp ? new Date(timestamp) : null;
    const dateStr = date && !isNaN(date.getTime()) 
      ? format(date, 'yyyy-MM-dd', { locale: ru })
      : 'Без даты';
    if (!acc[dateStr]) {
      acc[dateStr] = [];
    }
    acc[dateStr].push(item);
    return acc;
  }, {} as Record<string, typeof history>);

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white">История сканирования</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Просмотр ранее отсканированных кодов DataMatrix
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
        {loading ? (
          <div className="text-center text-blue-500">Загрузка истории...</div>
        ) : error ? (
          <div className="text-center text-red-500">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Нет истории сканирования</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Отсканируйте коды DataMatrix, чтобы увидеть их здесь.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(groupedHistory).map(([date, items]) => (
              <div key={date} className="space-y-4">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {date === 'Без даты' ? date : format(new Date(date), 'EEEE, d MMMM yyyy', { locale: ru })}
                </h3>
                <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                    {items.map((item, idx) => (
                      <li key={`${item.Code}-${item.Timestamp}-${idx}`}>
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-mono text-gray-900 dark:text-white truncate">
                              {item.Code}
                            </p>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-100">
                                {item['Box Number']}
                              </p>
                              <p className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-100">
                                Valid
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                                {(() => {
                                  const date = item.Timestamp ? new Date(item.Timestamp) : null;
                                  return date && !isNaN(date.getTime())
                                    ? format(date, 'HH:mm:ss', { locale: ru })
                                    : '—';
                                })()}
                              </p>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
