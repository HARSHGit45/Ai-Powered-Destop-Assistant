import Home from './components/Home'
import Sidebar from './components/Sidebar'
import { useState } from 'react'

const App = () => {
  const [completedTasks, setCompletedTasks] = useState([]) // Ensure state is initialized

  return (
    <div className="absolute inset-0 -z-10 h-full w-full items-center px-5 [background:radial-gradient(125%_125%_at_50%_10%,#000_40%,#63e_100%)] font-winky">
      <Home />
      <Sidebar completedTasks={completedTasks} setCompletedTasks={setCompletedTasks} />
    </div>
  )
}

export default App
