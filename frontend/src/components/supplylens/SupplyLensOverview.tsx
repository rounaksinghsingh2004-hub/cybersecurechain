import { useEffect, useState } from 'react'
import { AlertTriangle, Box, Brain, CheckCircle2, FileCode, Network, RefreshCw, ShieldAlert } from 'lucide-react'
import { Metric, Panel } from '../common'
import { api } from '../../services/api'

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading SupplyLens data...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Unable to load</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

const SEV_COLOR: Record<string, string> = { CRITICAL: '#eb6969', HIGH: '#e8bd68', MEDIUM: '#42b7c2', LOW: '#5CE0C0' }

export function SupplyLensOverview() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api<any>('/api/supplylens/overview')
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} retry={load} />

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · SOFTWARE & SUPPLIER RISK</span>
          <h2>Risk Intelligence Overview</h2>
          <p>
            Software supply-chain visibility across {data.projects} software projects, {data.components} tracked
            components, and {data.suppliers} supplier relationships. All records are clearly labeled as{' '}
            <code style={{ color: '#5CE0C0', fontSize: 11 }}>SYNTHETIC_DEMO</code> data for this PBL prototype.
          </p>
        </div>
        <button className="quiet-button" onClick={load}><RefreshCw size={15} /> Refresh</button>
      </section>

      <section className="metric-grid">
        <Metric label="Software projects" value={data.projects} note="SBOM-tracked codebases" />
        <Metric label="Components" value={data.components} tone="teal" note="Tracked OSS & 3rd-party" />
        <Metric label="Open findings" value={data.open_findings} tone="red" note="Unresolved CVEs" />
        <Metric label="CISA KEV hits" value={data.kev_findings} tone="gold" note="Known exploited vulns" />
      </section>

      <section className="metric-grid" style={{ marginTop: 0 }}>
        <Metric label="Suppliers" value={data.suppliers} note="Registered vendor relationships" />
        <Metric label="Critical findings" value={data.critical_findings} tone="red" note="CVSS ≥ 9.0" />
        <Metric label="Cyber-physical maps" value={data.cyber_physical_mappings} tone="teal" note="Component→Facility links" />
        <Metric label="Avg component risk" value={`${data.average_component_risk}/100`} tone="gold" note="Deterministic score" />
      </section>

      <section className="dashboard-grid">
        <Panel title="Recent findings" action={<span className="mini-label">SYNTHETIC_DEMO</span>}>
          {data.recent_findings?.length === 0
            ? <div className="empty"><CheckCircle2 size={16} /> No findings recorded yet.</div>
            : <div className="timeline">
                {data.recent_findings.map((f: any) => (
                  <div key={f.id} className="event">
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: SEV_COLOR[f.severity] || '#888', flexShrink: 0 }} />
                    <div>
                      <b style={{ color: SEV_COLOR[f.severity] || '#ccc' }}>{f.vulnerability_id}</b>
                      <p style={{ marginTop: 2 }}>{f.summary || 'No summary available.'}</p>
                    </div>
                    <span style={{ fontSize: 10, color: '#555', whiteSpace: 'nowrap' }}>
                      {f.severity}{f.cisa_kev ? ' · KEV' : ''}
                    </span>
                  </div>
                ))}
              </div>
          }
        </Panel>

        <Panel title="Module summary">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, padding: '4px 0' }}>
            {[
              { icon: FileCode, label: 'SBOM Imports', desc: 'CycloneDX & SPDX JSON ingestion', link: '/supplylens/sbom-imports' },
              { icon: Box, label: 'Component Inventory', desc: `${data.components} tracked components with CVE findings`, link: '/supplylens/components' },
              { icon: ShieldAlert, label: 'Vulnerability Findings', desc: `${data.findings} total · ${data.critical_findings} critical`, link: '/supplylens/findings' },
              { icon: Network, label: 'Supplier Intelligence', desc: `${data.suppliers} registered supplier relationships`, link: '/supplylens/suppliers' },
              { icon: Brain, label: 'AI Risk Copilot', desc: 'Deterministic grounded risk analysis', link: '/supplylens/ai-copilot' },
            ].map(({ icon: Icon, label, desc, link }) => (
              <a key={label} href={link} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', textDecoration: 'none', color: 'inherit', padding: '8px 10px', borderRadius: 6, border: '1px solid #1e3240', background: '#0f1e2a' }}>
                <Icon size={18} color="#5CE0C0" style={{ marginTop: 2, flexShrink: 0 }} />
                <div>
                  <b style={{ display: 'block', fontSize: 13, color: '#e2eef2' }}>{label}</b>
                  <span style={{ fontSize: 11, color: '#6a8fa0' }}>{desc}</span>
                </div>
              </a>
            ))}
          </div>
        </Panel>
      </section>

      <div style={{ fontSize: 11, color: '#4a6070', padding: '8px 0', borderTop: '1px solid #1a2e3a', marginTop: 8 }}>
        ⚠ All SupplyLens records are clearly labeled <strong>SYNTHETIC_DEMO</strong> data generated for this B.Tech CSE (Cybersecurity) PBL prototype. No external systems were scanned or contacted.
      </div>
    </div>
  )
}
