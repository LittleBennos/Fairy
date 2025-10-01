import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/cookieClient'

export default function Invoices() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => apiClient.get('/invoices/').then(res => res.data),
  })

  if (isLoading) return <div>Loading invoices...</div>
  if (error) return <div>Error loading invoices: {error.message}</div>

  return (
    <div>
      <h1>Invoices</h1>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
        {data?.results?.length === 0 ? (
          <p>No invoices found. Invoices will appear here once created.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ecf0f1' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>Invoice #</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Student</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Issue Date</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Due Date</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Total</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Outstanding</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {data?.results?.map((invoice) => (
                <tr key={invoice.id} style={{ borderBottom: '1px solid #ecf0f1' }}>
                  <td style={{ padding: '12px' }}>{invoice.invoice_number}</td>
                  <td style={{ padding: '12px' }}>{invoice.student_name}</td>
                  <td style={{ padding: '12px' }}>{invoice.issue_date}</td>
                  <td style={{ padding: '12px' }}>{invoice.due_date}</td>
                  <td style={{ padding: '12px' }}>${invoice.total}</td>
                  <td style={{ padding: '12px' }}>${invoice.amount_outstanding}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: invoice.status === 'paid' ? '#2ecc71' : '#e74c3c',
                      color: 'white',
                      fontSize: '12px'
                    }}>
                      {invoice.status}
                    </span>
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
