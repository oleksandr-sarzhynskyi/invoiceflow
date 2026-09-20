import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { getDashboardSummary } from '../api/client'

function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadSummary() {
      try {
        const data = await getDashboardSummary()
        setSummary(data)
      } catch (err) {
        setError('Failed to load dashboard')
      }
    }
    loadSummary()
  }, [])

  return (
    <Layout>
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      {error && <p className="error-text">{error}</p>}
      {!summary && !error && <p>Loading…</p>}

      {summary && (
        <div className="stat-grid">
          <div className="stat">
            <div className="stat-value mono">{summary.total}</div>
            <div className="stat-label">Total invoices</div>
          </div>
          <div className="stat">
            <div className="stat-value mono">{summary.processing}</div>
            <div className="stat-label">Processing</div>
          </div>
          <div className="stat">
            <div className="stat-value mono">{summary.review_required ?? summary.pending_review}</div>
            <div className="stat-label">Needs review</div>
          </div>
          <div className="stat">
            <div className="stat-value mono">{summary.approved}</div>
            <div className="stat-label">Approved</div>
          </div>
        </div>
      )}

      <Link to="/invoices" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
        View all invoices
      </Link>
    </Layout>
  )
}

export default Dashboard