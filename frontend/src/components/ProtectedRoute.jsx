import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function ProtectedRoute({ children, allowedRoles = [] }) {
  const { isAuthenticated, user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // If no specific roles required, allow any authenticated user
  if (allowedRoles.length === 0) {
    return children
  }

  // Check if user has one of the allowed roles
  const userRole = user?.role || user?.user_type
  if (allowedRoles.includes(userRole)) {
    return children
  }

  // Redirect based on user role if not authorized
  if (userRole === 'student') {
    return <Navigate to="/student-portal" replace />
  } else if (userRole === 'guardian' || userRole === 'parent') {
    return <Navigate to="/parent-portal" replace />
  }

  return <Navigate to="/unauthorized" replace />
}