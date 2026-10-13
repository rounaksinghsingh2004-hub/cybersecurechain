import { useState } from 'react'
import { AlertTriangle, CheckCircle2, Download, Filter, RefreshCw, ShieldAlert, Tag } from 'lucide-react'
import { Metric, Panel, Status } from '../common'
import { DataTable } from '../table'
import { api } from '../../services/api'
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

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading findings...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

export function FindingsView() {
  const { setDrawer } = useAppStore()
  const [severity, setSeverity] = useState('')
  const [status, setStatus] = useState('')
  const [updatingId, setUpdatingId] = useState<number | null>(null)

  const queryParams = new URLSearchParams()
  if (severity) queryParams.set('severity', severity)
  if (status) queryParams.set('status', status)
  const qs = queryParams.toString() ? `?${queryParams.toString()}` : ''

  const { data: findings, loading, error, reload } = useData<any[]>(`/api/supplylens/findings${qs}`, [])

  const handleStatusChange = async (findingId: number, nextStatus: string) => {
    setUpdatingId(findingId)
    try {
      await fetch(`http://localhost:8000/api/supplylens/findings/${findingId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      })
      reload()
    } catch {
      // Fallback
    } finally {
      setUpdatingId(null)
    }
  }

  const exportCsv = () => {
    window.open('http://localhost:8000/api/supplylens/reports/findings.csv', '_blank')
  }

  if (loading && !findings.length) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const total = findings.length
  const critical = findings.filter(f => f.severity === 'CRITICAL').length
  const kev = findings.filter(f => f.cisa_kev).length
  const openCount = findings.filter(f => f.status === 'OPEN').length

  const columns = [
    { key: 'vulnerability_id', label: 'Vulnerability ID' },
    { key: 'component_name', label: 'Affected Component' },
    { key: 'severity', label: 'Severity', status: true },
    { key: 'cvss_score', label: 'CVSS Score' },
    { key: 'cisa_kev', label: 'CISA KEV', render: (val: any) => (val ? 'ACTIVE' : 'NO') },
    { key: 'status', label: 'Triage Status', status: true },
    { key: 'source', label: 'Source' },
  ]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · VULNERABILITY FINDINGS</span>
          <h2>Vulnerability & Exploitation Register</h2>
          <p>
            Identified vulnerabilities across ingested dependencies with automated CISA KEV flagging,
            CVSS scoring, and remediation workflow tracking.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="quiet-button" onClick={exportCsv}>
            <Download size={14} /> Export CSV
          </button>
          <button className="quiet-button" onClick={reload}>
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </section>

      <section className="metric-grid">
        <Metric label="Total Findings" value={total} note="Active and triaged CVEs" />
        <Metric label="Critical Severity" value={critical} tone="red" note="CVSS 9.0 - 10.0" />
        <Metric label="CISA KEV Matches" value={kev} tone="gold" note="Actively exploited in wild" />
        <Metric label="Pending Triage" value={openCount} tone="teal" note="Action required" />
      </section>

      <Panel title="Filter Findings">
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Filter size={14} color="#8da1ad" />
            <span style={{ fontSize: 11, color: '#8ca7af', textTransform: 'uppercase' }}>Severity:</span>
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

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Tag size={14} color="#8da1ad" />
            <span style={{ fontSize: 11, color: '#8ca7af', textTransform: 'uppercase' }}>Status:</span>
            <select
              value={status}
              onChange={e => setStatus(e.target.value)}
              style={{ background: '#0a1620', border: '1px solid #1e3344', color: '#c0d8e0', borderRadius: 4, padding: '6px 10px', fontSize: 12 }}
            >
              <option value="">All Statuses</option>
              <option value="OPEN">OPEN</option>
              <option value="IN_TRIAGE">IN_TRIAGE</option>
              <option value="MITIGATED">MITIGATED</option>
              <option value="ACCEPTED">ACCEPTED</option>
            </select>
          </div>
        </div>
      </Panel>

      <Panel title={`Findings List (${findings.length})`}>
        <DataTable
          rows={findings}
          columns={columns}
          onRowClick={row => setDrawer({ title: `${row.vulnerability_id} · ${row.component_name}`, data: row })}
        />
      </Panel>

      <Panel title="Vulnerability Triage & Actions">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {findings.map(f => (
            <div key={f.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 14, background: '#0f1e2a', border: '1px solid #1a3040', borderRadius: 6, flexWrap: 'wrap', gap: 10 }}>
              <div style={{ maxWidth: '65%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <b style={{ color: f.severity === 'CRITICAL' ? '#eb6969' : f.severity === 'HIGH' ? '#e8bd68' : '#5CE0C0', fontSize: 14 }}>
                    {f.vulnerability_id}
                  </b>
                  <Status value={f.severity} />
                  {f.cisa_kev && <span style={{ background: '#e8bd68', color: '#000', fontSize: 10, fontWeight: 700, padding: '1px 6px', borderRadius: 3 }}>CISA KEV</span>}
                </div>
                <div style={{ fontSize: 12, color: '#c0d8e0', marginTop: 4 }}>
                  Component: <strong>{f.component_name}</strong> {f.fixed_version ? `(Fixed in: ${f.fixed_version})` : ''}
                </div>
                <p style={{ fontSize: 11, color: '#8da1ad', margin: '4px 0 0 0' }}>{f.summary}</p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 11, color: '#8ca7af' }}>Status:</span>
                <select
                  value={f.status}
                  disabled={updatingId === f.id}
                  onChange={e => handleStatusChange(f.id, e.target.value)}
                  style={{ background: '#0a1620', border: '1px solid #2d4a52', color: '#c8d9db', borderRadius: 4, padding: '6px 10px', fontSize: 12 }}
                >
                  <option value="OPEN">OPEN</option>
                  <option value="IN_TRIAGE">IN_TRIAGE</option>
                  <option value="MITIGATED">MITIGATED</option>
                  <option value="ACCEPTED">ACCEPTED</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  )
}
