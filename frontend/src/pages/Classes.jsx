import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/cookieClient'

export default function Classes() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['classes'],
    queryFn: () => apiClient.get('/classes/').then(res => res.data),
  })

  if (isLoading) return <div>Loading classes...</div>
  if (error) return <div>Error loading classes: {error.message}</div>

  return (
    <div>
      <h1>Classes</h1>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
        {data?.results?.length === 0 ? (
          <p>No classes found. Start by adding classes through the Django admin panel.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ecf0f1' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>Class Type</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Term</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Day</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Time</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Available Spots</th>
              </tr>
            </thead>
            <tbody>
              {data?.results?.map((classItem) => (
                <tr key={classItem.id} style={{ borderBottom: '1px solid #ecf0f1' }}>
                  <td style={{ padding: '12px' }}>{classItem.class_type_name}</td>
                  <td style={{ padding: '12px' }}>{classItem.term_name}</td>
                  <td style={{ padding: '12px' }}>{classItem.day_of_week_display}</td>
                  <td style={{ padding: '12px' }}>{classItem.start_time}</td>
                  <td style={{ padding: '12px' }}>{classItem.available_spots}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
