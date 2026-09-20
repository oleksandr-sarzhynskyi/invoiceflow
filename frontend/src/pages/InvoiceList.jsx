import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { listInvoices, uploadInvoice, deleteInvoice } from '../api/client'

function InvoiceList() {
  const [invoices, setInvoices] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadInvoices()
  }, [statusFilter])

  async function loadInvoices() {
    try {
      const data = await listInvoices(statusFilter || undefined)
      setInvoices(data)
    } catch (err) {
      setError('Failed to load invoices')
    }
  }

  async function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setError('')

    try {
      await uploadInvoice(file)
      await loadInvoices()
    } catch (err) {
      setError('Upload failed')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  async function handleDelete(id, name) {
    if (!window.confirm(`Delete "${name}"? This can't be undone.`)) return

    try {
      await deleteInvoice(id)
      await loadInvoices()
    } catch (err) {
      setError('Failed to delete invoice')
    }
  }

  return (
    <Layout>
      <div className="page-header">
        <h1>Invoices</h1>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: '7px 10px', border: '1px solid var(--rule-strong)', borderRadius: 3, background: 'var(--paper-raised)', fontFamily: 'var(--font-body)' }}
        >
          <option value="">All statuses</option>
          <option value="processing">Processing</option>
          <option value="ready_for_approval">Ready for approval</option>
          <option value="review_required">Needs review</option>
          <option value="approved">Approved</option>
        </select>
      </div>

      <div className="upload-tray">
        <span className="upload-tray-label">Drop an invoice in the tray, or choose a file to begin processing.</span>
        <label className="btn" style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}>
          {uploading ? 'Uploading…' : 'Upload invoice'}
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      {error && <p className="error-text">{error}</p>}

      {invoices.length === 0 && !error ? (
        <p style={{ color: 'var(--ink-soft)' }}>No invoices yet — upload one to get started.</p>
      ) : (
        <table className="ledger-table">
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Gross</th>
              <th>Uploaded</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id}>
                <td><Link to={`/invoices/${invoice.id}`}>{invoice.original_filename}</Link></td>
                <td><StatusBadge status={invoice.status} /></td>
                <td className="num">{invoice.gross_amount != null ? `$${Number(invoice.gross_amount).toFixed(2)}` : '—'}</td>
                <td style={{ color: 'var(--ink-soft)', fontSize: '0.875rem' }}>
                  {new Date(invoice.created_at).toLocaleDateString()}
                </td>
                <td style={{ textAlign: 'right' }}>
                  <button
                    type="button"
                    onClick={() => handleDelete(invoice.id, invoice.original_filename)}
                    style={{ background: 'none', border: 'none', color: 'var(--ink-soft)', cursor: 'pointer', fontSize: '0.85rem' }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Layout>
  )
}

export default InvoiceList