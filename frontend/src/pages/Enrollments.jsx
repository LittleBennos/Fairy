import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/cookieClient'

export default function Enrollments() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['enrollments'],
    queryFn: () => apiClient.get('/enrollments/').then(res => res.data),
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
        Error loading enrollments: {error.message}
      </div>
    )
  }

  const getStatusBadge = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      trial: 'bg-blue-100 text-blue-800',
      applied: 'bg-yellow-100 text-yellow-800',
      waitlist: 'bg-orange-100 text-orange-800',
      withdrawn: 'bg-gray-100 text-gray-800',
      completed: 'bg-purple-100 text-purple-800',
    }
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[status] || colors.applied}`}>
        {status}
      </span>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Enrollments</h1>
          <p className="text-gray-600 mt-1">Manage student class enrollments</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
          + New Enrollment
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {data?.results?.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No enrollments</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new enrollment.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Class
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Enrollment Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.results?.map((enrollment) => (
                <tr key={enrollment.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{enrollment.account_code}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {enrollment.class_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(enrollment.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {enrollment.enrollment_date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-purple-600 hover:text-purple-900 mr-3">Edit</button>
                    <button className="text-gray-600 hover:text-gray-900">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
