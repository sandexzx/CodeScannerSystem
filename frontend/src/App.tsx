import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Navigation } from './components/Navigation';
import { CodeContext } from './contexts/CodeContext';
import { ThemeSwitcher } from './components/ThemeSwitcher';
import { ScanSession, CodeHistoryItem } from './types';

function App() {
  const [currentCode, setCurrentCode] = useState<string>('');
  const [session, setSession] = useState<ScanSession | null>(null);
  const [codeHistory, setCodeHistory] = useState<CodeHistoryItem[]>([]);
  const [boxCapacity, setBoxCapacity] = useState<number>(12); // Default to 12 to match backend
  const [isAdminMode, setIsAdminMode] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme === 'dark';
    }
    // Если нет сохраненной темы, используем системные настройки
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Load initial settings from backend
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/settings');
        if (response.ok) {
          const data = await response.json();
          setBoxCapacity(data.box_capacity);
        }
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    };
    loadSettings();
  }, []);

  // Load saved settings on initial render
  useEffect(() => {
    // Применяем класс темы к HTML элементу
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    // Сохраняем тему в localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  // Handle new scan
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Continue existing session
  const continueSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5001/api/continue-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to continue session');
      }
      const data = await response.json();
      const newSession: ScanSession = {
        id: data.sessionId,
        startTime: data.startTime,
        status: 'active',
        boxCapacity: data.boxCapacity,
        scannedItems: data.scannedItems,
        currentBoxItems: data.currentBoxItems
      };
      setSession(newSession);
      setCurrentCode('');
      setCodeHistory([]);
    } catch (e: any) {
      setError(e.message || 'Failed to continue session');
    } finally {
      setLoading(false);
    }
  };

  // Новый handleNewScan: отправляет запрос на backend
  const handleNewScan = async (code: string) => {
    if (isProcessing) return; // Блокируем новый сканирование если предыдущий код еще обрабатывается
    
    setIsProcessing(true);
    setLoading(true);
    setError(null);

    // Сразу разблокируем ввод после отправки запроса
    const responsePromise = fetch('http://localhost:5001/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });

    // Разблокируем ввод сразу
    setIsProcessing(false);
    
    try {
      const response = await responsePromise;
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Scan failed');
      }
      const data = await response.json();
      // Only add to history if we got a valid code back
      if (data.result) {
        const timestamp = new Date().toISOString();
        const newCode: CodeHistoryItem = {
          code: data.result,
          timestamp,
          sessionId: session?.id || 'default-session'
        };
        setCurrentCode(data.result);
        setCodeHistory(prev => [newCode, ...prev].slice(0, 100));
        
        // Синхронизируем состояние с бэкендом
        const syncResponse = await fetch('http://localhost:5001/api/continue-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (syncResponse.ok) {
          const syncData = await syncResponse.json();
          if (session) {
            setSession({
              ...session,
              scannedItems: syncData.scannedItems,
              currentBoxItems: syncData.currentBoxItems
            });
          }
        }
      }
    } catch (e: any) {
      setError(e.message || 'Scan error');
    } finally {
      setLoading(false);
    }
  };

  // Start new session
  const startNewSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5001/api/start-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to start session');
      }
      const data = await response.json();
      const newSession: ScanSession = {
        id: data.sessionId,
        startTime: data.startTime,
        status: 'active',
        boxCapacity: data.boxCapacity,
        scannedItems: data.scannedItems,
        currentBoxItems: data.currentBoxItems
      };
      setSession(newSession);
      setCurrentCode('');
      setCodeHistory([]);
    } catch (e: any) {
      setError(e.message || 'Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  // Complete session
  const completeSession = async () => {
    if (session) {
      try {
        const response = await fetch('http://localhost:5001/api/complete-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.error || 'Failed to complete session');
        }
        setSession(null);
        setCurrentCode('');
        setCodeHistory([]);
      } catch (e: any) {
        setError(e.message || 'Failed to complete session');
      }
    }
  };

  // Update box capacity
  const updateBoxCapacity = async (capacity: number) => {
    try {
      const response = await fetch('http://localhost:5001/api/settings/box-capacity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ capacity }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setBoxCapacity(data.box_capacity);
      } else {
        const error = await response.json();
        console.error('Failed to update box capacity:', error.error);
      }
    } catch (error) {
      console.error('Error updating box capacity:', error);
    }
  };

  return (
    <CodeContext.Provider value={{ 
      currentCode, 
      session, 
      codeHistory, 
      boxCapacity,
      isAdminMode,
      isProcessing,
      setIsAdminMode,
      onNewScan: handleNewScan,
      onStartSession: startNewSession,
      onContinueSession: continueSession,
      onCompleteSession: completeSession,
      onUpdateBoxCapacity: updateBoxCapacity
    }}>
      <div className="flex flex-col h-screen">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 h-[104px]">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Сканер DataMatrix</h1>
            <ThemeSwitcher isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
          </div>
          {session && (
            <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 h-[32px] flex items-center">
              Сессия: {new Date(session.startTime).toLocaleString()} • 
              <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                session.status === 'active' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-100' 
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-100'
              }`}>
                {session.status === 'active' ? 'АКТИВНА' : session.status === 'completed' ? 'ЗАВЕРШЕНА' : 'ОТМЕНЕНА'}
              </span>
              {loading && (
                <span className="ml-2 inline-flex items-center px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-100 animate-pulse">
                  <span className="relative flex h-2 w-2 mr-1">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                  </span>
                  Сканирование...
                </span>
              )}
            </div>
          )}
          {error && <div className="text-red-500 mt-2">{error}</div>}
        </header>
        
        <main className="flex-1 overflow-hidden bg-gray-50 dark:bg-gray-900 pt-2">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
        
        <Navigation />
      </div>
    </CodeContext.Provider>
  );
}

export default App;
