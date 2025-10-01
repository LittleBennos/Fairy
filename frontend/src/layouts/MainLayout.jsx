import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function MainLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const isActive = (path) => location.pathname === path

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <nav className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-purple-600">Fairy Studio</h1>
          <p className="text-sm text-gray-600 mt-1">Admin Dashboard</p>
        </div>
        <ul className="py-4">
          <li>
            <Link
              to="/"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link
              to="/students"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/students')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Students
            </Link>
          </li>
          <li>
            <Link
              to="/guardians"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/guardians')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Guardians
            </Link>
          </li>
          <li>
            <Link
              to="/classes"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/classes')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Classes
            </Link>
          </li>
          <li>
            <Link
              to="/enrollments"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/enrollments')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Enrollments
            </Link>
          </li>
          <li>
            <Link
              to="/attendance"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/attendance')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Attendance
            </Link>
          </li>
          <li>
            <Link
              to="/invoices"
              className={`block px-6 py-3 text-sm font-medium transition-colors ${
                isActive('/invoices')
                  ? 'bg-purple-50 text-purple-600 border-r-4 border-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Invoices
            </Link>
          </li>
        </ul>

        {/* User info and logout */}
        <div className="absolute bottom-0 w-64 p-6 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.username}</p>
              <p className="text-xs text-gray-600">{user?.role || 'Admin'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
