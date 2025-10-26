const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendCommand: (cmd) => ipcRenderer.send('run-command', cmd),
  onCommandResult: (callback) => ipcRenderer.on('command-result', (event, result) => callback(result)),
  selectPDF: () => ipcRenderer.send('select-pdf'),
  loadPDF: (callback) => ipcRenderer.on('load-pdf', (event, filePath) => callback(filePath)),
  extractOutlines: (pdfPath) => ipcRenderer.send('extract-outlines', pdfPath),
  onOutlineLog: (callback) => ipcRenderer.on('outline-log', (event, data) => callback(data))
});
