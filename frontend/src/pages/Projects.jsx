import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { EmptyState, Modal, Spinner, StatusBadge } from '../components/ui.jsx'

const emptyForm = { code: '', name: '', department: '', manager: '', status: 'active' }

export default function Projects() {
  const [projects, setProjects] = useState(null)
  const [q, setQ] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [msg, setMsg] = useState(null)

  function load() {
    const params = {}
    if (q) params.q = q
    if (statusFilter) params.status = statusFilter
    api.projects(params).then(setProjects)
  }

  useEffect(load, [q, statusFilter])

  async function submitCreate(e) {
    e.preventDefault()
    try {
      await api.createProject(form)
      setShowCreate(false)
      setForm(emptyForm)
      setMsg({ type: 'ok', text: 'Project created.' })
      load()
    } catch (err) {
      setMsg({ type: 'err', text: err.response?.data?.detail || 'Create failed' })
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-slate-500">Project mapping and team sizes</p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          + Add Project
        </button>
      </div>

      {msg && (
        <div className={`mb-4 px-4 py-2 rounded-lg text-sm ${msg.type === 'ok' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
          {msg.text}
        </div>
      )}

      <div className="card mb-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="input" placeholder="Search name or code…" value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="on_hold">On hold</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {!projects ? (
        <Spinner />
      ) : projects.length === 0 ? (
        <EmptyState message="No projects found." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div key={p.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold">{p.name}</div>
                  <div className="text-xs font-mono text-slate-400">{p.code}</div>
                </div>
                <StatusBadge value={p.status} />
              </div>
              <div className="mt-3 text-sm text-slate-600 space-y-1">
                <div>🏢 {p.department || '—'}</div>
                <div>👤 {p.manager || '—'}</div>
                <div className="font-medium text-brand-600">
                  {p.employee_count} employee{p.employee_count === 1 ? '' : 's'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Project">
        <form onSubmit={submitCreate} className="space-y-3">
          <input className="input" placeholder="Code (e.g. PRJ-041)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required />
          <input className="input" placeholder="Project name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input className="input" placeholder="Department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
          <input className="input" placeholder="Manager" value={form.manager} onChange={(e) => setForm({ ...form, manager: e.target.value })} />
          <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="active">Active</option>
            <option value="on_hold">On hold</option>
            <option value="completed">Completed</option>
          </select>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button type="submit" className="btn-primary">Create</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
