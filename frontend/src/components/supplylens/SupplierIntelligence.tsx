import { useState } from 'react'
import { AlertTriangle, CheckCircle2, Network, Plus, RefreshCw, ShieldCheck, UserCheck } from 'lucide-react'
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

function Loading() { return <div className="loading"><RefreshCw size={18} />Loading suppliers...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Error</b><p>{error}</p><button className="command-button" onClick={retry}>Retry</button></div> }

export function SupplierIntelligence() {
  const { setDrawer } = useAppStore()
  const { data: suppliers, loading, error, reload } = useData<any[]>('/api/supplylens/suppliers', [])
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({
    code: '',
    name: '',
    category: 'SOFTWARE',
    business_owner: '',
    criticality: 5,
    tier: 'TIER_1',
    contact_email: '',
    data_sensitivity: 'MEDIUM',
    notes: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.code || !form.name) return
    setSubmitting(true)
    try {
      await post('/api/supplylens/suppliers', form)
      setMsg(`Supplier ${form.name} created successfully.`)
      setShowAdd(false)
      setForm({
        code: '',
        name: '',
        category: 'SOFTWARE',
        business_owner: '',
        criticality: 5,
        tier: 'TIER_1',
        contact_email: '',
        data_sensitivity: 'MEDIUM',
        notes: '',
      })
      reload()
    } catch (err: any) {
      setMsg(`Error: ${err.message}`)
    } finally {
      setSubmitting(false)
      setTimeout(() => setMsg(''), 4000)
    }
  }

  if (loading && !suppliers.length) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const total = suppliers.length
  const tier1 = suppliers.filter(s => s.tier === 'TIER_1').length
  const highRisk = suppliers.filter(s => s.risk_level === 'HIGH' || s.risk_level === 'CRITICAL').length
  const assessed = suppliers.filter(s => s.assessment_status === 'APPROVED' || s.assessment_status === 'ACTIVE').length

  const columns = [
    { key: 'code', label: 'Supplier Code' },
    { key: 'name', label: 'Company Name' },
    { key: 'category', label: 'Category' },
    { key: 'tier', label: 'Tier', status: true },
    { key: 'criticality', label: 'Criticality' },
    { key: 'assessment_status', label: 'Assessment', status: true },
    { key: 'risk_level', label: 'Risk', status: true },
    { key: 'risk_score', label: 'Score' },
  ]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · THIRD-PARTY RISK</span>
          <h2>Supplier Intelligence &amp; Governance</h2>
          <p>
            Registry of third-party software, hardware, and logistics vendors. Connects suppliers to components,
            evaluates vendor posture, and tracks security assessments.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="command-button" onClick={() => setShowAdd(!showAdd)}>
            <Plus size={15} /> {showAdd ? 'Close Form' : 'Register Supplier'}
          </button>
          <button className="quiet-button" onClick={reload}>
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </section>

      <section className="metric-grid">
        <Metric label="Registered Suppliers" value={total} note="Active vendor records" />
        <Metric label="Tier 1 Critical Vendors" value={tier1} tone="red" note="Direct supply chain impact" />
        <Metric label="High/Critical Risk" value={highRisk} tone="gold" note="Requires risk mitigation" />
        <Metric label="Security Approved" value={assessed} tone="teal" note="Vetted against baseline" />
      </section>

      {msg && (
        <div style={{ padding: '10px 16px', background: msg.startsWith('Error') ? 'rgba(235,105,105,0.1)' : 'rgba(92,224,192,0.1)', border: `1px solid ${msg.startsWith('Error') ? '#eb6969' : '#5CE0C0'}`, borderRadius: 6, color: msg.startsWith('Error') ? '#eb6969' : '#5CE0C0', marginBottom: 12 }}>
          {msg}
        </div>
      )}

      {showAdd && (
        <Panel title="Register New Supplier">
          <form onSubmit={handleCreate} className="form-grid">
            <label>Supplier Code
              <input value={form.code} onChange={e => setForm({ ...form, code: e.target.value.toUpperCase() })} placeholder="e.g. SUP-ORACLE" required />
            </label>
            <label>Company Name
              <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Oracle Systems" required />
            </label>
            <label>Category
              <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                <option value="SOFTWARE">SOFTWARE</option>
                <option value="CLOUD_INFRA">CLOUD_INFRA</option>
                <option value="HARDWARE_OT">HARDWARE_OT</option>
                <option value="LOGISTICS">LOGISTICS</option>
              </select>
            </label>
            <label>Tier
              <select value={form.tier} onChange={e => setForm({ ...form, tier: e.target.value })}>
                <option value="TIER_1">TIER_1 (Mission Critical)</option>
                <option value="TIER_2">TIER_2 (Operational)</option>
                <option value="TIER_3">TIER_3 (Non-Critical)</option>
              </select>
            </label>
            <label>Criticality (1-10)
              <input type="number" min="1" max="10" value={form.criticality} onChange={e => setForm({ ...form, criticality: Number(e.target.value) })} />
            </label>
            <label>Data Sensitivity
              <select value={form.data_sensitivity} onChange={e => setForm({ ...form, data_sensitivity: e.target.value })}>
                <option value="HIGH">HIGH (PII/Financial)</option>
                <option value="MEDIUM">MEDIUM (Operational)</option>
                <option value="LOW">LOW (Public)</option>
              </select>
            </label>
            <label>Business Owner
              <input value={form.business_owner} onChange={e => setForm({ ...form, business_owner: e.target.value })} placeholder="e.g. Enterprise Security" />
            </label>
            <label>Contact Email
              <input type="email" value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} placeholder="security@vendor.com" />
            </label>
            <div style={{ gridColumn: '1 / -1', marginTop: 10 }}>
              <button type="submit" disabled={submitting} className="launch-button">
                {submitting ? 'Registering...' : 'Submit Supplier Registration'}
              </button>
            </div>
          </form>
        </Panel>
      )}

      <Panel title={`Supplier Register (${suppliers.length})`}>
        <DataTable
          rows={suppliers}
          columns={columns}
          onRowClick={row => setDrawer({ title: `${row.name} (${row.code})`, data: row })}
        />
      </Panel>

      <section className="dashboard-grid">
        <Panel title="Supplier Risk Breakdown">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {suppliers.map(s => (
              <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: '#0f1e2a', border: '1px solid #1a3040', borderRadius: 6 }}>
                <div>
                  <b style={{ color: '#e2eef2' }}>{s.name}</b>
                  <div style={{ fontSize: 11, color: '#6a8fa0', marginTop: 2 }}>
                    {s.code} · {s.category} · {s.tier}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <span style={{ fontSize: 11, color: '#8ca7af' }}>Risk Score: <b>{s.risk_score}</b></span>
                  <Status value={s.risk_level} />
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Governance Framework">
          <div style={{ fontSize: 12, color: '#8da1ad', lineHeight: 1.8 }}>
            <p><strong style={{ color: '#5CE0C0' }}>Tier 1 Suppliers:</strong> Vendors providing mission-critical core software (e.g. WMS, ERP, SCADA/PLC firmware). Subject to continuous vulnerability monitoring and mandatory SBOM submission.</p>
            <p><strong style={{ color: '#5CE0C0' }}>Evidence Grounding:</strong> Risk scores are deterministically derived from supplier assessment status, data sensitivity exposure, and associated open vulnerabilities.</p>
            <p style={{ marginTop: 8 }}><strong style={{ color: '#e8bd68' }}>Automated Recalculation:</strong> When a new critical CVE is detected in a supplier's component, the vendor risk score updates automatically.</p>
          </div>
        </Panel>
      </section>
    </div>
  )
}
