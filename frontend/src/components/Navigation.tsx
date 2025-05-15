import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, ClockIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { useCodeContext } from '../contexts/CodeContext';

export const Navigation = () => {
  const location = useLocation();
  const { session } = useCodeContext();

  const navItems = [
    { name: 'Scanner', path: '/', icon: HomeIcon },
    { name: 'History', path: '/history', icon: ClockIcon },
    { name: 'Settings', path: '/settings', icon: Cog6ToothIcon },
  ];

  // Calculate packed boxes based on scanned items and box capacity
  const packedBoxes = session ? Math.floor(session.scannedItems / session.boxCapacity) : 0;

  return (
    <nav className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`inline-flex items-center px-4 pt-1 border-b-2 text-sm font-medium ${
                    isActive
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <item.icon className="h-5 w-5 mr-2" />
                  {item.name}
                </Link>
              );
            })}
          </div>
          <div className="flex items-center">
            {session && (
              <div className="flex flex-col items-center">
                <p className="text-sm font-medium text-gray-700">
                  {session.scannedItems} / {packedBoxes}
                </p>
                <p className="text-xs text-gray-500">
                  Сканов/Коробов
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
