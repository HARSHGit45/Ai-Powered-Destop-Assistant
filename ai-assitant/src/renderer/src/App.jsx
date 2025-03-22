import { motion } from 'framer-motion'
import { CiMicrophoneOn } from 'react-icons/ci'

function App() {
  return (
    <>
      <div className="text-center mt-5">
        <motion.span
          className="text-5xl font-extrabold inline-block mr-3"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          Welcome,
        </motion.span>
        <motion.span
          className="text-5xl font-extrabold text-blue-600 inline-block"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          {[...'ai-assitant'].map((char, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{
                duration: 0.2,
                delay: 1 + index * 0.1
              }}
            >
              {char}
            </motion.span>
          ))}
        </motion.span>
      </div>
      <div className="flex justify-center mt-4">
        <CiMicrophoneOn className="w-10 h-10 cursor-pointer" />
      </div>
    </>
  )
}

export default App
