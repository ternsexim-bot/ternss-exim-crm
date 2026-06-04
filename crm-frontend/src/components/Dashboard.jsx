import { useState, useEffect, useCallback } from 'react'
import { getLeads, getStats, updateLead, deleteLead, createLead } from '../api/leads'
import LeadStats from './LeadStats'
import LeadsTable from './LeadsTable'
import AddLeadModal from './AddLeadModal'

const STATUSES = ['New', 'Contacted', 'Negotiation', 'Won', 'Lost']

const EMPTY_STATS = { total: 0, new: 0, contacted: 0, negotiation: 0, won: 0, lost: 0 }

export default function Dashboard() {
  const [leads, setLeads]           = useState([])
  const [stats, setStats]           = useState(EMPTY_STATS)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)
  const [statusFilter, setFilter]   = useState('')
  const [showModal, setShowModal]   = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [leadsData, statsData] = await Promise.all([
        getLeads(statusFilter),
        getStats(),
      ])
      setLeads(leadsData)
      setStats(statsData)
    } catch {
      setError('Cannot reach CRM API. Check that terns-exim-api.onrender.com is running.')
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  const refreshStats = async () => {
    const statsData = await getStats()
    setStats(statsData)
  }

  const handleStatusChange = async (id, status) => {
    try {
      const updated = await updateLead(id, { status })
      setLeads(prev => prev.map(l => (l.id === id ? updated : l)))
      await refreshStats()
    } catch {
      setError('Failed to update lead status.')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lead? This cannot be undone.')) return
    try {
      await deleteLead(id)
      setLeads(prev => prev.filter(l => l.id !== id))
      await refreshStats()
    } catch {
      setError('Failed to delete lead.')
    }
  }

  const handleAdd = async (data) => {
    try {
      const lead = await createLead(data)
      if (!statusFilter || statusFilter === lead.status) {
        setLeads(prev => [lead, ...prev])
      }
      await refreshStats()
      setShowModal(false)
    } catch {
      setError('Failed to create lead.')
    }
  }

  return (
    <div className="dashboard">
      <div className="topbar">
        <div className="topbar-brand">
          TERNS EXIM <span>CRM</span>
        </div>
        <div className="topbar-meta">Lead Management Dashboard</div>
      </div>

      <div className="main-content">
        {error && <div className="error-bar">{error}</div>}

        <LeadStats stats={stats} />

        <div className="table-section">
          <div className="table-header">
            <div className="table-title">
              All Leads ({leads.length})
            </div>
            <div className="filter-bar">
              <select value={statusFilter} onChange={e => setFilter(e.target.value)}>
                <option value="">All Status</option>
                {STATUSES.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              <button className="btn-refresh" onClick={load}>
                ↻ Refresh
              </button>
              <button className="btn-primary" onClick={() => setShowModal(true)}>
                + Add Lead
              </button>
            </div>
          </div>

          <LeadsTable
            leads={leads}
            loading={loading}
            onStatusChange={handleStatusChange}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {showModal && (
        <AddLeadModal onClose={() => setShowModal(false)} onAdd={handleAdd} />
      )}
    </div>
  )
}
