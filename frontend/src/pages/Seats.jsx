import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { EmptyState, Pagination, Spinner, StatusBadge } from '../components/ui.jsx'

export default function Seats() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [locations, setLocations] = useState({ buildings: [], floors: [], zones: [] })
  const [filters, setFilters] = useState({ q: '', status: '', building: '', floor: '', zone: '' })
  const [page, setPage] = useState(1)
  const pageSize = 40

  function load() {
    setLoading(true)
    const params = { page, page_size: pageSize }
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== '') params[k] = v
    })
    api.seats(params).then((d) => {
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

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Seats</h1>
      <p className="text-slate-500 mb-6">Seat inventory & availability</p>

      <div className="card mb-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <input className="input" placeholder="Seat number…" value={filters.q} onChange={(e) => updateFilter('q', e.target.value)} />
          <select className="input" value={filters.status} onChange={(e) => updateFilter('status', e.target.value)}>
            <option value="">Any status</option>
            <option value="available">Available</option>
            <option value="occupied">Occupied</option>
            <option value="reserved">Reserved</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <select className="input" value={filters.building} onChange={(e) => updateFilter('building', e.target.value)}>
            <option value="">Any building</option>
            {locations.buildings.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
          <select className="input" value={filters.floor} onChange={(e) => updateFilter('floor', e.target.value)}>
            <option value="">Any floor</option>
            {locations.floors.map((f) => <option key={f} value={f}>Floor {f}</option>)}
          </select>
          <select className="input" value={filters.zone} onChange={(e) => updateFilter('zone', e.target.value)}>
            <option value="">Any zone</option>
            {locations.zones.map((z) => <option key={z} value={z}>{z}</option>)}
          </select>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <Spinner />
        ) : data.items.length === 0 ? (
          <EmptyState message="No seats match your filters." />
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {data.items.map((s) => (
                <div key={s.id} className="border border-slate-200 rounded-lg p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-medium">{s.seat_number}</span>
                    <StatusBadge value={s.status} />
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    {s.building} · Fl {s.floor} · {s.zone}
                  </div>
                  {s.employee && (
                    <div className="text-xs text-slate-600 mt-1 truncate">👤 {s.employee.name}</div>
                  )}
                </div>
              ))}
            </div>
            <Pagination page={data.page} pageSize={data.page_size} total={data.total} onChange={setPage} />
          </>
        )}
      </div>
    </div>
  )
}
