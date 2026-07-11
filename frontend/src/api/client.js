import axios from 'axios'

// In dev, Vite proxies /api -> http://127.0.0.1:8000 (see vite.config.js).
// In production, set VITE_API_BASE_URL to your deployed backend URL.
const baseURL = import.meta.env.VITE_API_BASE_URL || ''

const client = axios.create({ baseURL })

export const api = {
  // Dashboard
  stats: () => client.get('/api/dashboard/stats').then((r) => r.data),
  utilizationByBuilding: () =>
    client.get('/api/dashboard/utilization-by-building').then((r) => r.data),
  employeesByDepartment: () =>
    client.get('/api/dashboard/employees-by-department').then((r) => r.data),
  seatStatusBreakdown: () =>
    client.get('/api/dashboard/seat-status-breakdown').then((r) => r.data),

  // Employees
  employees: (params) => client.get('/api/employees', { params }).then((r) => r.data),
  employee: (id) => client.get(`/api/employees/${id}`).then((r) => r.data),
  createEmployee: (body) => client.post('/api/employees', body).then((r) => r.data),
  updateEmployee: (id, body) => client.put(`/api/employees/${id}`, body).then((r) => r.data),
  deleteEmployee: (id) => client.delete(`/api/employees/${id}`).then((r) => r.data),

  // Projects
  projects: (params) => client.get('/api/projects', { params }).then((r) => r.data),
  createProject: (body) => client.post('/api/projects', body).then((r) => r.data),

  // Seats
  seats: (params) => client.get('/api/seats', { params }).then((r) => r.data),
  availableSeats: (params) =>
    client.get('/api/seats/available', { params }).then((r) => r.data),
  seatLocations: () => client.get('/api/seats/locations').then((r) => r.data),

  // Allocations
  allocate: (body) => client.post('/api/allocations/allocate', body).then((r) => r.data),
  release: (body) => client.post('/api/allocations/release', body).then((r) => r.data),
  allocateNewJoiners: () =>
    client.post('/api/allocations/allocate-new-joiners').then((r) => r.data),

  // Assistant
  ask: (question) =>
    client.post('/api/assistant/query', { question }).then((r) => r.data),
  assistantExamples: () => client.get('/api/assistant/examples').then((r) => r.data),
}

export default client
