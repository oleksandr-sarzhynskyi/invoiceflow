import { NavLink, useNavigate } from 'react-router-dom'

function Layout({ children }) {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">InvoiceFlow</div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            Dashboard
          </NavLink>
          <NavLink to="/invoices" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            Invoices
          </NavLink>
          <NavLink to="/suppliers" className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            Suppliers
          </NavLink>
        </nav>
        <button className="sidebar-logout" onClick={handleLogout}>Log out</button>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}

export default Layout