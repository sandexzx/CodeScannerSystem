import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

interface ThemeSwitcherProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ isDarkMode, toggleTheme }) => {
  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all duration-300 ease-in-out overflow-hidden"
      aria-label={isDarkMode ? "Переключить на светлую тему" : "Переключить на темную тему"}
      style={{ width: '40px', height: '40px' }} // Фиксированный размер для корректного позиционирования иконки
    >
      {/* Иконка Луны (для светлой темы) */}
      <div
        className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ease-in-out
                    ${isDarkMode ? 'opacity-0 transform -rotate-90 scale-50' : 'opacity-100 transform rotate-0 scale-100'}`}
      >
        <MoonIcon className="h-6 w-6 text-gray-700" />
      </div>
      {/* Иконка Солнца (для темной темы) */}
      <div
        className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ease-in-out
                    ${isDarkMode ? 'opacity-100 transform rotate-0 scale-100' : 'opacity-0 transform rotate-90 scale-50'}`}
      >
        <SunIcon className="h-6 w-6 text-yellow-400" />
      </div>
    </button>
  );
};