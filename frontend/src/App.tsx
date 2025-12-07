import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Archive from './pages/Archive'
import Chapter from './pages/Chapter'
import About from './pages/About'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="archive" element={<Archive />} />
        <Route path="chapter/:date" element={<Chapter />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  )
}

export default App
