import { motion, AnimatePresence } from 'framer-motion'
import { FiTrash2, FiCheckCircle } from 'react-icons/fi'
import { FaTasks, FaHistory } from 'react-icons/fa'

const Sidebar = ({ completedTasks = [], setCompletedTasks }) => {
  const toggleTaskCompletion = (taskId) => {
    const updatedTasks = completedTasks.filter((task) => task.id !== taskId)
    setCompletedTasks(updatedTasks)
  }

  const deleteTask = (taskId) => {
    const updatedTasks = completedTasks.filter((task) => task.id !== taskId)
    setCompletedTasks(updatedTasks)
  }

  return (
    <motion.div
      className="w-96 bg-stone-900/70 backdrop-blur-lg border-l border-gray-800 h-screen overflow-y-auto"
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      transition={{ type: 'spring', damping: 30, stiffness: 200 }}
    >
      <div className="p-4">
        <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
          <FaHistory className="mr-2" /> Task History
        </h2>

        {completedTasks.length > 0 ? (
          <div>
            <h3 className="text-sm uppercase tracking-wider text-gray-400 mb-2 font-medium">
              Completed Tasks
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
                            <span>Completed on: {task.completedAt || 'N/A'}</span>
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
        ) : (
          <div className="flex flex-col items-center justify-center h-40 text-gray-500">
            <FaTasks className="text-4xl mb-3 opacity-50" />
            <p>No completed tasks yet</p>
            <p className="text-sm mt-1">Completed tasks will appear here</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default Sidebar
