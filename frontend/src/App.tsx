import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Navigation } from './components/Navigation';
import { CodeContext } from './contexts/CodeContext';
import { ScanSession, CodeHistoryItem } from './types';

function App() {
  const [currentCode, setCurrentCode] = useState<string>('');
  const [session, setSession] = useState<ScanSession | null>(null);
  const [codeHistory, setCodeHistory] = useState<CodeHistoryItem[]>([]);
  const [boxCapacity, setBoxCapacity] = useState<number>(10);
  const navigate = useNavigate();

  // Load saved settings on initial render
  useEffect(() => {
    const savedBoxCapacity = localStorage.getItem('boxCapacity');
    if (savedBoxCapacity) {
      setBoxCapacity(parseInt(savedBoxCapacity, 10));
    }
  }, []);

  // Handle new scan
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Новый handleNewScan: отправляет запрос на backend
  const handleNewScan = async (code: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Scan failed');
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
        
        // Update session with incremented scannedItems
        if (session) {
          setSession({
            ...session,
            scannedItems: session.scannedItems + 1
          });
        }
      }
    } catch (e: any) {
      setError(e.message || 'Scan error');
    } finally {
      setLoading(false);
    }
  };

  // Start new session
  const startNewSession = () => {
    const newSession: ScanSession = {
      id: `session-${Date.now()}`,
      startTime: new Date().toISOString(),
      status: 'active',
      boxCapacity,
      scannedItems: 0
    };
    setSession(newSession);
    setCurrentCode('');
    setCodeHistory([]);
  };

  // Complete session
  const completeSession = () => {
    if (session) {
      setSession({
        ...session,
        status: 'completed',
        endTime: new Date().toISOString()
      });
    }
  };

  // Update box capacity
  const updateBoxCapacity = (capacity: number) => {
    setBoxCapacity(capacity);
    localStorage.setItem('boxCapacity', capacity.toString());
  };

  return (
    <CodeContext.Provider value={{ 
      currentCode, 
      session, 
      codeHistory, 
      boxCapacity,
      onNewScan: handleNewScan,
      onStartSession: startNewSession,
      onCompleteSession: completeSession,
      onUpdateBoxCapacity: updateBoxCapacity
    }}>
      <div className="flex flex-col h-screen">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <h1 className="text-2xl font-semibold text-gray-900">DataMatrix Scanner</h1>
          {session && (
            <div className="mt-2 text-sm text-gray-500">
              Session: {new Date(session.startTime).toLocaleString()} • 
              Scanned: {codeHistory.length} of {boxCapacity} • 
              <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                session.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {session.status.toUpperCase()}
              </span>
            </div>
          )}
          {loading && <div className="text-blue-500 mt-2">Scanning...</div>}
          {error && <div className="text-red-500 mt-2">{error}</div>}
        </header>
        
        <main className="flex-1 overflow-hidden">
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
