import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function ParentPortal() {
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
              <h1 className="text-xl font-semibold">Parent Portal - Fairy Dance Studio</h1>
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
          {/* Children Section */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">My Children</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Emma Smith</h3>
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Active</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Current Classes:</span>
                      <span className="font-medium">2 classes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Attendance This Month:</span>
                      <span className="font-medium">85%</span>
                    </div>
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-gray-500">Next Class: Ballet - Tomorrow 4:00 PM</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Liam Smith</h3>
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Active</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Current Classes:</span>
                      <span className="font-medium">1 class</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Attendance This Month:</span>
                      <span className="font-medium">90%</span>
                    </div>
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-gray-500">Next Class: Hip Hop - Thursday 5:30 PM</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Schedule */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">This Week's Schedule</h3>
                <div className="space-y-2">
                  <div className="text-sm">
                    <p className="font-medium">Tuesday</p>
                    <p className="text-gray-600 text-xs">Emma - Ballet 4:00 PM</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Thursday</p>
                    <p className="text-gray-600 text-xs">Emma - Jazz 5:30 PM</p>
                    <p className="text-gray-600 text-xs">Liam - Hip Hop 5:30 PM</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Saturday</p>
                    <p className="text-gray-600 text-xs">Emma - Ballet 10:00 AM</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Billing */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Billing Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Account Balance:</span>
                    <span className="font-medium text-green-600">$0.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Next Payment:</span>
                    <span className="font-medium">Dec 1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Total:</span>
                    <span className="font-medium">$285.00</span>
                  </div>
                </div>
                <button className="mt-4 w-full bg-purple-600 text-white text-sm px-3 py-2 rounded hover:bg-purple-700">
                  View Invoices
                </button>
              </div>
            </div>

            {/* Communications */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Messages</h3>
                <div className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Winter Recital Info</p>
                    <p className="text-xs text-gray-600">2 days ago</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Schedule Change Notice</p>
                    <p className="text-xs text-gray-600">1 week ago</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Costume Measurements</p>
                    <p className="text-xs text-gray-600">2 weeks ago</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Upcoming Events */}
          <div className="mt-6 bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upcoming Events</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="border-l-4 border-purple-500 pl-4">
                  <p className="text-sm font-medium">Winter Recital</p>
                  <p className="text-xs text-gray-600">December 15, 6:00 PM</p>
                  <p className="text-xs text-gray-500 mt-1">All students performing</p>
                </div>
                <div className="border-l-4 border-pink-500 pl-4">
                  <p className="text-sm font-medium">Holiday Party</p>
                  <p className="text-xs text-gray-600">December 20, 4:00 PM</p>
                  <p className="text-xs text-gray-500 mt-1">Families welcome</p>
                </div>
                <div className="border-l-4 border-blue-500 pl-4">
                  <p className="text-sm font-medium">Spring Registration Opens</p>
                  <p className="text-xs text-gray-600">January 5, 2025</p>
                  <p className="text-xs text-gray-500 mt-1">Early bird discount available</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}