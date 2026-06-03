import { useState } from 'react'
import Dashboard from './components/Dashboard'
import ContactForm from './components/ContactForm'

const TABS = [
  { id: 'dashboard', label: 'CRM Dashboard' },
  { id: 'enquiry',   label: 'Enquiry Form'  },
]

export default function App() {
  const [tab, setTab] = useState('dashboard')

  return (
    <>
      <nav className="app-nav">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`nav-tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      {tab === 'dashboard' ? <Dashboard /> : <ContactForm />}
    </>
  )
}
