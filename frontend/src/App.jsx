import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './layouts/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Students from './pages/Students'
import Guardians from './pages/Guardians'
import Classes from './pages/Classes'
import Enrollments from './pages/Enrollments'
import Attendance from './pages/Attendance'
import Invoices from './pages/Invoices'
import StudentPortal from './pages/StudentPortal'
import ParentPortal from './pages/ParentPortal'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Student portal */}
        <Route path="/student-portal" element={
          <ProtectedRoute allowedRoles={['student']}>
            <StudentPortal />
          </ProtectedRoute>
        } />

        {/* Parent portal */}
        <Route path="/parent-portal" element={
          <ProtectedRoute allowedRoles={['guardian', 'parent']}>
            <ParentPortal />
          </ProtectedRoute>
        } />

        {/* Admin/Staff routes */}
        <Route path="/" element={
          <ProtectedRoute allowedRoles={['admin', 'staff']}>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="students" element={<Students />} />
          <Route path="guardians" element={<Guardians />} />
          <Route path="classes" element={<Classes />} />
          <Route path="enrollments" element={<Enrollments />} />
          <Route path="attendance" element={<Attendance />} />
          <Route path="invoices" element={<Invoices />} />
          <Route index element={<Navigate to="/dashboard" replace />} />
        </Route>

        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
