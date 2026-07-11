import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Employees from './pages/Employees.jsx'
import Projects from './pages/Projects.jsx'
import Seats from './pages/Seats.jsx'
import NewJoiners from './pages/NewJoiners.jsx'
import Assistant from './pages/Assistant.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="employees" element={<Employees />} />
        <Route path="projects" element={<Projects />} />
        <Route path="seats" element={<Seats />} />
        <Route path="new-joiners" element={<NewJoiners />} />
        <Route path="assistant" element={<Assistant />} />
      </Route>
    </Routes>
  )
}
