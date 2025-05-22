import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, ClockIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { useCodeContext } from '../contexts/CodeContext';
import { useState, useEffect } from 'react';

export const Navigation = () => {
  const location = useLocation();
  const { session, currentCode } = useCodeContext();
  const [lastScanTime, setLastScanTime] = useState<string | null>(null);

  // Update timestamp when currentCode changes
  useEffect(() => {
    if (currentCode) {
      setLastScanTime(new Date().toLocaleTimeString());
    }
  }, [currentCode]);

  const navItems = [
    { name: 'Сканер', path: '/', icon: HomeIcon },
    { name: 'История', path: '/history', icon: ClockIcon },
    { name: 'Настройки', path: '/settings', icon: Cog6ToothIcon },
  ];

  // Calculate packed boxes based on scanned items and box capacity
  const packedBoxes = session ? Math.floor(session.scannedItems / session.boxCapacity) : 0;

  return (
    <nav className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 overflow-x-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`group inline-flex items-center px-4 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ease-in-out hover:translate-y-[-2px] ${
                    isActive
                      ? 'border-primary-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-primary-400 dark:hover:border-primary-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <item.icon className={`h-5 w-5 mr-2 transition-transform duration-300 group-hover:scale-110 ${
                    isActive ? 'text-primary-500' : 'group-hover:text-primary-500'
                  }`} />
                  <span className="relative">
                    {item.name}
                    <span className={`absolute -bottom-1 left-0 w-0 h-0.5 bg-primary-500 transition-all duration-300 group-hover:w-full ${
                      isActive ? 'w-full' : ''
                    }`} />
                  </span>
                </Link>
              );
            })}
          </div>
          <div className="flex items-center space-x-6">
            {session && (
              <>
                {currentCode && (
                  <div className="flex flex-col items-center">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Последний код:
                    </p>
                    <p className="text-xs font-mono text-gray-500 dark:text-gray-400">
                      {currentCode}
                    </p>
                  </div>
                )}
                {lastScanTime && (
                  <div className="flex flex-col items-center">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Отсканировано в:
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {lastScanTime}
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
