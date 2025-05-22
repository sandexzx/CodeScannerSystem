import { useState, useEffect, useRef } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { PlayIcon, StopIcon, ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';
import { ProgressBox } from '../components/ProgressBox';

// Функция для проверки раскладки клавиатуры
const isEnglishLayout = (text: string): boolean => {
  // Проверяем, содержит ли текст русские буквы
  const russianPattern = /[а-яА-ЯёЁ]/;
  return !russianPattern.test(text);
};

export const Home = () => {
  const {
    currentCode,
    session,
    onNewScan,
    onStartSession,
    onContinueSession,
    onCompleteSession,
    boxCapacity,
    isAdminMode,
    isProcessing,
    setIsAdminMode
  } = useCodeContext();
  
  const [scanInput, setScanInput] = useState('');
  const [layoutError, setLayoutError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when the component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Focus the input when session becomes active
  useEffect(() => {
    if (session?.status === 'active' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [session?.status]);

  // Focus the input after processing a code
  useEffect(() => {
    if (!isProcessing && session?.status === 'active' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isProcessing, session?.status]);

  // Handle barcode scanning
  const handleScan = (e: React.FormEvent) => {
    e.preventDefault();
    if (scanInput.trim() && !isProcessing) {
      // Проверяем раскладку клавиатуры
      if (!isEnglishLayout(scanInput)) {
        setLayoutError('Пожалуйста, переключите раскладку клавиатуры на английскую');
        setScanInput('');
        return;
      }
      setLayoutError(null);

      // Check for admin mode
      if (scanInput.trim() === 'admin') {
        setIsAdminMode(true);
        setScanInput('');
        return;
      }

      onNewScan(scanInput.trim());
      setScanInput('');
      
      // Refocus the input after a short delay
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
    }
  };

  // Generate random DataMatrix code
  const generateRandomCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    const length = 12; // Typical DataMatrix code length
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };

  // Handle admin mode scan
  const handleAdminScan = () => {
    if (!isProcessing) {
      const randomCode = generateRandomCode();
      onNewScan(randomCode);
    }
  };

  // Start a new scanning session
  const startSession = () => {
    onStartSession();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Continue existing session
  const continueExistingSession = async () => {
    await onContinueSession();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Complete the current session
  const completeSession = () => {
    onCompleteSession();
    setIsAdminMode(false);
  };

  // Calculate progress percentage
  const progress = session ? (
    session.currentBoxItems === 0 && session.scannedItems > 0 
      ? 100 // Show full progress when box is full (currentBoxItems is 0 but we have scanned items)
      : (session.currentBoxItems / boxCapacity) * 100
  ) : 0;

  const isScanning = session?.status === 'active';

  return (
    <div className="flex flex-col h-full">
      {/* Main content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-gray-50 dark:bg-gray-900">
        {/* Main content container */}
        <div className="w-full max-w-3xl flex flex-col items-center h-full">
          <div className="flex flex-col items-center w-full">
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              {isScanning ? (isProcessing ? 'ОБРАБОТКА...' : 'СКАНИРОВАНИЕ') : 'ГОТОВ К СКАНИРОВАНИЮ'}
              {isAdminMode && ' (РЕЖИМ АДМИНИСТРАТОРА)'}
            </h2>
            
            {layoutError && (
              <div className="mb-4 p-4 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700 rounded-lg shadow-sm w-full">
                <div className="flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-amber-400 dark:text-amber-500 mr-3 flex-shrink-0" />
                  <p className="text-amber-800 dark:text-amber-200 font-medium">
                    {layoutError}
                  </p>
                </div>
              </div>
            )}

            <div className="flex flex-col items-center space-y-8 w-full">
              {session && currentCode && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 w-full">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {session.scannedItems} / {Math.floor(session.scannedItems / session.boxCapacity)}
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Сканов/Коробов
                  </p>
                </div>
              )}

              {!currentCode && (
                <div className="bg-gray-100 dark:bg-gray-800 p-12 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 w-full">
                  <p className="text-gray-400 dark:text-gray-500">
                    {isScanning 
                      ? 'Отсканируйте DataMatrix код...' 
                      : 'Начните новую сессию для сканирования'}
                  </p>
                </div>
              )}

              {/* Progress bar */}
              {isScanning && (
                <div className="w-full">
                  <ProgressBox
                    current={session?.currentBoxItems || 0}
                    total={boxCapacity}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Manual input form */}
          {isScanning && (
            <form onSubmit={handleScan} className="w-full mt-auto">
              <div className="flex rounded-md shadow-sm">
                <input
                  ref={inputRef}
                  type="text"
                  value={scanInput}
                  onChange={(e) => setScanInput(e.target.value)}
                  placeholder={isScanning ? (isProcessing ? "Обработка..." : "Введите или отсканируйте код...") : "Начните сессию для сканирования"}
                  disabled={!isScanning || isProcessing}
                  className="flex-1 min-w-0 block w-full px-4 py-3 rounded-l-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500 sm:text-sm placeholder-gray-400 dark:placeholder-gray-500"
                />
                <button
                  type="submit"
                  disabled={!isScanning || !scanInput.trim() || isProcessing}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Добавить
                </button>
                {isAdminMode && (
                  <button
                    type="button"
                    onClick={handleAdminScan}
                    disabled={isProcessing}
                    className="ml-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Имитировать сканирование
                  </button>
                )}
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="sticky bottom-0 p-6 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap justify-center gap-4">
          {!isScanning ? (
            <>
              <button
                onClick={continueExistingSession}
                className="inline-flex items-center px-4 py-2 sm:px-6 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 whitespace-nowrap"
              >
                <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
                Продолжить сессию
              </button>
              <button
                onClick={startSession}
                className="inline-flex items-center px-4 py-2 sm:px-6 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 dark:focus:ring-offset-gray-800 whitespace-nowrap"
              >
                <PlayIcon className="-ml-1 mr-2 h-5 w-5" />
                Начать новую сессию
              </button>
            </>
          ) : (
            <>
              <button
                onClick={completeSession}
                className="inline-flex items-center px-4 py-2 sm:px-6 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:focus:ring-offset-gray-800 whitespace-nowrap"
              >
                <StopIcon className="-ml-1 mr-2 h-5 w-5" />
                Завершить сессию
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
