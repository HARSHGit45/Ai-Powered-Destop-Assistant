const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
}

function startPythonProcess() {
    // Start the Python process
    pythonProcess = spawn('python', ['backend/speech_recognition_service.py']);

    pythonProcess.stdout.on('data', (data) => {
        try {
            const result = JSON.parse(data.toString());
            if (result.error) {
                mainWindow.webContents.send('recognition-error', result.error);
            } else {
                mainWindow.webContents.send('recognition-result', result);
            }
        } catch (error) {
            console.error('Error parsing Python output:', error);
            mainWindow.webContents.send('recognition-error', 'Failed to parse response');
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log('Python stderr:', data.toString());
        mainWindow.webContents.send('recognition-status', data.toString());
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        if (code !== 0) {
            mainWindow.webContents.send('recognition-error', 'Python process terminated unexpectedly');
        }
    });
}

app.whenReady().then(() => {
    createWindow();
    startPythonProcess();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (pythonProcess) {
            pythonProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle start listening request from renderer
ipcMain.on('start-listening', () => {
    if (pythonProcess) {
        pythonProcess.stdin.write('START_LISTENING\n');
    }
});

// Handle stop listening request from renderer
ipcMain.on('stop-listening', () => {
    if (pythonProcess) {
        pythonProcess.stdin.write('STOP_LISTENING\n');
    }
}); 