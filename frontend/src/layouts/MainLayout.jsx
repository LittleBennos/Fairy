import { Outlet, Link, useLocation } from 'react-router-dom'

export default function MainLayout() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <nav className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-purple-600">Fairy Studio</h1>
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
