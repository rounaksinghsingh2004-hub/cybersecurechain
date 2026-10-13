import { useState } from 'react'
import { AlertTriangle, ArrowRight, Building2, CheckCircle2, Cpu, GitBranch, Package, RefreshCw, Server, ShieldAlert, Trash2 } from 'lucide-react'
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

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading exposure map...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

export function ExposureMap() {
  const { setDrawer } = useAppStore()
  const { data: deployments, loading, error, reload } = useData<any[]>('/api/supplylens/deployments', [])
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const handleDelete = async (id: number) => {
    setDeletingId(id)
    try {
      await fetch(`http://localhost:8000/api/supplylens/deployments/${id}`, { method: 'DELETE' })
      reload()
    } catch {
      // Fallback
    } finally {
      setDeletingId(null)
    }
  }

  if (loading && !deployments.length) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const total = deployments.length
  const facilities = new Set(deployments.map(d => d.facility).filter(Boolean)).size
  const verified = deployments.filter(d => d.mapping_type === 'VERIFIED').length

  const columns = [
    { key: 'component_name', label: 'Software Component' },
    { key: 'service_name', label: 'Service / Microservice' },
    { key: 'cyber_asset', label: 'Cyber Asset' },
    { key: 'facility', label: 'Operational Facility' },
    { key: 'business_process', label: 'Impacted Business Process' },
    { key: 'mapping_type', label: 'Mapping Evidence', status: true },
  ]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · CYBER-PHYSICAL EXPOSURE</span>
          <h2>Software-to-Operations Exposure Map</h2>
          <p>
            Trace software dependencies directly into physical operations: from vulnerable open-source packages
            to running microservices, host cyber assets, operational facilities, and vulnerable customer orders.
          </p>
        </div>
        <button className="quiet-button" onClick={reload}><RefreshCw size={15} /> Refresh</button>
      </section>

      <section className="metric-grid">
        <Metric label="Mapped Deployments" value={total} note="Active component bindings" />
        <Metric label="Impacted Facilities" value={facilities} tone="red" note="Warehouses & Hubs exposed" />
        <Metric label="Verified Linkages" value={verified} tone="teal" note="Ground-truth telemetry confirmed" />
        <Metric label="Chain Depth" value="4 Levels" tone="gold" note="Pkg → Svc → Host → Facility" />
      </section>

      <Panel title="Interactive Propagation Chains">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {deployments.map(d => (
            <div key={d.id} style={{ background: '#0a1620', border: '1px solid #1a3040', borderRadius: 8, padding: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: '#5CE0C0', textTransform: 'uppercase' }}>
                  Propagation Path #{d.id} · {d.business_process}
                </span>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <Status value={d.mapping_type} />
                  <button
                    onClick={() => handleDelete(d.id)}
                    disabled={deletingId === d.id}
                    className="quiet-button"
                    style={{ padding: '4px 8px', color: '#eb6969', borderColor: '#4a1515' }}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              {/* Chain Steps */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, alignItems: 'center' }}>
                <div style={{ background: '#0f1e2a', padding: 12, borderRadius: 6, border: '1px solid #2d4a52' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#eb6969', fontWeight: 700 }}>
                    <ShieldAlert size={14} /> PACKAGE
                  </div>
                  <b style={{ display: 'block', marginTop: 4, fontSize: 13, color: '#e2eef2' }}>{d.component_name || 'Component'}</b>
                  <span style={{ fontSize: 10, color: '#6a8fa0' }}>Software Dependency</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <ArrowRight size={20} color="#5CE0C0" />
                </div>

                <div style={{ background: '#0f1e2a', padding: 12, borderRadius: 6, border: '1px solid #2d4a52' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#42b7c2', fontWeight: 700 }}>
                    <Server size={14} /> RUNTIME SERVICE
                  </div>
                  <b style={{ display: 'block', marginTop: 4, fontSize: 13, color: '#e2eef2' }}>{d.service_name}</b>
                  <span style={{ fontSize: 10, color: '#6a8fa0' }}>Microservice Layer</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <ArrowRight size={20} color="#5CE0C0" />
                </div>

                <div style={{ background: '#0f1e2a', padding: 12, borderRadius: 6, border: '1px solid #2d4a52' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#e8bd68', fontWeight: 700 }}>
                    <Cpu size={14} /> CYBER ASSET
                  </div>
                  <b style={{ display: 'block', marginTop: 4, fontSize: 13, color: '#e2eef2' }}>{d.cyber_asset || 'Host Asset'}</b>
                  <span style={{ fontSize: 10, color: '#6a8fa0' }}>Infrastructure Node</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <ArrowRight size={20} color="#5CE0C0" />
                </div>

                <div style={{ background: '#0f1e2a', padding: 12, borderRadius: 6, border: '1px solid #2d4a52' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#5CE0C0', fontWeight: 700 }}>
                    <Building2 size={14} /> PHYSICAL FACILITY
                  </div>
                  <b style={{ display: 'block', marginTop: 4, fontSize: 13, color: '#e2eef2' }}>{d.facility || 'Facility Hub'}</b>
                  <span style={{ fontSize: 10, color: '#6a8fa0' }}>Digital Twin Site</span>
                </div>
              </div>

              {d.notes && (
                <div style={{ marginTop: 10, fontSize: 11, color: '#8da1ad', fontStyle: 'italic' }}>
                  Note: {d.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      </Panel>

      <Panel title={`Full Mappings Table (${deployments.length})`}>
        <DataTable
          rows={deployments}
          columns={columns}
          onRowClick={row => setDrawer({ title: `${row.component_name} → ${row.facility}`, data: row })}
        />
      </Panel>
    </div>
  )
}
