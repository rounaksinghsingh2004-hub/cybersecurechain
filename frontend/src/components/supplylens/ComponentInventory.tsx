import { useState } from 'react'
import { AlertTriangle, Box, CheckCircle2, RefreshCw, Search, ShieldAlert, Sparkles } from 'lucide-react'
import { Metric, Panel, Status } from '../common'
import { DataTable } from '../table'
import { api, post } from '../../services/api'
import { useAppStore } from '../../stores/app-store'

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

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading components...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

export function ComponentInventory() {
  const { setDrawer } = useAppStore()
  const [search, setSearch] = useState('')
  const [severity, setSeverity] = useState('')
  const [enrichingId, setEnrichingId] = useState<number | null>(null)
  const [enrichMsg, setEnrichMsg] = useState('')

  const queryParams = new URLSearchParams()
  if (search) queryParams.set('search', search)
  if (severity) queryParams.set('severity', severity)
  const qs = queryParams.toString() ? `?${queryParams.toString()}` : ''

  const { data: components, loading, error, reload } = useData<any[]>(`/api/supplylens/components${qs}`, [])

  const handleEnrich = async (id: number, name: string) => {
    setEnrichingId(id)
    setEnrichMsg('')
    try {
      const res = await post<any>(`/api/supplylens/components/${id}/enrich`)
      setEnrichMsg(`Enriched ${name}: ${res.new_findings} new finding(s) discovered from OSV.dev`)
      reload()
    } catch (e: any) {
      setEnrichMsg(`Enrichment failed: ${e.message}`)
    } finally {
      setEnrichingId(null)
      setTimeout(() => setEnrichMsg(''), 5000)
    }
  }

  if (loading && !components.length) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const total = components.length
  const critical = components.filter(c => c.risk_level === 'CRITICAL').length
  const direct = components.filter(c => c.direct).length
  const withFindings = components.filter(c => c.finding_count > 0).length

  const columns = [
    { key: 'name', label: 'Component' },
    { key: 'version', label: 'Version' },
    { key: 'ecosystem', label: 'Ecosystem' },
    { key: 'supplier_name', label: 'Supplier' },
    { key: 'direct', label: 'Direct', render: (val: any) => (val ? 'Direct' : 'Transitive') },
    { key: 'finding_count', label: 'Findings' },
    { key: 'risk_level', label: 'Risk Level', status: true },
    { key: 'risk_score', label: 'Risk Score' },
  ]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · COMPONENT INVENTORY</span>
          <h2>Software Bill of Materials Components</h2>
          <p>
            Unified inventory of runtime libraries, direct and transitive dependencies mapped from ingested SBOMs.
            Enrichable on-demand via the OSV.dev vulnerability index.
          </p>
        </div>
        <button className="quiet-button" onClick={reload}><RefreshCw size={15} /> Refresh</button>
      </section>

      <section className="metric-grid">
        <Metric label="Total Components" value={total} note="Tracked across all projects" />
        <Metric label="Direct Dependencies" value={direct} tone="teal" note="First-order manifest imports" />
        <Metric label="With Known CVEs" value={withFindings} tone="red" note="Identified vulnerabilities" />
        <Metric label="Critical Risk" value={critical} tone="gold" note="Immediate triage priority" />
      </section>

      {enrichMsg && (
        <div style={{ padding: '10px 16px', background: 'rgba(92, 224, 192, 0.1)', border: '1px solid #5CE0C0', borderRadius: 6, color: '#5CE0C0', display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <Sparkles size={16} />
          <span>{enrichMsg}</span>
        </div>
      )}

      <Panel title="Filter Components">
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#0a1620', border: '1px solid #1e3344', borderRadius: 4, padding: '4px 10px', flex: '1 1 240px' }}>
            <Search size={14} color="#8da1ad" />
            <input
              type="text"
              placeholder="Search component name..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#c0d8e0', outline: 'none', width: '100%', fontSize: 12 }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: '#8ca7af', textTransform: 'uppercase' }}>Severity Filter:</span>
            <select
              value={severity}
              onChange={e => setSeverity(e.target.value)}
              style={{ background: '#0a1620', border: '1px solid #1e3344', color: '#c0d8e0', borderRadius: 4, padding: '6px 10px', fontSize: 12 }}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
        </div>
      </Panel>

      <Panel title={`Component Register (${components.length})`}>
        <DataTable
          rows={components}
          columns={columns}
          onRowClick={row => setDrawer({ title: `${row.name} v${row.version}`, data: row })}
        />
      </Panel>

      <Panel title="Component Quick Actions">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
          {components.slice(0, 6).map(c => (
            <div key={c.id} style={{ padding: 12, background: '#0f1e2a', border: '1px solid #1a3040', borderRadius: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <b style={{ fontSize: 13, color: '#e2eef2' }}>{c.name}</b>
                <div style={{ fontSize: 11, color: '#6a8fa0' }}>v{c.version} · {c.ecosystem}</div>
                <div style={{ marginTop: 4 }}><Status value={c.risk_level || 'LOW'} /></div>
              </div>
              <button
                className="quiet-button"
                disabled={enrichingId === c.id}
                onClick={() => handleEnrich(c.id, c.name)}
                style={{ fontSize: 11, padding: '6px 10px', borderColor: '#42b7c2', color: '#42b7c2' }}
              >
                <Sparkles size={13} /> {enrichingId === c.id ? 'Checking...' : 'OSV Enrich'}
              </button>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  )
}
