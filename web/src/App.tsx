import { useState } from 'react'

type ReportResponse = {
  location: string
  hours: number
  generated_at: string
  report: string
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [location, setLocation] = useState('Sanaa, Yemen')
  const [hours, setHours] = useState(4)
  const [useLLM, setUseLLM] = useState(true)
  const [model, setModel] = useState('phi3:mini')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReportResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, hours, use_llm: useLLM, model })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: ReportResponse = await res.json()
      setResult(data)
    } catch (err: any) {
      setError(err?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '2rem auto', padding: '0 1rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Network Outage Reporter</h1>
      <form onSubmit={submit} style={{ display: 'grid', gap: 12, marginBottom: 16 }}>
        <label>
          Location
          <input value={location} onChange={e => setLocation(e.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
        <label>
          Hours lookback
          <input type="number" min={1} max={72} value={hours} onChange={e => setHours(parseInt(e.target.value || '1', 10))} style={{ width: '100%', padding: 8 }} />
        </label>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input type="checkbox" checked={useLLM} onChange={e => setUseLLM(e.target.checked)} /> Use LLM
          </label>
          <input placeholder="model name" value={model} onChange={e => setModel(e.target.value)} style={{ flex: 1, padding: 8 }} />
        </div>
        <button disabled={loading} type="submit" style={{ padding: '8px 12px' }}>
          {loading ? 'Generating…' : 'Generate Report'}
        </button>
      </form>

      {error && <div style={{ color: 'crimson' }}>Error: {error}</div>}

      {result && (
        <div>
          <h2>Report</h2>
          <div style={{ fontSize: 12, color: '#555' }}>
            {result.location} • {result.hours}h • {new Date(result.generated_at).toLocaleString()}
          </div>
          <textarea readOnly value={result.report} style={{ width: '100%', height: 400, marginTop: 8, fontFamily: 'monospace' }} />
        </div>
      )}
    </div>
  )
}

