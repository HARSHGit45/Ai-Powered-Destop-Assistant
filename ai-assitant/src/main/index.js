import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { spawn } from 'child_process'
import record from 'node-record-lpcm16'

import os from 'os'

let pythonProcess = null;
let mainWindow = null;
let recordingStream = null;

function initializePythonProcess() {
  if (pythonProcess) {
    console.log('Python process already initialized');
    return; // Already initialized
  }

  console.log('Initializing Python process...');
  const scriptPath = join(__dirname, '../../../backend/main_classify.py')
  pythonProcess = spawn('python', [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  })

  console.log('Python process spawned, setting up event handlers...');

  pythonProcess.stdout.on('data', (data) => {
    try {
      // Split the data into lines and process each line
      const lines = data.toString().split('\n').filter(line => line.trim());
      
      // Process each line
      for (const line of lines) {
        try {
          // Try to parse as JSON first
          const result = JSON.parse(line);
          if (mainWindow && !mainWindow.isDestroyed()) {
            console.log('Sending JSON result to renderer:', result);
            mainWindow.webContents.send('command-result', result);
          }
        } catch (parseError) {
          // If not JSON, send as raw output
          if (mainWindow && !mainWindow.isDestroyed() && line.trim()) {
            console.log('Sending raw output to renderer:', line);
            mainWindow.webContents.send('command-result', {
              success: true,
              raw_output: line.trim()
            });
          }
        }
      }
    } catch (error) {
      console.error('Error processing Python output:', error);
    }
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error('Python Error:', data.toString())
  })

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`)
    pythonProcess = null
  })

  pythonProcess.on('error', (error) => {
    console.error('Failed to start Python process:', error)
    pythonProcess = null
  })

  // Add ready event handler
  pythonProcess.on('spawn', () => {
    console.log('Python process spawned successfully');
  });

  console.log('Python process initialization complete');
}

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: true
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
    // Initialize Python process after window is shown
    initializePythonProcess()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // Handle text commands
  ipcMain.on('process-command', (_, data) => {
    console.log('Received command from renderer:', data);
    
    if (!pythonProcess) {
      console.log('Python process not initialized, initializing now...');
      initializePythonProcess()
    }
    
    if (pythonProcess && pythonProcess.stdin.writable) {
      console.log('Sending command to Python process:', data);
      const commandData = JSON.stringify(data) + '\n'
      pythonProcess.stdin.write(commandData)
    } else {
      console.error('Python process not ready or stdin not writable');
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('command-result', {
          success: false,
          error: 'Python process not ready'
        })
      }
    }
  })

  // Handle voice recording
  ipcMain.on('start-recording', () => {
    const tempFile = join(os.tmpdir(), 'voice-input.wav')
    
    recordingStream = record.record({
      sampleRate: 16000,
      channels: 1,
      audioType: 'wav',
      filename: tempFile
    })
    
    recordingStream.stream().on('error', (err) => {
      console.error('Recording error:', err)
      mainWindow.webContents.send('recording-error', err.message)
    })
  })

  ipcMain.on('stop-recording', () => {
    if (recordingStream) {
      recordingStream.stop()
      recordingStream = null
    }
  })

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pythonProcess) {
      pythonProcess.kill()
      pythonProcess = null
    }
    app.quit()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
