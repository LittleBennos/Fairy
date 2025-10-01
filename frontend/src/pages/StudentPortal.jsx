import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function StudentPortal() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Student Portal - Fairy Dance Studio</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* My Classes */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">My Classes</h2>
                <div className="space-y-3">
                  <div className="border-l-4 border-purple-500 pl-4 py-2">
                    <p className="text-sm font-medium text-gray-900">Ballet - Beginner</p>
                    <p className="text-sm text-gray-600">Tuesdays 4:00 PM - 5:00 PM</p>
                  </div>
                  <div className="border-l-4 border-pink-500 pl-4 py-2">
                    <p className="text-sm font-medium text-gray-900">Jazz - Intermediate</p>
                    <p className="text-sm text-gray-600">Thursdays 5:30 PM - 6:30 PM</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Attendance */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">My Attendance</h2>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">This Month:</span>
                    <span className="text-sm font-medium">8 / 10 classes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Attendance Rate:</span>
                    <span className="text-sm font-medium text-green-600">80%</span>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '80%' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Upcoming Events</h2>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="text-xs text-white bg-purple-500 rounded px-2 py-1">DEC 15</div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">Winter Recital</p>
                      <p className="text-xs text-gray-600">Main Theater, 6:00 PM</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="text-xs text-white bg-pink-500 rounded px-2 py-1">DEC 20</div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">Holiday Party</p>
                      <p className="text-xs text-gray-600">Studio A, 4:00 PM</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Account Balance */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Account Balance</h2>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Current Balance:</span>
                    <span className="text-sm font-medium text-green-600">$0.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Next Payment Due:</span>
                    <span className="text-sm font-medium">Dec 1, 2024</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}