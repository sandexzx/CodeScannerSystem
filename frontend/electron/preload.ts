import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron';

declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>;
    };
  }
}

contextBridge.exposeInMainWorld('electronAPI', {
  getVersion: () => ipcRenderer.invoke('get-version'),
  // We'll add more methods here as needed
});

declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>;
    };
  }
}
