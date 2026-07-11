import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client.js'

export default function Assistant() {
  const [examples, setExamples] = useState([])
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hi! Ask me about seats, employees, projects or utilization. Try one of the suggestions below.",
    },
  ])
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    api.assistantExamples().then((d) => setExamples(d.examples))
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function ask(question) {
    const q = question ?? input
    if (!q.trim()) return
    setMessages((m) => [...m, { role: 'user', text: q }])
    setInput('')
    setLoading(true)
    try {
      const res = await api.ask(q)
      setMessages((m) => [
        ...m,
        { role: 'assistant', text: res.answer, data: res.data, intent: res.intent, sql: res.sql_like },
      ])
    } catch {
      setMessages((m) => [...m, { role: 'assistant', text: 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-1">AI Assistant</h1>
      <p className="text-slate-500 mb-6">Natural-language queries over your seat & employee data</p>

      <div className="card min-h-[420px] flex flex-col">
        <div className="flex-1 space-y-4 overflow-y-auto max-h-[520px] pr-1">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`rounded-2xl px-4 py-2 max-w-[85%] text-sm ${
                  m.role === 'user' ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-800'
                }`}
              >
                <div>{m.text}</div>
                {m.data && m.data.length > 0 && (
                  <div className="mt-2 bg-white/70 rounded-lg p-2 max-h-52 overflow-auto">
                    <table className="text-xs w-full">
                      <thead>
                        <tr className="text-slate-500 text-left">
                          {Object.keys(m.data[0]).map((k) => (
                            <th key={k} className="pr-3 py-0.5">{k}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {m.data.slice(0, 15).map((row, ri) => (
                          <tr key={ri} className="border-t border-slate-200">
                            {Object.values(row).map((v, vi) => (
                              <td key={vi} className="pr-3 py-0.5">{v === null ? '—' : String(v)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {m.data.length > 15 && (
                      <div className="text-slate-400 mt-1">+{m.data.length - 15} more…</div>
                    )}
                  </div>
                )}
                {m.sql && (
                  <div className="mt-2 text-[11px] font-mono text-slate-400">{m.sql}</div>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-slate-400 text-sm">Thinking…</div>}
          <div ref={endRef} />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {examples.map((ex) => (
            <button
              key={ex}
              className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200"
              onClick={() => ask(ex)}
            >
              {ex}
            </button>
          ))}
        </div>

        <form
          className="mt-3 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            ask()
          }}
        >
          <input
            className="input"
            placeholder="Ask a question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
