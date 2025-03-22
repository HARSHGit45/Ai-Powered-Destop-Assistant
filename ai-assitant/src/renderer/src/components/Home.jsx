import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { CiMicrophoneOn } from 'react-icons/ci'
import { FiSend } from 'react-icons/fi'
import { IoIosChatbubbles } from 'react-icons/io'

const Home = () => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [inputText, setInputText] = useState('')
  const handleSend = () => {
    if (inputText.trim()) {
      console.log('Message sent:', inputText)
      setInputText('')
    }
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
            className="flex items-center bg-gray-800 rounded-full p-3 shadow-lg"
            initial={{ width: 60, opacity: 0 }}
            animate={{ width: 350, opacity: 1 }}
            exit={{ width: 60, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            <button
              className="p-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 mr-3"
              aria-label="Voice Input"
            >
              <CiMicrophoneOn className="w-5 h-5 text-white" />
            </button>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-transparent border-none outline-none text-white px-2"
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <div className="flex items-center">
              <button 
                className="p-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 ml-2"
                onClick={handleSend}
                aria-label="Send Message"
              >
                <FiSend className="w-5 h-5 text-white" />
              </button>
              <button
                className="px-2 rounded-full bg-gray-700 hover:bg-gray-600 ml-3"
                onClick={() => setIsExpanded(false)}
                aria-label="Close"
              >
                <span className="text-white text-sm">×</span>
              </button>
            </div>
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
