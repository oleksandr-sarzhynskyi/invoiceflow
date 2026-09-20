import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { getInvoice, updateInvoice, approveInvoice, getInvoiceFileUrl } from '../api/client'

function InvoiceDetail() {
  const { id } = useParams()

  const [invoice, setInvoice] = useState(null)
  const [form, setForm] = useState({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadInvoice()
  }, [id])

  async function loadInvoice() {
    try {
      const data = await getInvoice(id)
      setInvoice(data)
      setForm({
        invoice_date: data.invoice_date || '',
        due_date: data.due_date || '',
        net_amount: data.net_amount ?? '',
        vat_amount: data.vat_amount ?? '',
        gross_amount: data.gross_amount ?? '',
      })
    } catch (err) {
      setError('Failed to load invoice')
    }
  }

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setError('')

    try {
      const updates = {
        invoice_date: form.invoice_date || null,
        due_date: form.due_date || null,
        net_amount: form.net_amount === '' ? null : Number(form.net_amount),
        vat_amount: form.vat_amount === '' ? null : Number(form.vat_amount),
        gross_amount: form.gross_amount === '' ? null : Number(form.gross_amount),
      }
      const updated = await updateInvoice(id, updates)
      setInvoice(updated)
    } catch (err) {
      setError('Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  async function handleApprove() {
    setError('')
    try {
      const updated = await approveInvoice(id)
      setInvoice(updated)
    } catch (err) {
      setError('Failed to approve invoice')
    }
  }

  async function handleViewPdf() {
    setError('')
    try {
      const url = await getInvoiceFileUrl(id)
      window.open(url, '_blank')
    } catch (err) {
      setError('Failed to load PDF')
    }
  }

  if (error && !invoice) {
    return (
      <Layout>
        <p className="error-text">{error}</p>
      </Layout>
    )
  }

  if (!invoice) {
    return (
      <Layout>
        <p>Loading…</p>
      </Layout>
    )
  }

  return (
    <Layout>
      <Link to="/invoices" className="back-link">← Back to invoices</Link>

      <div className="page-header">
        <h1>{invoice.original_filename}</h1>
        <StatusBadge status={invoice.status} />
      </div>

      <div className="detail-meta">
        {invoice.confidence_score != null && <span>Confidence: {(invoice.confidence_score * 100).toFixed(0)}%</span>}
        <button type="button" className="btn btn-secondary" onClick={handleViewPdf}>
          View PDF
        </button>
      </div>

      {invoice.review_reason && (
        <p className="error-text" style={{ marginBottom: 24 }}>{invoice.review_reason}</p>
      )}

      <form onSubmit={handleSave}>
        <div className="form-grid">
          <div className="field">
            <label>Invoice date</label>
            <input type="date" value={form.invoice_date || ''} onChange={(e) => handleChange('invoice_date', e.target.value)} />
          </div>
          <div className="field">
            <label>Due date</label>
            <input type="date" value={form.due_date || ''} onChange={(e) => handleChange('due_date', e.target.value)} />
          </div>
          <div className="field">
            <label>Net amount</label>
            <input className="mono" type="number" step="0.01" value={form.net_amount} onChange={(e) => handleChange('net_amount', e.target.value)} />
          </div>
          <div className="field">
            <label>VAT amount</label>
            <input className="mono" type="number" step="0.01" value={form.vat_amount} onChange={(e) => handleChange('vat_amount', e.target.value)} />
          </div>
          <div className="field">
            <label>Gross amount</label>
            <input className="mono" type="number" step="0.01" value={form.gross_amount} onChange={(e) => handleChange('gross_amount', e.target.value)} />
          </div>
        </div>

        {error && <p className="error-text">{error}</p>}

        <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
          <button type="submit" className="btn" disabled={saving}>
            {saving ? 'Saving…' : 'Save changes'}
          </button>
          <button
            type="button"
            className="btn btn-flag"
            onClick={handleApprove}
            disabled={invoice.status === 'approved' || invoice.status === 'processing'}
          >
            Approve
          </button>
        </div>
      </form>
    </Layout>
  )
}

export default InvoiceDetail