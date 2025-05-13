import { Fragment } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

import { useEffect, useState } from 'react';

export const History = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('http://localhost:8000/history')
      .then(res => {
        if (!res.ok) throw new Error('Ошибка загрузки истории');
        return res.json();
      })
      .then(setHistory)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Group history by date
  const groupedHistory = history.reduce((acc, item) => {
    const date = new Date(item.Timestamp || item.timestamp).toLocaleDateString('ru-RU');
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(item);
    return acc;
  }, {} as Record<string, typeof history>);

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Scan History</h2>
        <p className="mt-1 text-sm text-gray-500">
          View previously scanned DataMatrix codes
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="text-center text-blue-500">Загрузка истории...</div>
        ) : error ? (
          <div className="text-center text-red-500">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No scan history</h3>
            <p className="mt-1 text-sm text-gray-500">
              Scan some DataMatrix codes to see them here.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(groupedHistory).map(([date, items]) => (
              <div key={date} className="space-y-4">
                <h3 className="text-sm font-medium text-gray-500">
                  {new Date(date).toLocaleDateString('ru-RU', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </h3>
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {items.map((item, idx) => (
                      <li key={`${item.Code || item.code}-${item.Timestamp || item.timestamp}-${idx}`}>
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-mono text-gray-900 truncate">
                              {item.Code || item.code}
                            </p>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                {item.sessionId ? item.sessionId.slice(-6) : ''}
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                {(() => {
                                  const ts = item.Timestamp || item.timestamp;
                                  const date = ts ? new Date(ts) : null;
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
