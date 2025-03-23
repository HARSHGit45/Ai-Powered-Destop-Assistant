import Home from './components/Home'
import Stocks from './components/Stocks'
import Weather from './components/Weather'

const App = () => {

  return (
    <div className="relative min-h-screen w-full flex flex-col [background:radial-gradient(125%_125%_at_50%_10%,#000_40%,#63e_100%)] ">
      <Home />
      <Weather />
      <Stocks />
    </div>
  )
}

export default App
