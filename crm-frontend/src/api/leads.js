import axios from 'axios'

const api = axios.create({ baseURL: 'https://ternsexim.com/api' })

export const getLeads = (status) =>
  api.get('/leads', { params: status ? { status } : {} }).then(r => r.data)

export const createLead = (data) =>
  api.post('/leads', data).then(r => r.data)

export const updateLead = (id, data) =>
  api.put(`/leads/${id}`, data).then(r => r.data)

export const deleteLead = (id) =>
  api.delete(`/leads/${id}`).then(r => r.data)

export const getStats = () =>
  api.get('/leads/stats').then(r => r.data)
