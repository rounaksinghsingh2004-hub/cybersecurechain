import { useState } from 'react'
import { AlertTriangle, ArrowRight, CheckCircle2, CirclePlay, Clock3, Database, PackageCheck, RefreshCw, ShieldAlert, ShieldCheck, Siren, Truck } from 'lucide-react'
import { Metric, Panel, Status } from '../common'
import { DataTable } from '../table'
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

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading scenario data...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

const SUPPLY_CHAIN_SCENARIOS = [
  {
    id: 'SUPPLIER_COMPROMISE',
    name: 'Upstream Supplier Package Tampering',
    desc: 'Malicious dependency injected into warehouse management system via compromised vendor artifact repository.',
    targetAsset: 'SRV-WMS-01',
    targetId: 1,
  },
  {
    id: 'DEPENDENCY_RCE',
    name: 'Log4Shell / Spring4Shell RCE in Core Services',
    desc: 'Unauthenticated remote code execution targeting logging component in order routing microservice.',
    targetAsset: 'SRV-ORDER-01',
    targetId: 2,
  },
  {
    id: 'OUTDATED_FIRMWARE_EXPLOIT',
    name: 'Robotics Control Firmware Disruption',
    desc: 'Vulnerable MQTT/SCADA broker leveraged to send invalid telemetry to automated guided vehicles and sorting arms.',
    targetAsset: 'PLC-SORT-BLR',
    targetId: 3,
  },
]

export function ScenarioLab() {
  const [scenarioId, setScenarioId] = useState('SUPPLIER_COMPROMISE')
  const [evaluating, setEvaluating] = useState(false)
  const [comparison, setComparison] = useState<any>(null)
  const [error, setError] = useState('')

  const activeScenario = SUPPLY_CHAIN_SCENARIOS.find(s => s.id === scenarioId) || SUPPLY_CHAIN_SCENARIOS[0]

  const runComparison = async () => {
    setEvaluating(true)
    setError('')
    try {
      const data = await api<any>(`/api/cyber/what-if?scenario=${activeScenario.id}&target_asset_id=${activeScenario.targetId}`)
      setComparison(data)
    } catch (e: any) {
      setError(e.message || 'Failed to simulate scenario')
    } finally {
      setEvaluating(false)
    }
  }

  const rows = comparison ? [
    { metric: 'Assets compromised', current: comparison.current.affected_assets, hardened: comparison.hardened.affected_assets },
    { metric: 'Orders affected', current: comparison.current.affected_orders, hardened: comparison.hardened.affected_orders },
    { metric: 'Shipments delayed', current: comparison.current.affected_shipments, hardened: comparison.hardened.affected_shipments },
    { metric: 'Operational downtime', current: `${comparison.current.downtime_minutes} min`, hardened: `${comparison.hardened.downtime_minutes} min` },
    { metric: 'Estimated revenue loss', current: `₹ ${Number(comparison.current.estimated_revenue_loss).toLocaleString()}`, hardened: `₹ ${Number(comparison.hardened.estimated_revenue_loss).toLocaleString()}` },
  ] : []

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · RESILIENCE SCENARIO LAB</span>
          <h2>Software Disruption Impact &amp; Mitigation Lab</h2>
          <p>
            Simulate how software dependency vulnerabilities and supplier compromises cascade into
            operational disruptions, and compare baseline exposure against a hardened control state.
          </p>
        </div>
        <span className="safety"><ShieldCheck size={14} /> SAFE WHAT-IF LAB</span>
      </section>

      <section className="dashboard-grid">
        <Panel title="Select Disruption Scenario">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {SUPPLY_CHAIN_SCENARIOS.map(s => (
              <div
                key={s.id}
                onClick={() => setScenarioId(s.id)}
                style={{
                  padding: 14,
                  borderRadius: 6,
                  cursor: 'pointer',
                  border: scenarioId === s.id ? '1px solid #5CE0C0' : '1px solid #1a3040',
                  background: scenarioId === s.id ? 'rgba(92, 224, 192, 0.08)' : '#0f1e2a',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <b style={{ color: scenarioId === s.id ? '#5CE0C0' : '#e2eef2', fontSize: 13 }}>{s.name}</b>
                  <Status value={scenarioId === s.id ? 'ACTIVE' : 'READY'} />
                </div>
                <p style={{ fontSize: 11, color: '#8da1ad', margin: '6px 0 0 0' }}>{s.desc}</p>
                <div style={{ fontSize: 10, color: '#6a8fa0', marginTop: 4 }}>
                  Target Node: <strong>{s.targetAsset}</strong>
                </div>
              </div>
            ))}

            <button
              className="launch-button"
              disabled={evaluating}
              onClick={runComparison}
              style={{ marginTop: 8 }}
            >
              <CirclePlay size={16} />
              {evaluating ? 'Simulating Propagation...' : `Evaluate Scenario: ${activeScenario.name}`}
            </button>
          </div>
        </Panel>

        <Panel title="Resilience Theory & Boundary">
          <div style={{ fontSize: 12, color: '#8da1ad', lineHeight: 1.8 }}>
            <p><strong style={{ color: '#5CE0C0' }}>Baseline vs Hardened:</strong> The digital twin projects two parallel execution trajectories from the same initial vulnerable component state.</p>
            <p><strong style={{ color: '#5CE0C0' }}>Hardening Controls:</strong> When controls like dependency quarantine, software bill of materials enforcement, network micro-segmentation, and automated patch rollouts are active, lateral movement is contained at the first boundary.</p>
            <p style={{ color: '#e8bd68', marginTop: 8 }}>
              All calculations run entirely in memory against synthetic digital twin state. No production services are touched.
            </p>
          </div>
        </Panel>
      </section>

      {error && <div className="error-box">{error}</div>}

      {comparison && (
        <>
          <section className="comparison">
            <Panel title="Current Environment (Vulnerable)">
              <div className="comparison-empty" style={{ borderColor: '#eb6969' }}>
                <ShieldAlert size={28} color="#eb6969" />
                <b style={{ color: '#eb6969', fontSize: 15 }}>
                  {comparison.current.affected_assets} Modeled Nodes Compromised
                </b>
                <p style={{ margin: '6px 0 0 0', color: '#c0d8e0' }}>
                  Boundary: {comparison.current.blocked_by || 'Uncontained lateral movement'}
                </p>
              </div>
            </Panel>

            <Panel title="Hardened Environment (SupplyLens Controls)">
              <div className="comparison-empty" style={{ borderColor: '#5CE0C0' }}>
                <ShieldCheck size={28} color="#5CE0C0" />
                <b style={{ color: '#5CE0C0', fontSize: 15 }}>
                  {comparison.hardened.affected_assets} Modeled Nodes Compromised
                </b>
                <p style={{ margin: '6px 0 0 0', color: '#c0d8e0' }}>
                  Boundary: <strong>{comparison.hardened.blocked_by || 'Preventive Quarantine Active'}</strong>
                </p>
              </div>
            </Panel>
          </section>

          <Panel title="Comparative Disruption Impact Table">
            <DataTable
              rows={rows}
              columns={[
                { key: 'metric', label: 'Business Impact Metric' },
                { key: 'current', label: 'Baseline Environment (Unmitigated)' },
                { key: 'hardened', label: 'Hardened Environment (Protected)' },
              ]}
            />
          </Panel>
        </>
      )}
    </div>
  )
}
