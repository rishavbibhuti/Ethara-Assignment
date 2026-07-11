// Small reusable presentational components.

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-2 text-slate-500 text-sm py-6">
      <span className="h-4 w-4 border-2 border-slate-300 border-t-brand-600 rounded-full animate-spin" />
      {label}
    </div>
  )
}

const STATUS_STYLES = {
  active: 'bg-green-100 text-green-700',
  new_joiner: 'bg-amber-100 text-amber-700',
  inactive: 'bg-slate-200 text-slate-600',
  available: 'bg-green-100 text-green-700',
  occupied: 'bg-blue-100 text-blue-700',
  reserved: 'bg-purple-100 text-purple-700',
  maintenance: 'bg-red-100 text-red-700',
  on_hold: 'bg-amber-100 text-amber-700',
  completed: 'bg-slate-200 text-slate-600',
}

export function StatusBadge({ value }) {
  const cls = STATUS_STYLES[value] || 'bg-slate-100 text-slate-600'
  return <span className={`badge ${cls}`}>{String(value).replace('_', ' ')}</span>
}

export function Pagination({ page, pageSize, total, onChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  return (
    <div className="flex items-center justify-between mt-4 text-sm text-slate-600">
      <span>
        {total.toLocaleString()} results · page {page} of {totalPages}
      </span>
      <div className="flex gap-2">
        <button
          className="btn-ghost disabled:opacity-40"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
        >
          ← Prev
        </button>
        <button
          className="btn-ghost disabled:opacity-40"
          disabled={page >= totalPages}
          onClick={() => onChange(page + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  )
}

export function Modal({ open, onClose, title, children }) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button className="text-slate-400 hover:text-slate-600" onClick={onClose}>
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function EmptyState({ message }) {
  return <div className="text-center text-slate-400 py-10 text-sm">{message}</div>
}
