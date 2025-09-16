import { useMemo, useState } from 'react'

type ReportResponse = {
  location: string
  hours: number
  generated_at: string
  report: string
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [location, setLocation] = useState('Sanaa, Yemen')
  const [hours, setHours] = useState(24)
  const [useLLM, setUseLLM] = useState(true)
  const [model, setModel] = useState('phi3:mini')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [articles, setArticles] = useState<any[]>([])
  const [selected, setSelected] = useState<Record<number, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReportResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  function onImageChange(f: File | null) {
    setImageFile(f)
    setImagePreview(null)
    setImageBase64(null)
    if (!f) return
    const reader = new FileReader()
    reader.onload = () => {
      const dataUrl = reader.result as string
      setImagePreview(dataUrl)
      const base64 = dataUrl.split(',')[1] || ''
      setImageBase64(base64)
    }
    reader.readAsDataURL(f)
  }

  async function getNews() {
    try {
      setError(null)
      setArticles([])
      setSelected({})
      const body = { query: location, hours }
      const res = await fetch(`${API_URL}/news`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setArticles(data.articles || [])
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch news')
    }
  }

  const selectedArticles = useMemo(() => articles.filter((_, idx) => selected[idx]), [articles, selected])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, hours, use_llm: useLLM, model, image_base64: imageBase64, articles: selectedArticles })
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
    <div className="container">
      <div className="header">
        <div>
          <div className="title">Network Outage Reporter</div>
          <div className="subtitle">Upload an image, pick the news, and generate a clear report.</div>
        </div>
        <div className="pill">API: {API_URL.replace(/^https?:\/\//,'')}</div>
      </div>

      {error && <div className="error" role="alert">{error}</div>}

      <div className="grid">
        <div className="left">
          <div className="card">
            <div className="section-title">Inputs</div>
            <div className="section-sub">Set location and time window for fetching recent news.</div>

            <div className="field">
              <label className="label">Location</label>
              <input className="input" value={location} onChange={e => setLocation(e.target.value)} placeholder="City, Country" />
            </div>
            <div className="field">
              <label className="label">Hours lookback</label>
              <input className="input" type="number" min={1} max={72} value={hours} onChange={e => setHours(parseInt(e.target.value || '1', 10))} />
            </div>

            <div className="field">
              <label className="label">Outage Image (PNG/JPEG)</label>
              <input className="input" accept="image/png,image/jpeg" type="file" onChange={e => onImageChange(e.target.files?.[0] || null)} />
              {imagePreview && (
                <div className="preview"><img src={imagePreview} alt="Preview" /></div>
              )}
            </div>

            <div className="row" style={{ marginTop: 6 }}>
              <button type="button" className="btn" onClick={getNews}>Fetch Latest News</button>
              <span className="count">{articles.length ? `${articles.length} articles` : 'No articles yet'}</span>
            </div>

            {articles.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <div className="section-title">Select relevant articles <span className="count">({selectedArticles.length} selected)</span></div>
                <div className="articles">
                  {articles.map((a, idx) => (
                    <div className="article" key={idx}>
                      <input type="checkbox" checked={!!selected[idx]} onChange={e => setSelected(s => ({ ...s, [idx]: e.target.checked }))} />
                      <div>
                        <div className="article-title">{a.title || 'Untitled'}</div>
                        <div className="article-meta">{(a.source?.name) || a.source || ''}</div>
                        {a.url && <a href={a.url} target="_blank" rel="noreferrer">Open article</a>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="card" style={{ marginTop: 12 }}>
            <div className="section-title">Generation</div>
            <div className="row">
              <label className="row" style={{ gap: 8 }}>
                <input type="checkbox" checked={useLLM} onChange={e => setUseLLM(e.target.checked)} /> Use LLM
              </label>
              <input className="input grow" placeholder="model name" value={model} onChange={e => setModel(e.target.value)} />
            </div>
            <div className="row" style={{ marginTop: 12 }}>
              <button className="btn btn-primary" disabled={loading} onClick={submit as any}>
                {loading ? (<span><span className="spinner" /> Generating…</span>) : 'Generate Report'}
              </button>
              <span className="footer-note">Uses selected articles and the uploaded image when provided.</span>
            </div>
          </div>
        </div>

        <div className="right">
          <div className="card">
            <div className="section-title">Report Preview</div>
            {result ? (
              <>
                <div className="section-sub">{result.location} • {result.hours}h • {new Date(result.generated_at).toLocaleString()}</div>
                <textarea className="textarea" readOnly value={result.report} />
              </>
            ) : (
              <div className="section-sub">Generated report will appear here.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
