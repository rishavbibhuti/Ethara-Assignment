import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { EmptyState, Spinner, StatusBadge } from '../components/ui.jsx'

export default function NewJoiners() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)

  function load() {
    setLoading(true)
    api
      .employees({ status: 'new_joiner', has_seat: false, page_size: 100 })
      .then((d) => {
        setData(d)
        setLoading(false)
      })
  }

  useEffect(load, [])

  async function runAutoAllocate() {
    setRunning(true)
    setResult(null)
    try {
      const r = await api.allocateNewJoiners()
      setResult(r)
      load()
    } finally {
      setRunning(false)
    }
  }

  async function allocateOne(id) {
    await api.allocate({ employee_id: id, allocated_by: 'admin' })
    load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">New Joiner Allocation</h1>
          <p className="text-slate-500">New joiners currently without a seat</p>
        </div>
        <button className="btn-primary" disabled={running} onClick={runAutoAllocate}>
          {running ? 'Allocating…' : '⚡ Auto-allocate all'}
        </button>
      </div>

      {result && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700 text-sm">
          Allocated {result.allocated_count} seat(s).{' '}
          {result.skipped_count > 0 && `${result.skipped_count} skipped (no seats available).`}
        </div>
      )}

      <div className="card">
        {loading ? (
          <Spinner />
        ) : data.items.length === 0 ? (
          <EmptyState message="🎉 All new joiners have seats." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Code</th>
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Department</th>
                  <th className="py-2 pr-4">Team</th>
                  <th className="py-2 pr-4">Joined</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((e) => (
                  <tr key={e.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 pr-4 font-mono text-xs">{e.employee_code}</td>
                    <td className="py-2 pr-4 font-medium">{e.name}</td>
                    <td className="py-2 pr-4">{e.department}</td>
                    <td className="py-2 pr-4">{e.team}</td>
                    <td className="py-2 pr-4">{e.join_date}</td>
                    <td className="py-2 pr-4"><StatusBadge value={e.status} /></td>
                    <td className="py-2 pr-4">
                      <button className="btn-ghost" onClick={() => allocateOne(e.id)}>
                        Allocate seat
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data.total > data.items.length && (
              <p className="text-xs text-slate-400 mt-3">
                Showing {data.items.length} of {data.total}. Use “Auto-allocate all” to process everyone.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
