const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    }
  });
  // win.webContents.openDevTools();
  win.loadFile('index.html');

  const { spawn } = require('child_process');

  ipcMain.on('select-pdf', async () => {
    try {
      const result = await dialog.showOpenDialog(win, {
        properties: ['openFile'],
        filters: [{ name: 'PDFs', extensions: ['pdf'] }]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const pdfPath = `file://${result.filePaths[0]}`;
        win.webContents.send('load-pdf', pdfPath);
      }
    } catch (err) {
      console.error('Dialog error:', err);
    }
  });
  ipcMain.on('run-command', (event, cmd) => {
    // Split the command string into arguments (handles quoted filenames)
    const args = cmd.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
    const python = spawn('python', ['cli_handler.py', ...args], {
        cwd: __dirname
    });

    let result = '';

    python.stdout.on('data', (data) => {
        result += data.toString();
    });

    python.stderr.on('data', (data) => {
        result += `Error: ${data.toString()}`;
    });

    python.on('close', () => {
        event.sender.send('command-result', result.trim());
    });
  });
  ipcMain.on('extract-outlines', (event, pdfPath) => {
    const { spawn } = require('child_process');
    const py = spawn('python3', ['outline_wrapper.py', pdfPath]);

    py.stdout.on('data', (data) => {
      event.sender.send('outline-log', data.toString());
    });

    py.stderr.on('data', (data) => {
      event.sender.send('outline-log', `[ERROR] ${data.toString()}`);
    });

    py.on('close', (code) => {
      event.sender.send('outline-log', `\nProcess exited with code ${code}`);
    });
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
