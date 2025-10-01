import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import apiClient from '../api/cookieClient'

export default function Dashboard() {
  const navigate = useNavigate()

  // Fetch dashboard stats
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const [students, classes, invoices, enrollments] = await Promise.all([
        apiClient.get('/students/').then(res => res.data),
        apiClient.get('/classes/').then(res => res.data),
        apiClient.get('/invoices/').then(res => res.data),
        apiClient.get('/enrollments/').then(res => res.data),
      ])
      return { students, classes, invoices, enrollments }
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Error loading dashboard: {error.message}
      </div>
    )
  }

  const activeStudents = stats?.students?.results?.filter(s => s.status === 'active').length || 0
  const activeEnrollments = stats?.enrollments?.results?.filter(e => e.status === 'active').length || 0
  const overdueInvoices = stats?.invoices?.results?.filter(i => i.status === 'overdue').length || 0

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to Fairy Dance Studio Management System</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link to="/students" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {stats?.students?.count || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">{activeStudents} active</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </Link>

        <Link to="/classes" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Classes</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats?.classes?.count || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">This term</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
          </div>
        </Link>

        <Link to="/enrollments" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Enrollments</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {stats?.enrollments?.count || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">{activeEnrollments} active</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </Link>

        <Link to="/invoices" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Invoices</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {stats?.invoices?.count || 0}
              </p>
              <p className="text-xs text-red-500 mt-1">{overdueInvoices} overdue</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-full">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
              </svg>
            </div>
          </div>
        </Link>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/students', { state: { addNew: true } })}
            className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            + Add New Student
          </button>
          <button
            onClick={() => navigate('/enrollments', { state: { addNew: true } })}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            + Create Enrollment
          </button>
          <button
            onClick={() => navigate('/invoices', { state: { addNew: true } })}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
          >
            + Generate Invoice
          </button>
        </div>
      </div>
    </div>
  )
}
