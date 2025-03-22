import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { CiMicrophoneOn } from 'react-icons/ci'
import { FiSend } from 'react-icons/fi'
import { IoIosChatbubbles } from 'react-icons/io'
import { FaTasks, FaFileAlt, FaSearch } from 'react-icons/fa'
import { GrServices } from 'react-icons/gr'

const Home = () => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [inputText, setInputText] = useState('')

  const speakWelcome = () => {
    if ('speechSynthesis' in window) {
      const message = new SpeechSynthesisUtterance('Welcome to Anshukal')
      message.rate = 1.0
      message.pitch = 1.0
      message.volume = 1.0
      window.speechSynthesis.speak(message);
    }
  }

  useEffect(() => {
    if (isExpanded) {
      speakWelcome()
    }
  }, [isExpanded])

  const handleSend = () => {
    if (inputText.trim()) {
      console.log('Message sent:', inputText)
      setInputText('')
    }
  }

  const handleTaskSelect = (task) => {
    console.log(`Selected task: ${task}`)
    // You can add functionality for each task here
  }

  const titleText = 'Welcome to Anshukal'
  const letterVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.05,
        duration: 0.6,
        ease: [0.22, 1, 0.36, 1]
      }
    })
  }

  return (
    <div className="flex flex-col gap-12 items-center justify-center min-h-screen">
      <motion.div
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.div
          className="overflow-hidden relative"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            duration: 1.5,
            background: {
              duration: 8,
              repeat: Infinity,
              repeatType: 'reverse'
            }
          }}
        >
          <div className="flex justify-center mb-2">
            {titleText.split('').map((char, i) => (
              <motion.span
                key={i}
                custom={i}
                variants={letterVariants}
                initial="hidden"
                animate="visible"
                className="text-5xl md:text-6xl lg:text-7xl xl:text-8xl tracking-tight text-transparent bg-clip-text font-bold bg-gradient-to-b from-gray-600 via-white to-gray-300 inline-block"
                style={{ textShadow: '0 10px 30px rgba(0,0,0,0.5)' }}
              >
                {char === ' ' ? '\u00A0' : char}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </motion.div>

      <AnimatePresence>
        {isExpanded ? (
          <motion.div
            className="flex flex-col bg-stone-900/70 rounded-xl p-4 shadow-lg max-w-md w-full"
            initial={{ height: 60, opacity: 0, width: 60, borderRadius: 30 }}
            animate={{ height: 'auto', opacity: 1, width: '100%', borderRadius: 12 }}
            exit={{ height: 60, opacity: 0, width: 60, borderRadius: 30 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            <div className="text-center mb-4">
              <motion.p
                className="text-gray-300 text-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                How can I help you today?
              </motion.p>
            </div>

            {/* Task Options */}
            <motion.div
              className="grid grid-cols-2 gap-3 mb-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <motion.button
                className="flex flex-col items-center justify-center p-3 bg-indigo-600/60 hover:bg-indigo-600 rounded-lg text-white"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleTaskSelect('Create Task')}
              >
                <FaTasks className="text-xl mb-1" />
                <span className="text-sm">Create Task</span>
              </motion.button>

              <motion.button
                className="flex flex-col items-center justify-center p-3 bg-purple-600/60 hover:bg-purple-600 rounded-lg text-white"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleTaskSelect('Set Reminder')}
              >
                <GrServices className="text-xl mb-1" />
                <span className="text-sm">system control operations</span>
              </motion.button>

              <motion.button
                className="flex flex-col items-center justify-center p-3 bg-blue-600/60 hover:bg-blue-600 rounded-lg text-white"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleTaskSelect('Take Notes')}
              >
                <FaFileAlt className="text-xl mb-1" />
                <span className="text-sm">Take Notes</span>
              </motion.button>

              <motion.button
                className="flex flex-col items-center justify-center p-3 bg-cyan-600/60 hover:bg-cyan-600 rounded-lg text-white"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleTaskSelect('Web Search')}
              >
                <FaSearch className="text-xl mb-1" />
                <span className="text-sm">Web Search</span>
              </motion.button>
            </motion.div>

            {/* Input Area */}
            <motion.div 
              className="flex items-center gap-2 bg-gray-700 rounded-full p-2 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <button
                className="p-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                aria-label="Voice Input"
              >
                <CiMicrophoneOn className="w-5 h-5 text-white" />
              </button>

              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Or type your request..."
                className="flex-1 bg-transparent border-none outline-none text-white px-2"
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />

              <button 
                className="p-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                onClick={handleSend}
                aria-label="Send Message"
              >
                <FiSend className="w-5 h-5 text-white" />
              </button>
            </motion.div>

            {/* Close Button */}
            <motion.button
              className="absolute top-3 right-3 w-6 h-6 rounded-full bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
              onClick={() => setIsExpanded(false)}
              aria-label="Close"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <span className="text-white text-sm">×</span>
            </motion.button>
          </motion.div>
        ) : (
          <motion.button
            className="p-4 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsExpanded(true)}
            aria-label="Open Assistant"
            initial={{ opacity: 0 }}
            animate={{
              opacity: 1,
              y: [0, -10, 0],
              transition: {
                y: {
                  repeat: Infinity,
                  duration: 1.5,
                  ease: 'easeInOut'
                }
              }
            }}
            exit={{ opacity: 0 }}
          >
            <IoIosChatbubbles className="w-6 h-6 text-white" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Home
