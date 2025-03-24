import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useMemo, useRef } from 'react'
import { CiMicrophoneOn } from 'react-icons/ci'
import { FiSend, FiTrash2, FiClock, FiCheckCircle, FiCircle, FiBell, FiX } from 'react-icons/fi'
import { IoIosChatbubbles } from 'react-icons/io'
import { FaTasks, FaFileAlt, FaSearch } from 'react-icons/fa'
import { GrServices } from 'react-icons/gr'

const Home = () => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [inputText, setInputText] = useState('')
  const [tasks, setTasks] = useState([])
  const [isCreatingTask, setIsCreatingTask] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDeadline, setNewTaskDeadline] = useState('')
  const [reminderActive, setReminderActive] = useState(false)
  const [reminderTask, setReminderTask] = useState(null)
  const [toast, setToast] = useState(null)
  const reminderTimeoutRef = useRef(null)
  const toastTimeoutRef = useRef(null)
  const [isListening, setIsListening] = useState(false)

  const speakWelcome = () => {
    if ('speechSynthesis' in window) {
      const message = new SpeechSynthesisUtterance('Welcome to Anshukal')
      message.rate = 1.0
      message.pitch = 1.0
      message.volume = 1.0
      window.speechSynthesis.speak(message)
    }
  }

  // Speak function for general notifications
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1.0
      utterance.pitch = 1.0
      utterance.volume = 1.0
      window.speechSynthesis.speak(utterance)
    }
  }

  // Function to check for upcoming deadlines
  const checkDeadlines = () => {
    if (pendingTasks.length === 0) return;

    const now = new Date();
    const thirtyMinutesFromNow = new Date(now.getTime() + 30 * 60 * 1000);

    // Find tasks that are due within 30 minutes
    const tasksNearingDeadline = pendingTasks.filter(task => {
      if (!task.deadline) return false;

      const deadline = new Date(task.deadline);
      // Task is due within the next 30 minutes but not past due
      return deadline > now && deadline <= thirtyMinutesFromNow;
    })
    // Sort by closest deadline first
    tasksNearingDeadline.sort((a, b) => new Date(a.deadline) - new Date(b.deadline))

    // If we found a task nearing deadline and no reminder is active
    if (tasksNearingDeadline.length > 0 && !reminderActive) {
      const taskToRemind = tasksNearingDeadline[0];
      const deadline = new Date(taskToRemind.deadline);
      const minutesRemaining = Math.floor((deadline - now) / (60 * 1000))

      // Set reminder state
      setReminderActive(true)
      setReminderTask(taskToRemind)

      // Speak the reminder
      speak(`Reminder: Task "${taskToRemind.title}" is due in ${minutesRemaining} minutes.`)

      // Show the reminder for 15 seconds, then reset
      if (reminderTimeoutRef.current) {
        clearTimeout(reminderTimeoutRef.current)
      }

      reminderTimeoutRef.current = setTimeout(() => {
        setReminderActive(false)
        setReminderTask(null)
      }, 15000)
    }
  }
  // Check deadlines every minute
  useEffect(() => {
    const interval = setInterval(checkDeadlines, 60000);

    checkDeadlines()

    return () => {
      clearInterval(interval)
      if (reminderTimeoutRef.current) {
        clearTimeout(reminderTimeoutRef.current)
      }
    };
  }, [tasks]) // Re-setup when tasks change

  useEffect(() => {
    if (isExpanded) {
      speakWelcome()
    }
  }, [isExpanded])

  const handleSend = () => {
    if (inputText.trim()) {
      // Send command to main process for classification
      window.api.processCommand({
        type: 'text',
        command: inputText.trim()
      });

      // Clear input after sending
      setInputText('');
    }
  }

  // Function to handle voice input
  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      showToast('Speech recognition is not supported in your browser');
      return;
    }

    if (!isListening) {
      // Create a new recognition instance
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        showToast('Listening... Speak your command');
      };

      recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        setInputText(text);
        
        // Send the recognized text to the same processCommand method
        window.api.processCommand({
          type: 'text',
          command: text.trim()
        });
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        showToast('Error with voice recognition. Please try again.');
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      // Start recognition
      recognition.start();
    } else {
      // Stop listening
      setIsListening(false);
      showToast('Voice input stopped');
    }
  };

  // Function to show toast message
  const showToast = (message) => {
    if (!message) return;
    
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    
    console.log('Setting toast message:', message);
    setToast(message);
    
    toastTimeoutRef.current = setTimeout(() => {
      console.log('Clearing toast message');
      setToast(null);
    }, 5000); // Hide after 5 seconds
  };

  const handleTaskSelect = (task) => {
    console.log(`Selected task: ${task}`)

    if (task === 'Create Task') {
      setIsCreatingTask(true)
    }
  }

  const handleCreateTask = () => {
    if (newTaskTitle.trim()) {
      const newTask = {
        id: Date.now(),
        title: newTaskTitle,
        completed: false,
        createdAt: new Date().toISOString(),
        deadline: newTaskDeadline ? new Date(newTaskDeadline).toISOString() : null
      }

      setTasks([...tasks, newTask])
      setNewTaskTitle('')
      setNewTaskDeadline('')
      setIsCreatingTask(false)

      if ('speechSynthesis' in window) {
        const message = new SpeechSynthesisUtterance(`Task created: ${newTaskTitle}`)
        window.speechSynthesis.speak(message)
      }

      // Check if deadlines need to be triggered immediately after adding a task
      setTimeout(checkDeadlines, 1000);
    }
  }

  const toggleTaskCompletion = (taskId) => {
    setTasks(
      tasks.map((task) => (task.id === taskId ? { ...task, completed: !task.completed } : task))
    )

    // If we're completing the task that has an active reminder, dismiss the reminder
    if (reminderActive && reminderTask && reminderTask.id === taskId) {
      setReminderActive(false);
      setReminderTask(null);
      if (reminderTimeoutRef.current) {
        clearTimeout(reminderTimeoutRef.current);
      }
    }
  }

  const deleteTask = (taskId) => {
    setTasks(tasks.filter((task) => task.id !== taskId))

    // If we're deleting the task that has an active reminder, dismiss the reminder
    if (reminderActive && reminderTask && reminderTask.id === taskId) {
      setReminderActive(false);
      setReminderTask(null);
      if (reminderTimeoutRef.current) {
        clearTimeout(reminderTimeoutRef.current);
      }
    }
  }

  const dismissReminder = () => {
    setReminderActive(false);
    setReminderTask(null);
    if (reminderTimeoutRef.current) {
      clearTimeout(reminderTimeoutRef.current);
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

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Organize tasks by completion status
  const pendingTasks = useMemo(() => tasks.filter((task) => !task.completed), [tasks])
  const completedTasks = useMemo(() => tasks.filter((task) => task.completed), [tasks])

  return (
    <div className="flex min-h-screen">
      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-50 max-w-md"
            initial={{ opacity: 0, y: 50, scale: 0.3 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
            transition={{ type: "spring", duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <p className="text-sm">{toast}</p>
              <button
                onClick={() => setToast(null)}
                className="ml-4 text-gray-400 hover:text-white"
              >
                <FiX className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content area */}
      <div className="flex-1 flex flex-col gap-8 items-center justify-center py-8 px-4">
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
            <div className="flex justify-center mb-2 head">
              {titleText.split('').map((char, i) => (
                <motion.span
                  key={i}
                  custom={i}
                  variants={letterVariants}
                  initial="hidden"
                  animate="visible"
                  className="text-4xl md:text-6xl lg:text-7xl xl:text-8xl text-transparent bg-clip-text font-bold bg-gradient-to-b from-gray-600 via-white to-gray-300 inline-block"
                  style={{ textShadow: '0 10px 30px rgba(0,0,0,0.5)' }}
                >
                  {char === ' ' ? '\u00A0' : char}
                </motion.span>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* Task Reminder Alert */}
        <AnimatePresence>
          {reminderActive && reminderTask && (
            <motion.div
              className="max-w-md w-full bg-amber-500/90 text-white p-4 rounded-lg shadow-lg absolute top-4 left-1/2 transform -translate-x-1/2 z-50"
              initial={{ opacity: 0, y: -50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ type: 'spring', damping: 20 }}
            >
              <div className="flex items-start">
                <div className="mr-3 mt-0.5">
                  <FiBell className="w-5 h-5 text-white animate-pulse" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">Task Due Soon!</h3>
                  <p className="text-sm mt-1">{reminderTask.title}</p>
                  <p className="text-xs mt-1">Due: {formatDate(reminderTask.deadline)}</p>
                  <div className="flex gap-2 mt-2">
                    <button
                      className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm"
                      onClick={() => toggleTaskCompletion(reminderTask.id)}
                    >
                      Complete
                    </button>
                    <button
                      className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded text-sm"
                      onClick={dismissReminder}
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isExpanded ? (
            <motion.div
              className="flex flex-col bg-stone-900/70 backdrop-blur-lg rounded-xl p-4 shadow-lg max-w-md w-full"
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

              <AnimatePresence>
                {isCreatingTask && (
                  <motion.div
                    className="mb-4 bg-gray-800/90 backdrop-blur-sm p-4 rounded-lg"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <h3 className="text-white text-lg mb-3 font-medium">Create New Task</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-gray-400 text-sm mb-1">Task Title</label>
                        <input
                          type="text"
                          value={newTaskTitle}
                          onChange={(e) => setNewTaskTitle(e.target.value)}
                          placeholder="Enter task name..."
                          className="w-full p-2 bg-gray-700/80 text-white rounded border-none outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-gray-400 text-sm mb-1">
                          Deadline (Optional)
                        </label>
                        <input
                          type="datetime-local"
                          value={newTaskDeadline}
                          onChange={(e) => setNewTaskDeadline(e.target.value)}
                          className="w-full p-2 bg-gray-700/80 text-white rounded border-none outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-4">
                      <button
                        className="px-3 py-1 bg-gray-600/30 text-white rounded hover:bg-gray-500 transition-colors"
                        onClick={() => setIsCreatingTask(false)}
                      >
                        Cancel
                      </button>
                      <button
                        className="px-3 py-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded hover:from-indigo-600 hover:to-purple-700 transition-colors"
                        onClick={handleCreateTask}
                      >
                        Create
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {!isCreatingTask && (
                <motion.div
                  className="grid grid-cols-2 gap-3 mb-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <motion.button
                    className="flex flex-col items-center justify-center p-3 bg-indigo-600/60 hover:bg-indigo-600 rounded-lg text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTaskSelect('Create Task')}
                  >
                    <FaTasks className="text-xl mb-1" />
                    <span className="text-sm">Create Task</span>
                  </motion.button>

                  <motion.button
                    className="flex flex-col items-center justify-center p-3 bg-purple-600/60 hover:bg-purple-600 rounded-lg text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTaskSelect('Set Reminder')}
                  >
                    <GrServices className="text-xl mb-1" />
                    <span className="text-sm">System Control</span>
                  </motion.button>

                  <motion.button
                    className="flex flex-col items-center justify-center p-3 bg-blue-600/60 hover:bg-blue-600 rounded-lg text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTaskSelect('Take Notes')}
                  >
                    <FaFileAlt className="text-xl mb-1" />
                    <span className="text-sm">Take Notes</span>
                  </motion.button>

                  <motion.button
                    className="flex flex-col items-center justify-center p-3 bg-cyan-600/60 hover:bg-cyan-600 rounded-lg text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTaskSelect('Web Search')}
                  >
                    <FaSearch className="text-xl mb-1" />
                    <span className="text-sm">Web Search</span>
                  </motion.button>
                </motion.div>
              )}

              <motion.div 
                className="flex items-center gap-2 bg-gray-700/80 rounded-full p-2 mt-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <button
                  className={`p-2 rounded-full transition-colors ${
                    isListening 
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                      : 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700'
                  }`}
                  onClick={handleVoiceInput}
                  aria-label="Voice Input"
                >
                  <CiMicrophoneOn className={`w-5 h-5 text-white ${isListening ? 'animate-pulse' : ''}`} />
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
                  className="p-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 transition-colors"
                  onClick={handleSend}
                  aria-label="Send Message"
                >
                  <FiSend className="w-5 h-5 text-white" />
                </button>
              </motion.div>

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

      {/* Tasks sidebar */}
      <AnimatePresence>
        {tasks.length > 0 && (
          <motion.div
            className="w-96 bg-stone-900/70 backdrop-blur-lg border-l border-gray-800 h-screen overflow-y-auto"
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            transition={{ type: 'spring', damping: 30, stiffness: 200 }}
          >
            <div className="p-4">
              <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
                <FaTasks className="mr-2" /> Tasks
              </h2>

              {pendingTasks.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm uppercase tracking-wider text-gray-400 mb-2 font-medium">
                    Pending
                  </h3>
                  <div className="space-y-2">
                    <AnimatePresence>
                      {pendingTasks.map((task) => (
                        <motion.div
                          key={task.id}
                          className="bg-gray-800/60 p-3 rounded-lg"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, x: -100 }}
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: 'spring', damping: 25 }}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <div className="flex items-start gap-2">
                              <button
                                onClick={() => toggleTaskCompletion(task.id)}
                                className="mt-1 text-gray-400 hover:text-green-400 transition-colors"
                              >
                                <FiCircle className="w-4 h-4" />
                              </button>
                              <div>
                                <h4 className="text-white font-medium">{task.title}</h4>
                                <div className="text-xs text-gray-400 flex items-center mt-1">
                                  <span>Created: {formatDate(task.createdAt)}</span>
                                </div>
                                {task.deadline && (
                                  <div className="text-xs text-amber-400 flex items-center mt-1">
                                    <FiClock className="mr-1" /> 
                                    <span>Due: {formatDate(task.deadline)}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                            <button
                              onClick={() => deleteTask(task.id)}
                              className="text-gray-500 hover:text-red-400 transition-colors"
                            >
                              <FiTrash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              )}

              {completedTasks.length > 0 && (
                <div>
                  <h3 className="text-sm uppercase tracking-wider text-gray-400 mb-2 font-medium">
                    Completed
                  </h3>
                  <div className="space-y-2">
                    <AnimatePresence>
                      {completedTasks.map((task) => (
                        <motion.div
                          key={task.id}
                          className="bg-gray-800/30 p-3 rounded-lg"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 0.8, y: 0 }}
                          exit={{ opacity: 0, x: -100 }}
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: 'spring', damping: 25 }}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex items-start gap-2">
                              <button 
                                onClick={() => toggleTaskCompletion(task.id)}
                                className="mt-1 text-green-500 hover:text-green-400 transition-colors"
                              >
                                <FiCheckCircle className="w-4 h-4" />
                              </button>
                              <div>
                                <h4 className="text-gray-400 font-medium line-through">
                                  {task.title}
                                </h4>
                                <div className="text-xs text-gray-500 flex items-center mt-1">
                                  <span>Completed</span>
                                </div>
                              </div>
                            </div>
                            <button 
                              onClick={() => deleteTask(task.id)}
                              className="text-gray-500 hover:text-red-400 transition-colors"
                            >
                              <FiTrash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Home
