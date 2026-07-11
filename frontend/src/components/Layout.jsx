import { NavLink, Outlet } from 'react-router-dom'

const NAV = [
  { to: '/', label: 'Dashboard', icon: '📊', end: true },
  { to: '/employees', label: 'Employees', icon: '👥' },
  { to: '/projects', label: 'Projects', icon: '📁' },
  { to: '/seats', label: 'Seats', icon: '💺' },
  { to: '/new-joiners', label: 'New Joiners', icon: '✨' },
  { to: '/assistant', label: 'AI Assistant', icon: '🤖' },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-slate-900 text-slate-100 flex flex-col fixed h-full">
        <div className="px-6 py-5 border-b border-slate-800">
          <div className="text-xl font-bold tracking-tight">SeatFlow</div>
          <div className="text-xs text-slate-400 mt-0.5">Seat & Project Mapping</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-slate-500 border-t border-slate-800">
          ~5,000 employees · 5,600 seats
        </div>
      </aside>

      <main className="flex-1 ml-60 p-8 max-w-[1400px]">
        <Outlet />
      </main>
    </div>
  )
}
