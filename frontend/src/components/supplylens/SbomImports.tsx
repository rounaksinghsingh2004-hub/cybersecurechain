import { useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, FileCode, RefreshCw, Upload } from 'lucide-react'
import { Panel, Status } from '../common'
import { api, post } from '../../services/api'

function useData<T>(path: string, fallback: T) {
  const [data, setData] = useState<T>(fallback)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const reload = () => {
    setLoading(true)
    api<T>(path).then(setData).catch(e => setError(e.message)).finally(() => setLoading(false))
  }
  useState(() => { reload() })
  return { data, loading, error, reload }
}

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

const DEMO_CYCLONEDX = JSON.stringify({
  bomFormat: 'CycloneDX', specVersion: '1.4', version: 1,
  components: [
    { type: 'library', name: 'log4j-core', version: '2.14.1', purl: 'pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1', scope: 'required' },
    { type: 'library', name: 'spring-core', version: '5.3.15', purl: 'pkg:maven/org.springframework/spring-core@5.3.15', scope: 'required' },
    { type: 'library', name: 'jackson-databind', version: '2.13.1', purl: 'pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.13.1', scope: 'required' }
  ]
}, null, 2)

export function SbomImports() {
  const { data: jobs, loading, error, reload } = useData<any[]>('/api/supplylens/imports', [])
  const { data: projects } = useData<any[]>('/api/supplylens/projects', [])
  const [projectId, setProjectId] = useState<number | ''>('')
  const [filename, setFilename] = useState('demo-cyclonedx.json')
  const [content, setContent] = useState(DEMO_CYCLONEDX)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [uploadError, setUploadError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFilename(f.name)
    const reader = new FileReader()
    reader.onload = ev => setContent(ev.target?.result as string)
    reader.readAsText(f)
  }

  const importSbom = async () => {
    if (!projectId) { setUploadError('Select a project first'); return }
    setUploading(true); setResult(null); setUploadError('')
    try {
      const res = await post<any>(`/api/supplylens/projects/${projectId}/import-sbom`, { filename, content })
      setResult(res); reload()
    } catch (e: any) { setUploadError(e.message) }
    finally { setUploading(false) }
  }

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const fmtStatus: Record<string, string> = { COMPLETED: 'SUCCESS', FAILED: 'CRITICAL', PROCESSING: 'MEDIUM', PENDING: 'LOW' }

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · SBOM INGESTION</span>
          <h2>SBOM Imports</h2>
          <p>Import Software Bill of Materials (CycloneDX JSON or SPDX JSON) to populate component inventory and trigger CVE enrichment.</p>
        </div>
        <button className="quiet-button" onClick={reload}><RefreshCw size={15} /> Refresh</button>
      </section>

      <section className="dashboard-grid">
        <Panel title="Upload SBOM">
          <div className="form-grid">
            <label>Target project
              <select value={projectId} onChange={e => setProjectId(Number(e.target.value) || '')}>
                <option value="">Select project...</option>
                {projects.map((p: any) => <option key={p.id} value={p.id}>{p.name} ({p.code})</option>)}
              </select>
            </label>
            <label>File (or paste JSON below)
              <div style={{ display: 'flex', gap: 8 }}>
                <input value={filename} onChange={e => setFilename(e.target.value)} placeholder="filename.json" style={{ flex: 1 }} />
                <button className="quiet-button" onClick={() => fileRef.current?.click()}><Upload size={14} /> Browse</button>
                <input ref={fileRef} type="file" accept=".json" style={{ display: 'none' }} onChange={handleFile} />
              </div>
            </label>
          </div>
          <label style={{ display: 'block', marginTop: 8 }}>
            <span style={{ fontSize: 10, color: '#8ca7af', fontWeight: 650, textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>SBOM JSON content</span>
            <textarea value={content} onChange={e => setContent(e.target.value)}
              style={{ width: '100%', minHeight: 160, fontFamily: 'monospace', fontSize: 11, background: '#0a1620', border: '1px solid #1e3344', color: '#c0d8e0', borderRadius: 4, padding: 10, resize: 'vertical', boxSizing: 'border-box' }} />
          </label>
          <div style={{ marginTop: 12, display: 'flex', gap: 10, alignItems: 'center' }}>
            <button className="launch-button" onClick={importSbom} disabled={uploading || !projectId}>
              <FileCode size={15} />{uploading ? 'Parsing...' : 'Import SBOM'}
            </button>
            <span style={{ fontSize: 11, color: '#5a7a8a' }}>Supported: CycloneDX 1.4+ JSON · SPDX 2.3 JSON</span>
          </div>
          {uploadError && <div className="error-box" style={{ marginTop: 8 }}>{uploadError}</div>}
          {result && (
            <div style={{ marginTop: 12, padding: 12, background: '#0b2618', border: '1px solid #2ecc71', borderRadius: 6 }}>
              <CheckCircle2 size={16} color="#2ecc71" style={{ marginBottom: 4 }} />
              <div style={{ color: '#2ecc71', fontWeight: 'bold' }}>Import completed</div>
              <div style={{ fontSize: 12, color: '#aaa', marginTop: 4 }}>
                Format: {result.format} · Components added: {result.components_added} · Relationships: {result.relationships}
              </div>
              {result.warnings?.length > 0 && (
                <div style={{ fontSize: 11, color: '#e8bd68', marginTop: 4 }}>
                  {result.warnings.length} warning(s): {result.warnings.slice(0, 2).join(', ')}
                </div>
              )}
            </div>
          )}
        </Panel>

        <Panel title="Format reference">
          <div style={{ fontSize: 12, color: '#8da1ad', lineHeight: 1.8 }}>
            <p><strong style={{ color: '#5CE0C0' }}>CycloneDX JSON</strong> — Industry standard for SBOM. Must have <code>bomFormat: "CycloneDX"</code> and a <code>components</code> array.</p>
            <p><strong style={{ color: '#5CE0C0' }}>SPDX JSON</strong> — SPDX 2.3 format. Must have <code>SPDXID</code>, <code>spdxVersion</code>, and <code>packages</code> array.</p>
            <p style={{ marginTop: 8 }}>Each component should have: <code>name</code>, <code>version</code>, optionally <code>purl</code> for enrichment targeting.</p>
            <p style={{ color: '#eb6969', marginTop: 8 }}>Max size: 5MB. Results labeled SYNTHETIC_DEMO.</p>
          </div>
        </Panel>
      </section>

      <Panel title={`Import history (${jobs.length})`} action={<span className="mini-label">ALL PROJECTS</span>}>
        {jobs.length === 0
          ? <div className="empty"><FileCode size={18} /> No imports yet. Upload an SBOM above.</div>
          : <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {jobs.map((j: any) => (
                <div key={j.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: '#0f1e2a', border: '1px solid #1a3040', borderRadius: 6 }}>
                  <div>
                    <b style={{ fontSize: 13 }}>{j.filename}</b>
                    <span style={{ marginLeft: 10, fontSize: 11, color: '#6a8fa0' }}>{j.project_name} · {j.format}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                    <span style={{ fontSize: 11, color: '#5CE0C0' }}>{j.component_count} components</span>
                    <Status value={fmtStatus[j.status] || j.status} />
                  </div>
                </div>
              ))}
            </div>
        }
      </Panel>
    </div>
  )
}
