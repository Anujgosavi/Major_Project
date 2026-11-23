// main.cjs - Electron Main Process for Digital Wellness Assistant
const { app, BrowserWindow, session, shell, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec } = require('child_process');

let mainWindow = null;
let splashWindow = null;
let backendProcess = null;
const BACKEND_PORT = 5000;
let isQuitting = false;

// Determine backend executable path
function getBackendExecutable() {
  if (app.isPackaged) {
    return path.join(
      process.resourcesPath,
      'python-backend',
      'wellness_backend',
      'wellness_backend.exe'
    );
  } else {
    // Development mode
    const distExe = path.join(__dirname, '..', 'dist', 'wellness_backend', 'wellness_backend.exe');
    if (fs.existsSync(distExe)) {
      return distExe;
    }
    return null;
  }
}

// Check backend health endpoint
function checkHealth(port) {
  return new Promise((resolve) => {
    const req = http.get(
      {
        hostname: '127.0.0.1',
        port: port,
        path: '/health',
        timeout: 1000,
      },
      (res) => {
        if (res.statusCode === 200) {
          resolve(true);
        } else {
          resolve(false);
        }
      }
    );
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Poll health check until ready or timed out
async function waitForBackend(port, maxWaitMs = 45000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWaitMs) {
    const healthy = await checkHealth(port);
    if (healthy) return true;
    await new Promise((r) => setTimeout(r, 600));
  }
  return false;
}

// Start backend process
function startBackend(port) {
  const exePath = getBackendExecutable();

  if (exePath && fs.existsSync(exePath)) {
    console.log(`[Desktop] Starting bundled backend executable: ${exePath}`);
    backendProcess = spawn(
      exePath,
      ['--host', '127.0.0.1', '--port', String(port)],
      {
        cwd: path.dirname(exePath),
        windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe'],
      }
    );
  } else {
    // Development fallback to system python
    console.log('[Desktop] Standalone backend exe not found, launching python source...');
    const pythonScript = path.join(__dirname, '..', 'backend', 'api', 'server.py');
    backendProcess = spawn(
      'python',
      [pythonScript, '--host', '127.0.0.1', '--port', String(port)],
      {
        cwd: path.join(__dirname, '..'),
        windowsHide: false,
        stdio: ['ignore', 'pipe', 'pipe'],
      }
    );
  }

  if (backendProcess) {
    backendProcess.stdout?.on('data', (d) => {
      console.log(`[Python stdout] ${d.toString().trim()}`);
    });
    backendProcess.stderr?.on('data', (d) => {
      console.error(`[Python stderr] ${d.toString().trim()}`);
    });
    backendProcess.on('exit', (code, sig) => {
      console.log(`[Python process exited] code=${code}, signal=${sig}`);
    });
  }
}

// Safely kill backend process tree
function killBackend() {
  if (!backendProcess || !backendProcess.pid) return;

  const pid = backendProcess.pid;
  console.log(`[Desktop] Terminating backend process tree (PID: ${pid})...`);

  // Try graceful shutdown endpoint first
  try {
    const req = http.request({
      hostname: '127.0.0.1',
      port: BACKEND_PORT,
      path: '/api/shutdown',
      method: 'POST',
      timeout: 1000,
    });
    req.on('error', () => {});
    req.end();
  } catch (e) {}

  // Force-kill process tree on Windows using taskkill
  setTimeout(() => {
    if (process.platform === 'win32') {
      exec(`taskkill /pid ${pid} /T /F`, () => {});
    } else {
      try {
        process.kill(-pid, 'SIGKILL');
      } catch (e) {
        backendProcess.kill('SIGKILL');
      }
    }
    backendProcess = null;
  }, 300);
}

// Create splash window
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 440,
    height: 320,
    frame: false,
    resizable: false,
    transparent: false,
    backgroundColor: '#0f172a',
    center: true,
    alwaysOnTop: true,
    show: false,
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.once('ready-to-show', () => {
    splashWindow.show();
  });
}

// Create main window
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 880,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#0b1120',
    title: 'Digital Wellness Assistant',
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.cjs'),
    },
  });

  // Automatically approve camera/microphone permissions for local application
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === 'media') {
      callback(true);
      return;
    }
    callback(false);
  });

  // Restrict navigation away from localhost
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://127.0.0.1') || url.startsWith('http://localhost')) {
      return { action: 'allow' };
    }
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Load the backend-served React UI
  mainWindow.loadURL(`http://127.0.0.1:${BACKEND_PORT}/`);

  mainWindow.once('ready-to-show', () => {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      isQuitting = true;
      killBackend();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(async () => {
  createSplashWindow();

  startBackend(BACKEND_PORT);

  const ready = await waitForBackend(BACKEND_PORT);

  if (ready) {
    createMainWindow();
  } else {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
    }
    dialog.showErrorBox(
      'Startup Error',
      'The Digital Wellness AI backend failed to start within 45 seconds.\n\nPlease ensure your webcam is connected and try launching the application again.'
    );
    killBackend();
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  killBackend();
});

app.on('window-all-closed', () => {
  isQuitting = true;
  killBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
