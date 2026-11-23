// preload.cjs - Context isolation preload script for Digital Wellness Assistant
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopAPI', {
  platform: process.platform,
  isDesktop: true,
  getVersion: () => '1.0.0',
});
