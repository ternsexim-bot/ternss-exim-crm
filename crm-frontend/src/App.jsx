import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import ContactForm from './components/ContactForm'

export default function App() {
  return (
    <BrowserRouter>
      <nav className="app-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-tab${isActive ? ' active' : ''}`}
        >
          CRM Dashboard
        </NavLink>
        <NavLink
          to="/contact"
          className={({ isActive }) => `nav-tab${isActive ? ' active' : ''}`}
        >
          Enquiry Form
        </NavLink>
      </nav>
      <Routes>
        <Route path="/"        element={<Dashboard />} />
        <Route path="/contact" element={<ContactForm />} />
      </Routes>
    </BrowserRouter>
  )
}
