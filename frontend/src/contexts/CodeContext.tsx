import { createContext, useContext } from 'react';
import { CodeContextType } from '../types';

export const CodeContext = createContext<CodeContextType | undefined>(undefined);

export const useCodeContext = () => {
  const context = useContext(CodeContext);
  if (context === undefined) {
    throw new Error('useCodeContext must be used within a CodeProvider');
  }
  return context;
};
