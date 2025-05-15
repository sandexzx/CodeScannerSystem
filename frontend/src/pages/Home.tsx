import { useState, useEffect, useRef } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { PlayIcon, StopIcon, ArrowPathIcon } from '@heroicons/react/24/solid';

export const Home = () => {
  const {
    currentCode,
    session,
    onNewScan,
    onStartSession,
    onCompleteSession,
    boxCapacity,
  } = useCodeContext();
  
  const [isScanning, setIsScanning] = useState(false);
  const [scanInput, setScanInput] = useState('');
  const [isAdminMode, setIsAdminMode] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when the component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Handle barcode scanning
  const handleScan = (e: React.FormEvent) => {
    e.preventDefault();
    if (scanInput.trim()) {
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
    const randomCode = generateRandomCode();
    onNewScan(randomCode);
  };

  // Start a new scanning session
  const startSession = () => {
    onStartSession();
    setIsScanning(true);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Complete the current session
  const completeSession = () => {
    onCompleteSession();
    setIsScanning(false);
    setIsAdminMode(false);
  };

  // Calculate progress percentage
  const progress = session ? (
    session.currentBoxItems === 0 && session.scannedItems > 0 
      ? 100 // Show full progress when box is full (currentBoxItems is 0 but we have scanned items)
      : (session.currentBoxItems / boxCapacity) * 100
  ) : 0;

  return (
    <div className="flex flex-col h-full">
      {/* Main content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        {/* Current code display */}
        <div className="w-full max-w-2xl mb-8">
          <h2 className="text-sm font-medium text-gray-500 mb-2">
            {isScanning ? 'SCANNING' : 'READY TO SCAN'}
            {isAdminMode && ' (ADMIN MODE)'}
          </h2>
          
          {currentCode ? (
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
              <div className="text-4xl font-mono font-bold tracking-wider break-all">
                {currentCode}
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Scanned at: {new Date().toLocaleTimeString()}
              </p>
            </div>
          ) : (
            <div className="bg-gray-50 p-12 rounded-xl border-2 border-dashed border-gray-200">
              <p className="text-gray-400">
                {isScanning 
                  ? 'Scan a DataMatrix code...' 
                  : 'Start a new session to begin scanning'}
              </p>
            </div>
          )}
        </div>

        {/* Progress bar */}
        {isScanning && (
          <div className="w-full max-w-md mb-8">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Scanned: {session?.currentBoxItems || 0}</span>
              <span>Capacity: {boxCapacity}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-primary-500 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, progress)}%` }}
              />
            </div>
          </div>
        )}

        {/* Manual input form */}
        <form onSubmit={handleScan} className="w-full max-w-md">
          <div className="flex rounded-md shadow-sm">
            <input
              ref={inputRef}
              type="text"
              value={scanInput}
              onChange={(e) => setScanInput(e.target.value)}
              disabled={!isScanning}
              placeholder={isScanning ? "Enter or scan a code..." : "Start a session to scan"}
              className="flex-1 min-w-0 block w-full px-4 py-3 rounded-l-md border-gray-300 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            />
            <button
              type="submit"
              disabled={!isScanning || !scanInput.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add
            </button>
            {isAdminMode && (
              <button
                type="button"
                onClick={handleAdminScan}
                className="ml-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Simulate Scan
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Action buttons */}
      <div className="p-6 bg-gray-50 border-t border-gray-200">
        <div className="flex justify-center space-x-4">
          {!isScanning ? (
            <button
              onClick={startSession}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <PlayIcon className="-ml-1 mr-2 h-5 w-5" />
              Start New Session
            </button>
          ) : (
            <>
              <button
                onClick={completeSession}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <StopIcon className="-ml-1 mr-2 h-5 w-5" />
                Complete Session
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
