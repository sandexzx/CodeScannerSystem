export interface ScanSession {
  id: string;
  startTime: string;
  endTime?: string;
  status: 'active' | 'completed' | 'cancelled';
  boxCapacity: number;
  scannedItems: number;
  currentBoxItems: number;
}

export interface CodeHistoryItem {
  code: string;
  timestamp: string;
  sessionId: string;
}

export interface CodeContextType {
  currentCode: string;
  session: ScanSession | null;
  codeHistory: CodeHistoryItem[];
  boxCapacity: number;
  isAdminMode: boolean;
  setIsAdminMode: (isAdmin: boolean) => void;
  onNewScan: (code: string) => void;
  onStartSession: () => void;
  onContinueSession: () => void;
  onCompleteSession: () => void;
  onUpdateBoxCapacity: (capacity: number) => void;
}
