import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { getSupplierStats } from '../api/client'

function Suppliers() {
  const [suppliers, setSuppliers] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const data = await getSupplierStats()
        setSuppliers(data)
      } catch (err) {
        setError('Failed to load suppliers')
      }
    }
    load()
  }, [])

  return (
    <Layout>
      <div className="page-header">
        <h1>Suppliers</h1>
      </div>

      {error && <p className="error-text">{error}</p>}

      {suppliers.length === 0 && !error ? (
        <p style={{ color: 'var(--ink-soft)' }}>No suppliers yet — they'll appear once invoices are processed.</p>
      ) : (
        <table className="ledger-table">
          <thead>
            <tr>
              <th>Supplier</th>
              <th style={{ textAlign: 'right' }}>Invoices</th>
              <th style={{ textAlign: 'right' }}>Total spend</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td className="num">{s.invoice_count}</td>
                <td className="num">{s.total_spend != null ? `$${s.total_spend.toFixed(2)}` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Layout>
  )
}

export default Suppliers