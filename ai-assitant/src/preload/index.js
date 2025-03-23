import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  // Send command to main process
  processCommand: (command) => {
    try {
      ipcRenderer.send('process-command', command)
      return true
    } catch (error) {
      console.error('Error sending command:', error)
      return false
    }
  },
  // Listen for command results
  onCommandResult: (callback) => {
    try {
      const subscription = (_event, result) => callback(result)
      ipcRenderer.on('command-result', subscription)
      return () => {
        ipcRenderer.removeListener('command-result', subscription)
      }
    } catch (error) {
      console.error('Error setting up command result listener:', error)
      return () => {}
    }
  }
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error('Error exposing APIs:', error)
  }
} else {
  window.electron = electronAPI
  window.api = api
}