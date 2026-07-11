import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { EmptyState, Modal, Pagination, Spinner, StatusBadge } from '../components/ui.jsx'

const emptyForm = {
  employee_code: '',
  name: '',
  email: '',
  designation: '',
  department: '',
  team: '',
  status: 'new_joiner',
  project_id: '',
}

export default function Employees() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    q: '',
    department: '',
    status: '',
    has_seat: '',
  })
  const [page, setPage] = useState(1)
  const [locations, setLocations] = useState({ buildings: [] })
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [msg, setMsg] = useState(null)

  const pageSize = 20

  function load() {
    setLoading(true)
    const params = { page, page_size: pageSize }
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== '') params[k] = v
    })
    api.employees(params).then((d) => {
      setData(d)
      setLoading(false)
    })
  }

  useEffect(load, [page, filters])
  useEffect(() => {
    api.seatLocations().then(setLocations)
  }, [])

  function updateFilter(key, value) {
    setPage(1)
    setFilters((f) => ({ ...f, [key]: value }))
  }

  async function allocate(id) {
    try {
      await api.allocate({ employee_id: id })
      setMsg({ type: 'ok', text: 'Seat allocated.' })
      load()
    } catch (e) {
      setMsg({ type: 'err', text: e.response?.data?.detail || 'Allocation failed' })
    }
  }

  async function release(id) {
    try {
      await api.release({ employee_id: id })
      setMsg({ type: 'ok', text: 'Seat released.' })
      load()
    } catch (e) {
      setMsg({ type: 'err', text: e.response?.data?.detail || 'Release failed' })
    }
  }

  async function submitCreate(e) {
    e.preventDefault()
    try {
      const body = { ...form }
      if (body.project_id === '') delete body.project_id
      else body.project_id = Number(body.project_id)
      await api.createEmployee(body)
      setShowCreate(false)
      setForm(emptyForm)
      setMsg({ type: 'ok', text: 'Employee created.' })
      load()
    } catch (err) {
      setMsg({ type: 'err', text: err.response?.data?.detail || 'Create failed' })
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Employees</h1>
          <p className="text-slate-500">Search, filter, and manage seat allocation</p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          + Add Employee
        </button>
      </div>

      {msg && (
        <div
          className={`mb-4 px-4 py-2 rounded-lg text-sm ${
            msg.type === 'ok' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}
        >
          {msg.text}
        </div>
      )}

      <div className="card mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            className="input"
            placeholder="Search name, code, email…"
            value={filters.q}
            onChange={(e) => updateFilter('q', e.target.value)}
          />
          <select
            className="input"
            value={filters.department}
            onChange={(e) => updateFilter('department', e.target.value)}
          >
            <option value="">All departments</option>
            {['Engineering', 'Data', 'Design', 'Product', 'Quality Assurance', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations', 'IT', 'Legal'].map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
          <select
            className="input"
            value={filters.status}
            onChange={(e) => updateFilter('status', e.target.value)}
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="new_joiner">New joiner</option>
            <option value="inactive">Inactive</option>
          </select>
          <select
            className="input"
            value={filters.has_seat}
            onChange={(e) => updateFilter('has_seat', e.target.value)}
          >
            <option value="">Seat: any</option>
            <option value="true">Has seat</option>
            <option value="false">No seat</option>
          </select>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <Spinner />
        ) : data.items.length === 0 ? (
          <EmptyState message="No employees match your filters." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Code</th>
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Department</th>
                  <th className="py-2 pr-4">Project</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Seat</th>
                  <th className="py-2 pr-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((e) => (
                  <tr key={e.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 pr-4 font-mono text-xs">{e.employee_code}</td>
                    <td className="py-2 pr-4">
                      <div className="font-medium">{e.name}</div>
                      <div className="text-xs text-slate-400">{e.email}</div>
                    </td>
                    <td className="py-2 pr-4">
                      {e.department}
                      <div className="text-xs text-slate-400">{e.team}</div>
                    </td>
                    <td className="py-2 pr-4">{e.project?.name || '—'}</td>
                    <td className="py-2 pr-4">
                      <StatusBadge value={e.status} />
                    </td>
                    <td className="py-2 pr-4">
                      {e.seat ? (
                        <span className="font-mono text-xs">
                          {e.seat.seat_number}
                          <div className="text-slate-400">
                            {e.seat.building} · Fl {e.seat.floor}
                          </div>
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-2 pr-4">
                      {e.seat ? (
                        <button className="btn-danger" onClick={() => release(e.id)}>
                          Release
                        </button>
                      ) : (
                        <button className="btn-ghost" onClick={() => allocate(e.id)}>
                          Allocate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination
              page={data.page}
              pageSize={data.page_size}
              total={data.total}
              onChange={setPage}
            />
          </div>
        )}
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Employee">
        <form onSubmit={submitCreate} className="space-y-3">
          {[
            ['employee_code', 'Employee code (e.g. EMP09001)'],
            ['name', 'Full name'],
            ['email', 'Email'],
            ['designation', 'Designation'],
            ['team', 'Team'],
          ].map(([key, label]) => (
            <input
              key={key}
              className="input"
              placeholder={label}
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              required={['employee_code', 'name', 'email'].includes(key)}
            />
          ))}
          <select
            className="input"
            value={form.department}
            onChange={(e) => setForm({ ...form, department: e.target.value })}
          >
            <option value="">Select department</option>
            {['Engineering', 'Data', 'Design', 'Product', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations', 'IT', 'Legal'].map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
          <select
            className="input"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          >
            <option value="new_joiner">New joiner</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
