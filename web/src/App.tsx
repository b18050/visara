import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx'
import { saveAs } from 'file-saver'

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
  const [model, setModel] = useState('gpt-4o-mini')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [articles, setArticles] = useState<any[]>([])
  const [selected, setSelected] = useState<Record<number, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReportResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editedReport, setEditedReport] = useState('')
  const [tempEditReport, setTempEditReport] = useState('')

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
      setLoading(true)
      const body = { query: location, hours }
      const res = await fetch(`${API_URL}/news`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      if (!res.ok) {
        // Gracefully handle API errors - don't show technical errors to users
        console.warn('News API not available, continuing in demo mode')
        setArticles([])
        return
      }
      const data = await res.json()
      setArticles(data.articles || [])
    } catch (err: any) {
      // Silent fail for demo - API might not be configured
      console.warn('News fetch failed:', err)
      setArticles([])
    } finally {
      setLoading(false)
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
      if (!res.ok) {
        const errorText = await res.text()
        console.error('Report generation failed:', errorText)
        setError('Unable to generate report. Please check your backend server is running.')
        return
      }
      const data: ReportResponse = await res.json()
      setResult(data)
      setEditedReport(data.report)
      setTempEditReport(data.report)
      setShowEditModal(false)
    } catch (err: any) {
      console.error('Report error:', err)
      setError('Connection failed. Make sure the backend server is running at ' + API_URL)
    } finally {
      setLoading(false)
    }
  }

  async function downloadPDF() {
    if (!result) return
    const element = document.getElementById('report-content')
    if (!element) return
    
    const canvas = await html2canvas(element, { scale: 2 })
    const imgData = canvas.toDataURL('image/png')
    
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
    pdf.save(`network-outage-report-${result.location.replace(/,\s*/g, '-')}.pdf`)
  }

  async function downloadDOCX() {
    if (!editedReport) return
    
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            text: `Network Outage Report: ${result?.location || 'Unknown'}`,
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph({
            text: `Generated: ${result?.generated_at ? new Date(result.generated_at).toLocaleString() : ''}`,
            spacing: { after: 200 },
          }),
          ...editedReport.split('\n').map(line => 
            new Paragraph({
              children: [new TextRun(line)],
            })
          ),
        ],
      }],
    })
    
    const blob = await Packer.toBlob(doc)
    saveAs(blob, `network-outage-report-${result?.location.replace(/,\s*/g, '-') || 'report'}.docx`)
  }

  function shareToInstagram() {
    if (!result) return
    const text = `Network Outage Report: ${result.location}\n\nGenerated with AI-powered analysis.\n\n#NetworkEngineering #OutageAnalysis #AI #TechTools`
    
    // Copy to clipboard for Instagram
    navigator.clipboard.writeText(editedReport.substring(0, 500) + '\n\n' + text)
    alert('📋 Report summary copied to clipboard!\n\nPaste it into your Instagram post.\n\n💡 Tip: Add a screenshot of the report for visual appeal.')
  }

  function openEditModal() {
    setTempEditReport(editedReport)
    setShowEditModal(true)
  }

  function saveEdit() {
    setEditedReport(tempEditReport)
    setShowEditModal(false)
  }

  function cancelEdit() {
    setTempEditReport(editedReport)
    setShowEditModal(false)
  }

  function insertMarkdown(type: string) {
    const textarea = document.getElementById('edit-textarea') as HTMLTextAreaElement
    if (!textarea) return
    
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = tempEditReport.substring(start, end)
    let newText = tempEditReport
    
    switch(type) {
      case 'bold':
        newText = tempEditReport.substring(0, start) + `**${selectedText || 'bold text'}**` + tempEditReport.substring(end)
        break
      case 'italic':
        newText = tempEditReport.substring(0, start) + `*${selectedText || 'italic text'}*` + tempEditReport.substring(end)
        break
      case 'heading':
        newText = tempEditReport.substring(0, start) + `## ${selectedText || 'Heading'}` + tempEditReport.substring(end)
        break
      case 'list':
        newText = tempEditReport.substring(0, start) + `\n- ${selectedText || 'List item'}` + tempEditReport.substring(end)
        break
    }
    
    setTempEditReport(newText)
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

      {error && <div className="error" role="alert">⚠️ {error}</div>}
      
      {!error && result && <div className="success" role="status">✅ Report generated successfully!</div>}

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
              <div className="section-sub" style={{ marginTop: -6, marginBottom: 8 }}>Optional: Upload a network outage visualization or map</div>
              <input className="input-file" accept="image/png,image/jpeg" type="file" onChange={e => onImageChange(e.target.files?.[0] || null)} />
              {imagePreview && (
                <div className="preview"><img src={imagePreview} alt="Preview" /></div>
              )}
            </div>

            <div className="row" style={{ marginTop: 6 }}>
              <button type="button" className="btn" onClick={getNews} disabled={loading}>
                {loading ? 'Fetching...' : 'Fetch Latest News'}
              </button>
              <span className="count">{articles.length ? `📰 ${articles.length} articles` : '📰 No articles yet'}</span>
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
            <div className="section-title">Report Generation</div>
            <div className="section-sub">Configure AI model settings (optional)</div>
            <div className="row">
              <label className="row" style={{ gap: 8 }}>
                <input type="checkbox" checked={useLLM} onChange={e => setUseLLM(e.target.checked)} /> Use AI/LLM
              </label>
              <input className="input grow" placeholder="model name (e.g., gpt-4o-mini, phi3:mini)" value={model} onChange={e => setModel(e.target.value)} />
            </div>
            <div style={{ marginTop: 12 }}>
              <button className="btn btn-primary" disabled={loading} onClick={submit as any} style={{ width: '100%' }}>
                {loading ? (<span><span className="spinner" /> Generating Report…</span>) : '🚀 Generate Network Outage Report'}
              </button>
              <div className="footer-note" style={{ marginTop: 8, textAlign: 'center' }}>
                {useLLM ? '🤖 Will use AI to analyze data' : '📋 Will use template-based analysis'}
              </div>
            </div>
          </div>
        </div>

        <div className="right">
          <div className="card">
            <div className="section-title">Report Preview</div>
            {result ? (
              <>
                <div className="report-header">
                  <div className="report-meta">
                    <span className="meta-badge">📍 {result.location}</span>
                    <span className="meta-badge">🕐 {result.hours}h window</span>
                    <span className="meta-badge">📅 {new Date(result.generated_at).toLocaleString()}</span>
                  </div>
                  
                  <div className="action-buttons">
                    <button className="action-btn edit-btn" onClick={openEditModal} title="Edit report">
                      ✏️ Edit
                    </button>
                    <button className="action-btn" onClick={shareToInstagram} title="Share to Instagram">
                      📸 Instagram
                    </button>
                    <button className="action-btn" onClick={downloadPDF} title="Download as PDF">
                      📄 PDF
                    </button>
                    <button className="action-btn" onClick={downloadDOCX} title="Download as DOCX">
                      📝 DOCX
                    </button>
                  </div>
                </div>

                <div id="report-content" className="report-content">
                  <ReactMarkdown>{editedReport}</ReactMarkdown>
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📊</div>
                <div className="empty-text">Generated report will appear here</div>
                <div className="empty-hint">Enter location and click "Generate Report"</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="modal-overlay" onClick={cancelEdit}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">✏️ Edit Report</h2>
              <button className="modal-close" onClick={cancelEdit}>✕</button>
            </div>

            <div className="modal-toolbar">
              <button className="toolbar-btn" onClick={() => insertMarkdown('bold')} title="Bold">
                <strong>B</strong>
              </button>
              <button className="toolbar-btn" onClick={() => insertMarkdown('italic')} title="Italic">
                <em>I</em>
              </button>
              <button className="toolbar-btn" onClick={() => insertMarkdown('heading')} title="Heading">
                H1
              </button>
              <button className="toolbar-btn" onClick={() => insertMarkdown('list')} title="Bullet List">
                • List
              </button>
              <div className="toolbar-divider"></div>
              <span className="toolbar-hint">Select text and click formatting buttons</span>
            </div>

            <div className="modal-body">
              <div className="edit-container">
                <div className="edit-pane">
                  <div className="pane-label">📝 Markdown Editor</div>
                  <textarea
                    id="edit-textarea"
                    className="modal-textarea"
                    value={tempEditReport}
                    onChange={e => setTempEditReport(e.target.value)}
                    placeholder="Edit your report using Markdown..."
                  />
                </div>
                <div className="preview-pane">
                  <div className="pane-label">👁️ Live Preview</div>
                  <div className="modal-preview">
                    <ReactMarkdown>{tempEditReport}</ReactMarkdown>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn" onClick={cancelEdit}>Cancel</button>
              <button className="btn btn-primary" onClick={saveEdit}>💾 Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
