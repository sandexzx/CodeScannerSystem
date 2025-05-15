import { useState, useEffect } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { Cog6ToothIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export const Settings = () => {
  const { boxCapacity, onUpdateBoxCapacity } = useCodeContext();
  const [capacity, setCapacity] = useState(boxCapacity.toString());
  const [showSaved, setShowSaved] = useState(false);

  // Update local state when boxCapacity changes
  useEffect(() => {
    setCapacity(boxCapacity.toString());
  }, [boxCapacity]);

  // Handle save
  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    const newCapacity = parseInt(capacity, 10);
    if (!isNaN(newCapacity) && newCapacity > 0) {
      onUpdateBoxCapacity(newCapacity);
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 2000);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Settings</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Configure application settings
        </p>
      </div>

      <div className="flex-1 p-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                Box Capacity
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>
                  Set the maximum number of items that can fit in a box.
                </p>
              </div>
              <form onSubmit={handleSave} className="mt-5 sm:flex sm:items-center">
                <div className="w-full sm:max-w-xs">
                  <label htmlFor="capacity" className="sr-only">
                    Box Capacity
                  </label>
                  <input
                    type="number"
                    name="capacity"
                    id="capacity"
                    min="1"
                    value={capacity}
                    onChange={(e) => setCapacity(e.target.value)}
                    className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md placeholder-gray-400 dark:placeholder-gray-500"
                    placeholder="e.g. 10"
                  />
                </div>
                <button
                  type="submit"
                  className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-800 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  {showSaved ? (
                    <>
                      <CheckCircleIcon className="-ml-1 mr-2 h-5 w-5 text-green-400" />
                      Saved
                    </>
                  ) : (
                    'Save'
                  )}
                </button>
              </form>
            </div>
          </div>

          <div className="mt-8 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                About
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>
                  DataMatrix Scanner v1.0.0
                </p>
                <p className="mt-2">
                  A modern interface for scanning and managing DataMatrix codes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
