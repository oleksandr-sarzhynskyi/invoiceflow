const BASE_URL = 'http://localhost:8000'

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token')
  const isFormData = options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return response.json()
}

export async function login(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function signup(email, password) {
  return apiFetch('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function getDashboardSummary() {
  return apiFetch('/dashboard/summary', {
    method: 'GET',
  })
}

export async function listInvoices(status) {
  const query = status ? `?status=${status}` : ''
  return apiFetch(`/invoices/${query}`, {
    method: 'GET',
  })
}

export async function getInvoice(id) {
  return apiFetch(`/invoices/${id}`, {
    method: 'GET',
  })
}

export async function updateInvoice(id, updates) {
  return apiFetch(`/invoices/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
}

export async function approveInvoice(id) {
  return apiFetch(`/invoices/${id}/approve`, {
    method: 'POST',
  })
}

export async function uploadInvoice(file) {
  const formData = new FormData()
  formData.append('file', file)

  return apiFetch('/invoices/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function getInvoiceFileUrl(id) {
  const token = localStorage.getItem('token')

  const response = await fetch(`${BASE_URL}/invoices/${id}/file`, {
    headers: token ? { 'Authorization': `Bearer ${token}` } : {},
  })

  if (!response.ok) {
    throw new Error('Failed to load PDF')
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

export async function getSupplierStats() {
  return apiFetch('/suppliers')
}

export async function deleteInvoice(id) {
  return apiFetch(`/invoices/${id}`, {
    method: 'DELETE',
  })
}