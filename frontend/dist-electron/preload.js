"use strict";
const require$$0 = require("electron");
var preload = {};
const { contextBridge, ipcRenderer } = require$$0;
contextBridge.exposeInMainWorld("electronAPI", {
  getVersion: () => ipcRenderer.invoke("get-version")
});
module.exports = preload;
