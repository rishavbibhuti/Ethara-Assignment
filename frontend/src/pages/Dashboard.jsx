import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../api/client.js'
import { Spinner } from '../components/ui.jsx'

const PIE_COLORS = {
  available: '#22c55e',
  occupied: '#3b82f6',
  reserved: '#a855f7',
  maintenance: '#ef4444',
}

function StatCard({ label, value, accent }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-500">{label}</div>
      <div className={`text-3xl font-bold mt-1 ${accent || 'text-slate-800'}`}>{value}</div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [byBuilding, setByBuilding] = useState([])
  const [byDept, setByDept] = useState([])
  const [seatBreakdown, setSeatBreakdown] = useState([])

  useEffect(() => {
    api.stats().then(setStats)
    api.utilizationByBuilding().then(setByBuilding)
    api.employeesByDepartment().then(setByDept)
    api.seatStatusBreakdown().then(setSeatBreakdown)
  }, [])

  if (!stats) return <Spinner label="Loading dashboard…" />

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Dashboard</h1>
      <p className="text-slate-500 mb-6">Seat allocation & utilization overview</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Employees" value={stats.total_employees.toLocaleString()} />
        <StatCard label="Total Seats" value={stats.total_seats.toLocaleString()} />
        <StatCard
          label="Seat Utilization"
          value={`${stats.utilization_pct}%`}
          accent="text-brand-600"
        />
        <StatCard
          label="Available Seats"
          value={stats.available_seats.toLocaleString()}
          accent="text-green-600"
        />
        <StatCard label="Occupied Seats" value={stats.occupied_seats.toLocaleString()} accent="text-blue-600" />
        <StatCard label="New Joiners" value={stats.new_joiners.toLocaleString()} accent="text-amber-600" />
        <StatCard
          label="Unseated Employees"
          value={stats.unseated_employees.toLocaleString()}
          accent="text-red-600"
        />
        <StatCard label="Projects" value={stats.total_projects.toLocaleString()} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-4">Utilization by Building</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byBuilding}>
              <XAxis dataKey="building" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="occupied" stackId="a" fill="#3b82f6" name="Occupied" />
              <Bar dataKey="available" stackId="a" fill="#22c55e" name="Available" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Seat Status Breakdown</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={seatBreakdown}
                dataKey="count"
                nameKey="status"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(e) => `${e.status} (${e.count})`}
              >
                {seatBreakdown.map((entry) => (
                  <Cell key={entry.status} fill={PIE_COLORS[entry.status] || '#94a3b8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card lg:col-span-2">
          <h3 className="font-semibold mb-4">Employees by Department</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byDept} margin={{ bottom: 40 }}>
              <XAxis dataKey="department" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b6ff6" name="Employees" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
