import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Students from './pages/Students'
import Guardians from './pages/Guardians'
import Classes from './pages/Classes'
import Enrollments from './pages/Enrollments'
import Attendance from './pages/Attendance'
import Invoices from './pages/Invoices'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="students" element={<Students />} />
        <Route path="guardians" element={<Guardians />} />
        <Route path="classes" element={<Classes />} />
        <Route path="enrollments" element={<Enrollments />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="invoices" element={<Invoices />} />
      </Route>
    </Routes>
  )
}

export default App
