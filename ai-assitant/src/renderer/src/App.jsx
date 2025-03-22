import { motion } from 'framer-motion'
import { CiMicrophoneOn, CiMicrophoneOff } from 'react-icons/ci'
import { useState } from 'react'
import { FiSend } from 'react-icons/fi'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [messages, setMessages] = useState([
    { text: 'Hello! How can I assist you today?', isAI: true }
  ])
  const [inputText, setInputText] = useState('')

  const handleMicClick = () => {
    setIsListening(!isListening)
  }

  const handleSendMessage = () => {
    if (inputText.trim()) {
      setMessages([...messages, { text: inputText, isAI: false }])
      setInputText('')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-4xl font-bold mb-2">AI Assistant</h1>
          <p className="text-gray-400">Your intelligent desktop companion</p>
        </motion.div>

        {/* Chat Container */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-4 mb-4">
          <div className="h-[400px] overflow-y-auto mb-4 space-y-4">
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: message.isAI ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.isAI ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-[70%] p-3 rounded-lg ${
                    message.isAI
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-white'
                  }`}
                >
                  {message.text}
                </div>
              </motion.div>
            ))}
          </div>

          {/* Input Area */}
          <div className="flex items-center gap-3 bg-gray-700 rounded-lg p-3">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleMicClick}
              className={`p-2 rounded-full ${isListening ? 'bg-red-500' : 'bg-blue-600'}`}
            >
              {isListening ? (
                <CiMicrophoneOff className="w-6 h-6" />
              ) : (
                <CiMicrophoneOn className="w-6 h-6" />
              )}
            </motion.button>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-400"
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSendMessage}
              className="p-2 rounded-full bg-blue-600"
            >
              <FiSend className="w-5 h-5" />
            </motion.button>
          </div>
        </div>

        {/* Status Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-sm text-gray-400"
        >
          {isListening ? 'Listening...' : 'Click the microphone or type to start'}
        </motion.div>
      </div>
    </div>
  )
}

export default App
