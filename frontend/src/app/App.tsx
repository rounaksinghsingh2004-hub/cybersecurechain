import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { AlertTriangle, ArrowRight, Bot, CheckCircle2, CirclePlay, Clock3, Database, LockKeyhole, PackageCheck, RadioTower, RefreshCw, Server, Shield, ShieldAlert, ShieldCheck, Siren, Truck, UserRound, Wifi, WifiOff, Zap } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EntityDrawer, Metric, Panel, Status } from '../components/common'
import { LiveFeed } from '../components/LiveFeed'
import { ThreatBanner } from '../components/ThreatBanner'
import { TwinMap } from '../components/map'
import { AutoDefenseCenter } from '../components/AutoDefenseCenter'
import { Shell } from '../components/shell'
import { DataTable } from '../components/table'
import { SupplyLensOverview } from '../components/supplylens/SupplyLensOverview'
import { SbomImports } from '../components/supplylens/SbomImports'
import { ComponentInventory } from '../components/supplylens/ComponentInventory'
import { FindingsView } from '../components/supplylens/FindingsView'
import { SupplierIntelligence } from '../components/supplylens/SupplierIntelligence'
import { ExposureMap } from '../components/supplylens/ExposureMap'
import { AICopilot } from '../components/supplylens/AICopilot'
import { ScenarioLab } from '../components/supplylens/ScenarioLab'
import { api, post, del } from '../services/api'
import { useAppStore } from '../stores/app-store'
import { useLiveStore } from '../stores/live-store'

type Twin = { metrics: Record<string, number>; facilities: any[]; relationships: any[]; recent_events: any[] }
type CyberOverview = { posture: number; critical_assets: number; high_risk_assets: number; active_incidents: number; external_connections: number; assets: any[] }

function useData<T>(path: string, fallback: T) { const [data, setData] = useState<T>(fallback); const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const reload = () => { setLoading(true); api<T>(path).then(setData).catch(e => setError(e.message)).finally(() => setLoading(false)) }; useEffect(reload, [path]); return { data, loading, error, reload } }
const title = (word: string) => word.split('-').map(v => v[0]?.toUpperCase() + v.slice(1)).join(' ')

function Overview() {
  const { data: twin, loading, error, reload } = useData<Twin>('/api/digital-twin', { metrics: {}, facilities: [], relationships: [], recent_events: [] }); const { setDrawer } = useAppStore()
  if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />
  const m = twin.metrics
  return <div className="page"><section className="page-intro"><div><span className="eyebrow">LIVE OPERATIONAL STATE</span><h2>Supply chain at a glance</h2><p>Every view references the same seeded operational state and event history.</p></div><button className="quiet-button" onClick={reload}><RefreshCw size={15} /> Refresh twin</button></section>
    <section className="metric-grid"><Metric label="Active orders" value={m.active_orders || 0} note="Across all fulfillment sites" /><Metric label="Inventory units" value={Number(m.inventory_units || 0).toLocaleString()} tone="teal" note="Available physical stock" /><Metric label="Shipments" value={m.shipments || 0} tone="gold" note="Modeled shipments" /><Metric label="Connected facilities" value={m.facilities || 0} tone="red" note="India network" /></section>
    <section className="dashboard-grid"><Panel title="Network Operations" action={<span className="legend"><i className="facility-dot" /> Facility <i className="vehicle-dot" /> Vehicle</span>} className="map-panel"><TwinMap facilities={twin.facilities} onSelect={facility => setDrawer({ title: facility.code, data: facility })} /></Panel><Activity events={twin.recent_events} /></section>
    <Panel title="Facility posture"><DataTable rows={twin.facilities} columns={[{ key: 'code', label: 'Facility' }, { key: 'type', label: 'Type' }, { key: 'city', label: 'Location' }, { key: 'status', label: 'Status', status: true }, { key: 'capacity', label: 'Capacity' }, { key: 'cyber_risk', label: 'Cyber risk' }]} onRowClick={row => setDrawer({ title: String(row.code), data: row })} /></Panel></div>
}

function Activity({ events }: { events: any[] }) { return <Panel title="Unified activity" action={<span className="mini-label">EVENT STREAM</span>} className="activity-panel"><div className="timeline">{events.map(event => <div className="event" key={event.id}><span className={`event-dot ${event.category.toLowerCase()}`} /><div><b>{event.type.replaceAll('_', ' ')}</b><p>{event.description}</p></div><time>{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time></div>)}</div></Panel> }

function ResourceTable({ resource, endpoint, columns }: { resource: string; endpoint: string; columns: any[] }) { const { data, loading, error, reload } = useData<any[]>(endpoint, []); const { setDrawer } = useAppStore(); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; return <div className="page"><section className="page-intro"><div><span className="eyebrow">OPERATIONAL REGISTER</span><h2>{resource}</h2><p>{data.length} records from the shared digital twin.</p></div></section><Panel title={`${resource} register`}><DataTable rows={data} columns={columns} onRowClick={row => setDrawer({ title: String(row.code || row.number || row.sku || row.id), data: row })} /></Panel></div> }

function Fleet() { const { data: map, loading, error, reload } = useData<any>('/api/digital-twin/map', { facilities: [], vehicles: [] }); const { setDrawer } = useAppStore(); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; const vehicles = map.vehicles.map((v: any) => ({ ...v, integrity: v.integrity || 'VERIFIED' })); return <div className="page"><section className="page-intro"><div><span className="eyebrow">FLEET TELEMETRY</span><h2>Vehicle position and GPS integrity</h2><p>Reported and actual location fields support safe GPS spoofing scenarios.</p></div></section><section className="dashboard-grid"><Panel title="Live fleet map" className="map-panel"><TwinMap facilities={map.facilities} vehicles={vehicles} onVehicleSelect={vehicle => setDrawer({ title: vehicle.code, data: vehicle })} /></Panel><Panel title="GPS integrity"><div className="callout"><ShieldCheck size={22} /><div><b>{vehicles.filter((v: any) => v.integrity === 'VERIFIED').length} verified location feeds</b><p>Vehicle GPS records are part of the operational twin, not a separate cyber dataset.</p></div></div></Panel></section><Panel title="Fleet register"><DataTable rows={vehicles} columns={[{ key: 'code', label: 'Vehicle' }, { key: 'driver', label: 'Driver' }, { key: 'status', label: 'Status', status: true }, { key: 'destination', label: 'Destination' }, { key: 'gps_integrity', label: 'GPS integrity', status: true }]} onRowClick={row => setDrawer({ title: String(row.code), data: row })} /></Panel></div> }

function Twin() { const { data, loading, error, reload } = useData<Twin>('/api/digital-twin', { metrics: {}, facilities: [], relationships: [], recent_events: [] }); const [mode, setMode] = useState('Combined'); const { setDrawer } = useAppStore(); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; return <div className="page twin-page"><section className="page-intro"><div><span className="eyebrow">DIGITAL TWIN</span><h2>Connected operational and cyber dependency model</h2><p>{data.relationships.length} modeled dependencies connect physical flow with cyber exposure.</p></div><div className="tabs">{['Physical', 'Logistics', 'Cyber', 'Combined'].map(tab => <button className={mode === tab ? 'active' : ''} onClick={() => setMode(tab)} key={tab}>{tab}</button>)}</div></section><Panel title={`${mode} network`} className="map-panel twin-map"><TwinMap facilities={data.facilities} onSelect={f => setDrawer({ title: f.code, data: f })} /></Panel><Panel title="Modeled dependencies"><div className="dependency-list">{data.relationships.map((edge, index) => <div key={index}><b>{edge.source}</b><ArrowRight size={15} /><b>{edge.target}</b><Status value={edge.type} /></div>)}</div></Panel></div> }

function SecurityOverview() { const { data, loading, error, reload } = useData<CyberOverview>('/api/cyber/overview', { posture: 0, critical_assets: 0, high_risk_assets: 0, active_incidents: 0, external_connections: 0, assets: [] }); const { setDrawer } = useAppStore(); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; const riskData = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(name => ({ name, value: data.assets.filter(a => a.risk_level === name).length })); return <div className="page"><section className="page-intro"><div><span className="eyebrow">CYBER STATE DERIVED FROM THE TWIN</span><h2>Security posture {data.posture}/100</h2><p>Exposure, likelihood, criticality, impact, vulnerabilities, and control state are calculated against modeled assets.</p></div><div className="posture"><Shield size={18} /><b>{data.posture}</b><span>POSTURE</span></div></section><section className="metric-grid"><Metric label="Critical assets" value={data.critical_assets} tone="red" note="Criticality >= 8" /><Metric label="High-risk assets" value={data.high_risk_assets} tone="gold" note="Risk score >= 61" /><Metric label="Active incidents" value={data.active_incidents} tone="red" note="Simulation-derived" /><Metric label="External connections" value={data.external_connections} tone="cyan" note="Attack surface" /></section><section className="dashboard-grid"><Panel title="Risk distribution" className="chart-panel"><ResponsiveContainer width="100%" height={240}><BarChart data={riskData}><CartesianGrid vertical={false} stroke="#29414e" /><XAxis dataKey="name" stroke="#8da1ad" tickLine={false} axisLine={false} /><YAxis stroke="#8da1ad" tickLine={false} axisLine={false} /><Tooltip /><Bar dataKey="value" radius={[3, 3, 0, 0]}>{riskData.map((entry, index) => <Cell key={index} fill={entry.name === 'CRITICAL' ? '#eb6969' : entry.name === 'HIGH' ? '#e8bd68' : '#42b7c2'} />)}</Bar></BarChart></ResponsiveContainer></Panel><Panel title="Control logic"><div className="control-summary"><p><ShieldCheck size={17} /> Controls change propagation. MFA reduces identity compromise; segmentation prevents IT-to-OT reach.</p><p><Database size={17} /> All Red Team actions operate only on synthetic snapshot state.</p></div></Panel></section><Panel title="Cyber asset register"><DataTable rows={data.assets} columns={[{ key: 'code', label: 'Asset' }, { key: 'name', label: 'Name' }, { key: 'type', label: 'Type' }, { key: 'facility', label: 'Facility' }, { key: 'risk_level', label: 'Risk', status: true }, { key: 'risk', label: 'Score' }]} onRowClick={row => setDrawer({ title: String(row.code), data: row })} /></Panel></div> }

function Simulation() {
  const { data: assets, loading, error, reload } = useData<any[]>('/api/cyber/assets', [])
  const [scenario, setScenario] = useState('ACCOUNT_COMPROMISE')
  const [asset, setAsset] = useState<number | undefined>()
  const [result, setResult] = useState<any>(null)
  const [busy, setBusy] = useState(false)
  const [revealedSteps, setRevealedSteps] = useState(0)
  // Live inject state
  const [injectFacility, setInjectFacility] = useState('')
  const [injectScenario, setInjectScenario] = useState('OT_DISRUPTION')
  const [injecting, setInjecting] = useState(false)
  const [injectStatus, setInjectStatus] = useState<string | null>(null)
  const { compromisedFacilities, connected } = useLiveStore()

  useEffect(() => {
    if (!result?.timeline?.length) { setRevealedSteps(0); return }
    setRevealedSteps(0)
    const timer = window.setInterval(() => setRevealedSteps(step => {
      if (step >= result.timeline.length) { window.clearInterval(timer); return step }
      return step + 1
    }), 560)
    return () => window.clearInterval(timer)
  }, [result])

  const launch = async () => {
    if (!asset) return; setBusy(true)
    try {
      const sim = await post<any>('/api/simulations', { scenario, target_asset_id: asset })
      const started = await post<any>(`/api/simulations/${sim.id}/start`)
      setResult(started.result)
    } catch (e: any) { setResult({ error: e.message }) }
    finally { setBusy(false); reload() }
  }

  const automaticAttack = async () => {
    setBusy(true)
    try {
      const simulation = await post<any>('/api/simulations/automatic-attack')
      setScenario(simulation.scenario); setResult(simulation.result)
    } catch (e: any) { setResult({ error: e.message }) }
    finally { setBusy(false); reload() }
  }

  const injectLive = async () => {
    if (!injectFacility) return
    setInjecting(true); setInjectStatus(null)
    try {
      const res = await post<any>('/api/live/inject', { scenario: injectScenario, facility_code: injectFacility, duration_seconds: 60 })
      setInjectStatus(`✓ Attack injected into ${injectFacility}. ML detection will fire within ~3 seconds.`)
    } catch (e: any) { setInjectStatus(`✗ ${e.message}`) }
    finally { setInjecting(false) }
  }

  const clearLive = async () => {
    if (!injectFacility) return
    try {
      await del(`/api/live/inject/${injectFacility}`)
      setInjectStatus(`✓ Attack cleared from ${injectFacility}. Recovery will begin.`)
    } catch (e: any) { setInjectStatus(`✗ ${e.message}`) }
  }

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} retry={reload} />

  const facilityOptions = [...new Set(assets.map((a: any) => a.facility).filter(Boolean))]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">RED TEAM · SYNTHETIC LAB</span>
          <h2>Launch a safe propagation simulation</h2>
          <p>All outcomes are evaluated against a launch-time snapshot. The primary operational twin is never changed.</p>
        </div>
        <span className="safety"><ShieldCheck size={14} /> SAFE ONLY</span>
      </section>
      <section className="simulation-layout">
        <Panel title="Scenario configuration">
          <div className="form-grid">
            <label>Scenario
              <select value={scenario} onChange={e => setScenario(e.target.value)}>
                {['ACCOUNT_COMPROMISE', 'INVENTORY_MANIPULATION', 'GPS_SPOOFING', 'QR_TAMPERING', 'SUPPLIER_COMPROMISE', 'IOT_SPOOFING', 'OT_DISRUPTION', 'RANSOMWARE_IMPACT'].map(v => <option key={v}>{v}</option>)}
              </select>
            </label>
            <label>Initial target
              <select value={asset || ''} onChange={e => setAsset(Number(e.target.value))}>
                <option value="">Select a modeled asset</option>
                {assets.map((a: any) => <option value={a.id} key={a.id}>{a.code} · {a.name}</option>)}
              </select>
            </label>
          </div>
          <div className="simulation-actions">
            <button disabled={!asset || busy} className="launch-button" onClick={launch}><CirclePlay size={17} />{busy ? 'Evaluating model...' : 'Launch selected simulation'}</button>
            <button disabled={busy} className="automatic-button" onClick={automaticAttack}><Siren size={17} />{busy ? 'Evaluating model...' : 'Simulate attack automatically'}</button>
          </div>
          <div className="safety-boundary"><ShieldCheck size={16} /> Automatic mode runs the reproducible ACCOUNT_COMPROMISE demo against the seeded warehouse account.</div>
        </Panel>

        {/* ── LIVE ATTACK INJECTION ─────────────────────────────────── */}
        <Panel title="🔴 Inject Live Real-Time Attack" className="inject-panel">
          <div className="inject-form">
            <div style={{ fontSize: 11, color: '#c49a9a', lineHeight: 1.5 }}>
              This directly injects malicious packet signatures into the live ML scanner. Assets will be compromised in real-time, incidents auto-created, and the sidebar feed will turn red within seconds.
              <span style={{ display: 'block', marginTop: 6, color: connected ? '#59cbb9' : '#888' }}>
                {connected ? '● WebSocket connected — live updates will appear instantly' : '○ WebSocket offline — connect backend first'}
              </span>
            </div>
            <label className="form-grid" style={{ padding: 0 }}>
              <span style={{ fontSize: 10, color: '#8ca7af', fontWeight: 650, textTransform: 'uppercase' }}>Target Facility</span>
              <select style={{ background: '#0a161a', border: '1px solid #4a1515', color: '#d6e4e6', borderRadius: 3, padding: 10, fontSize: 11 }}
                value={injectFacility} onChange={e => setInjectFacility(e.target.value)}>
                <option value="">Select facility to attack</option>
                {facilityOptions.map((f: any) => (
                  <option key={f} value={f}>{f} {compromisedFacilities.has(f) ? '⚠ COMPROMISED' : ''}</option>
                ))}
              </select>
            </label>
            <label className="form-grid" style={{ padding: 0 }}>
              <span style={{ fontSize: 10, color: '#8ca7af', fontWeight: 650, textTransform: 'uppercase' }}>Attack Scenario</span>
              <select style={{ background: '#0a161a', border: '1px solid #4a1515', color: '#d6e4e6', borderRadius: 3, padding: 10, fontSize: 11 }}
                value={injectScenario} onChange={e => setInjectScenario(e.target.value)}>
                {['OT_DISRUPTION', 'ACCOUNT_COMPROMISE', 'RANSOMWARE_IMPACT', 'IOT_SPOOFING', 'GPS_SPOOFING', 'INVENTORY_MANIPULATION', 'QR_TAMPERING', 'SUPPLIER_COMPROMISE'].map(v => <option key={v}>{v}</option>)}
              </select>
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="inject-btn" disabled={!injectFacility || injecting} onClick={injectLive} style={{ flex: 1 }}>
                <Zap size={14} />{injecting ? 'Injecting...' : 'Inject Attack (60s)'}
              </button>
              <button className="inject-btn" disabled={!injectFacility} onClick={clearLive}
                style={{ flex: 'none', width: 90, background: '#1a3a2a', borderColor: '#2d6b4a', color: '#90e0b8' }}>
                Clear
              </button>
            </div>
            {injectStatus && <div style={{ fontSize: 11, color: injectStatus.startsWith('✓') ? '#59cbb9' : '#eb6969', background: '#0d1b20', padding: 8, borderRadius: 3 }}>{injectStatus}</div>}
          </div>
        </Panel>

        <Panel title="Visual impact and findings">
          <SimulationResult result={result} revealedSteps={revealedSteps} />
        </Panel>
      </section>
    </div>
  )
}


function AttackNodeIcon({ asset, blocked }: { asset: string; blocked: boolean }) { if (blocked) return <LockKeyhole size={20} />; if (asset.startsWith('USR')) return <UserRound size={20} />; if (asset.startsWith('SRV') || asset.startsWith('DB')) return <Server size={20} />; if (asset.startsWith('RBT') || asset.startsWith('PLC')) return <Bot size={20} />; if (asset.startsWith('IOT') || asset.startsWith('GPS')) return <RadioTower size={20} />; return <Database size={20} /> }

function SimulationResult({ result, revealedSteps }: { result: any; revealedSteps: number }) { if (!result) return <div className="empty"><Clock3 size={18} />Choose a target or run the automatic demo.</div>; if (result.error) return <div className="error-box">{result.error}</div>; return <div className="impact"><div className="attack-picture"><header><div><span className="eyebrow">SIMULATED PROPAGATION</span><b>{result.initial_target} to modeled business impact</b></div><Status value={result.blocked_by ? 'CONTAINED' : 'UNCONTAINED'} /></header><div className="attack-lane">{result.timeline?.map((event: any, index: number) => <div className={`attack-node-wrap ${index < revealedSteps ? 'visible' : ''}`} key={`${event.asset}-${event.step}`}>{index > 0 && <div className={`attack-connector ${event.state === 'BLOCKED' ? 'blocked' : ''}`}><i /></div>}<div className={`attack-node ${event.state === 'BLOCKED' ? 'blocked' : ''}`}><div className="attack-node-icon"><AttackNodeIcon asset={event.asset} blocked={event.state === 'BLOCKED'} /></div><span>STEP {event.step}</span><b>{event.asset}</b><small>{event.state === 'BLOCKED' ? 'Control boundary' : event.name}</small></div></div>)}</div><div className="attack-legend"><span><i className="legend-entry" /> Initial access</span><span><i className="legend-spread" /> Synthetic propagation</span><span><i className="legend-stop" /> Containment boundary</span></div></div><div className="impact-tiles">{result.detected_attack && <div className="detected-attack-tile" style={{border: '1px solid #42b7c2', background: 'rgba(66, 183, 194, 0.1)'}}><RadioTower size={18} color="#42b7c2" /><span>IDS ML Detection<b style={{color: '#42b7c2'}}>{result.detected_attack}</b></span></div>}<div><PackageCheck size={18} /><span>Orders at risk<b>{result.affected_orders}</b></span></div><div><Truck size={18} /><span>Shipments delayed<b>{result.affected_shipments}</b></span></div><div><Clock3 size={18} /><span>Modeled downtime<b>{result.downtime_minutes} min</b></span></div><div><Database size={18} /><span>Estimated impact<b>Rs. {Number(result.total_estimated_impact).toLocaleString()}</b></span></div></div><div className="finding"><Siren size={16} /><div><b>Primary control gap: {result.primary_control_gap?.replaceAll('_', ' ')}</b><p>{result.root_cause}</p></div></div><div className="finding neutral"><ShieldCheck size={16} /><div><b>Accountability</b><p>{result.accountability?.finding} Affected component: {result.accountability?.affected_component}.</p></div></div><div className="improvements"><b>How to improve</b>{result.improvements?.map((improvement: string) => <span key={improvement}><CheckCircle2 size={13} />{improvement}</span>)}</div></div> }
function Controls() { const { data, loading, error, reload } = useData<any[]>('/api/cyber/controls', []); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; const toggle = async (id: number) => { await post(`/api/cyber/controls/${id}/toggle`); reload() }; return <div className="page"><section className="page-intro"><div><span className="eyebrow">BLUE TEAM PREVENTION</span><h2>Security controls</h2><p>These controls directly alter the safe simulation engine's reachability decisions.</p></div></section><div className="controls-grid">{data.map(control => <section className="control-card" key={control.id}><div><Status value={control.enabled ? 'ENABLED' : 'DISABLED'} /><h3>{control.name}</h3><p>{control.description}</p></div><button className={control.enabled ? 'toggle on' : 'toggle'} onClick={() => toggle(control.id)} aria-label={`Toggle ${control.name}`}><i /></button></section>)}</div></div> }

function Incidents() {
  const { data, loading, error, reload } = useData<any[]>('/api/cyber/incidents', []);
  const [actions, setActions] = useState<Record<number, string>>({});
  const [toast, setToast] = useState<{id: number; action: string} | null>(null);
  const [applying, setApplying] = useState<number | null>(null);
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  // Auto-refresh every 5s to pick up new ML-IDS-created incidents
  useEffect(() => {
    const t = setInterval(reload, 5000);
    return () => clearInterval(t);
  }, []);

  if (loading && !data.length) return <Loading />;
  if (error) return <ErrorState error={error} retry={reload} />;

  const getAction = (id: number) => actions[id] || 'ISOLATE_ASSET';
  const DONE = ['CONTAINED', 'RECOVERED', 'MITIGATED', 'RESOLVED'];
  // Instantly hide dismissed ones from active; show all resolved from API
  const active = data.filter(i => !DONE.includes(i.status) && !dismissed.has(i.id));
  const resolved = data.filter(i => DONE.includes(i.status));

  const respond = async (id: number) => {
    const a = getAction(id);
    setApplying(id);
    // Optimistically remove from active list immediately
    setDismissed(prev => new Set([...prev, id]));
    try {
      await post(`/api/incidents/${id}/respond`, { action: a });
      setToast({ id, action: a });
      setTimeout(() => setToast(null), 4000);
      reload();
    } finally { setApplying(null); }
  };

  const renderActions = (acts: any[]) => {
    if (!acts?.length) return <span style={{color:'#555'}}>No response actions yet</span>;
    return acts.map((a: any, idx: number) => {
      const label = typeof a === 'string' ? a : (a?.action || 'UNKNOWN');
      const note  = typeof a === 'object' ? a?.note : '';
      const ts    = typeof a === 'object' ? a?.timestamp : '';
      return (
        <span key={idx} title={[note, ts ? new Date(ts).toLocaleTimeString() : ''].filter(Boolean).join(' · ')}
          style={{display:'inline-block',background:'rgba(66,183,194,0.12)',border:'1px solid #42b7c2',
            borderRadius:4,padding:'1px 7px',margin:'2px 3px 2px 0',fontSize:11,color:'#42b7c2',cursor:'default'}}>
          {label}
        </span>
      );
    });
  };

  return (
    <div className="page">
      {toast && (
        <div style={{position:'fixed',top:20,right:20,zIndex:9999,background:'#0d2d1a',border:'1px solid #2ecc71',
          borderRadius:8,padding:'14px 20px',display:'flex',gap:12,alignItems:'center',
          boxShadow:'0 4px 24px rgba(0,0,0,0.5)',animation:'slideIn 0.3s ease'}}>
          <CheckCircle2 size={20} color="#2ecc71" />
          <div><b style={{color:'#2ecc71',display:'block'}}>Action Applied</b>
            <span style={{color:'#aaa',fontSize:13}}>{toast.action.replaceAll('_',' ')} → INC #{toast.id}</span></div>
        </div>
      )}

      <section className="page-intro">
        <div>
          <span className="eyebrow">BLUE TEAM RESPONSE</span>
          <h2>Incident operations</h2>
          <p>Live ML-IDS incidents appear automatically. Apply containment actions to resolve them.</p>
        </div>
        <button className="quiet-button" onClick={reload}><RefreshCw size={15} /> Refresh</button>
      </section>

      {/* ── ACTIVE INCIDENTS ── */}
      <Panel title={`Active incidents (${active.length})`}>
        {!active.length
          ? <div className="empty"><CheckCircle2 size={18} /> No active incidents. Launch an attack from Hacker Remote or the Simulation panel.</div>
          : <div className="incident-list">{active.map(i => (
              <div key={i.id} style={{border:'1px solid #eb6969',borderRadius:8,padding:16,marginBottom:12,background:'rgba(235,105,105,0.05)'}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:8}}>
                  <div>
                    <span style={{fontWeight:'bold',fontSize:15,color:'#eb6969'}}>{i.code}</span>
                    <span style={{marginLeft:8}}><Status value={i.severity} /></span>
                    <span style={{marginLeft:8}}><Status value={i.status} /></span>
                  </div>
                  <span style={{fontSize:11,color:'#666'}}>{i.facility}</span>
                </div>
                <p style={{margin:'0 0 8px',color:'#c8d9db'}}>{i.summary}</p>
                <div style={{marginBottom:10}}>
                  <small style={{color:'#888',fontSize:11}}>Actions applied: </small>
                  {renderActions(i.actions)}
                </div>
                <div style={{display:'flex',gap:8,alignItems:'center'}}>
                  <select value={getAction(i.id)} onChange={e => setActions(prev => ({...prev, [i.id]: e.target.value}))}
                    style={{background:'#0d1c21',border:'1px solid #2d4a52',color:'#c8d9db',borderRadius:4,padding:'6px 10px',fontSize:12,flex:1}}>
                    {['ISOLATE_ASSET','DISABLE_ACCOUNT','BLOCK_CONNECTION','ENABLE_MFA','APPLY_SEGMENTATION','REDUCE_PRIVILEGE','INCREASE_MONITORING','RESTORE_BACKUP'].map(v =>
                      <option key={v}>{v}</option>)}
                  </select>
                  <button className="command-button" onClick={() => respond(i.id)} disabled={applying === i.id}
                    style={{opacity: applying === i.id ? 0.6 : 1, whiteSpace:'nowrap'}}>
                    {applying === i.id ? 'Applying...' : 'Apply action'}
                  </button>
                </div>
              </div>
            ))}</div>
        }
      </Panel>

      {/* ── RESOLVED LOG ── */}
      {resolved.length > 0 && (
        <Panel title={`Resolved log (${resolved.length})`}>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {resolved.map(i => (
              <div key={i.id} style={{display:'flex',justifyContent:'space-between',alignItems:'center',
                padding:'10px 14px',background:'rgba(46,204,113,0.05)',border:'1px solid rgba(46,204,113,0.2)',borderRadius:6}}>
                <div>
                  <span style={{fontWeight:'bold',fontSize:13,color:'#aaa'}}>{i.code}</span>
                  <span style={{marginLeft:8,fontSize:12,color:'#666'}}>{i.facility} · {i.summary}</span>
                </div>
                <div style={{display:'flex',gap:6,alignItems:'center'}}>
                  {renderActions(i.actions)}
                  <Status value={i.status} />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      <style>{`@keyframes slideIn { from { opacity:0; transform:translateX(40px); } to { opacity:1; transform:translateX(0); } }`}</style>
    </div>
  );
}

function Timeline() { const { data, loading, error, reload } = useData<any[]>('/api/events', []); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; return <div className="page"><section className="page-intro"><div><span className="eyebrow">UNIFIED EVENT ENGINE</span><h2>Operational and cyber timeline</h2><p>Meaningful state changes create events that feed the audit trail, Digital Twin history, and simulation visualization.</p></div></section><Activity events={data} /></div> }

function WhatIf() { const { data, loading, error, reload } = useData<any>('/api/cyber/what-if?scenario=ACCOUNT_COMPROMISE&target_asset_id=1', null); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; const rows = [{ metric: 'Assets reached', current: data.current.affected_assets, hardened: data.hardened.affected_assets }, { metric: 'Orders affected', current: data.current.affected_orders, hardened: data.hardened.affected_orders }, { metric: 'Shipments delayed', current: data.current.affected_shipments, hardened: data.hardened.affected_shipments }, { metric: 'Downtime', current: `${data.current.downtime_minutes} min`, hardened: `${data.hardened.downtime_minutes} min` }, { metric: 'Revenue loss', current: `Rs. ${Number(data.current.estimated_revenue_loss).toLocaleString()}`, hardened: `Rs. ${Number(data.hardened.estimated_revenue_loss).toLocaleString()}` }]; return <div className="page"><section className="page-intro"><div><span className="eyebrow">RESILIENCE COMPARISON</span><h2>Current environment vs hardened environment</h2><p>The exact {data.scenario.replaceAll('_', ' ')} path is projected twice against the same synthetic target: {data.target}.</p></div></section><section className="comparison"><Panel title="Current environment"><div className="comparison-empty"><ShieldAlert size={26} /><b>{data.current.affected_assets} modeled assets reached</b><p>Boundary: {data.current.blocked_by || 'no active preventive boundary'}.</p></div></Panel><Panel title="Hardened environment"><div className="comparison-empty"><ShieldCheck size={26} /><b>{data.hardened.affected_assets} modeled assets reached</b><p>Boundary: {data.hardened.blocked_by || 'none'}.</p></div></Panel></section><Panel title="Actual simulation comparison"><DataTable rows={rows} columns={[{ key: 'metric', label: 'Impact metric' }, { key: 'current', label: 'Current environment' }, { key: 'hardened', label: 'Hardened environment' }]} /></Panel></div> }

function Resilience() { const { data: cyber, loading, error, reload } = useData<CyberOverview>('/api/cyber/overview', { posture: 0, critical_assets: 0, high_risk_assets: 0, active_incidents: 0, external_connections: 0, assets: [] }); const { data: controls } = useData<any[]>('/api/cyber/controls', []); if (loading) return <Loading />; if (error) return <ErrorState error={error} retry={reload} />; const enabled = controls.filter(control => control.enabled).length; const score = Math.min(100, Math.round(cyber.posture * .55 + (enabled / Math.max(1, controls.length)) * 45)); const factors = [{ factor: 'Detection capability', value: controls.some(c => c.code === 'MONITORING' && c.enabled) ? 85 : 45 }, { factor: 'Containment capability', value: controls.some(c => c.code === 'NETWORK_SEGMENTATION' && c.enabled) ? 90 : 40 }, { factor: 'Recovery capability', value: controls.some(c => c.code === 'BACKUP' && c.enabled) ? 88 : 35 }, { factor: 'Identity resilience', value: controls.some(c => c.code === 'MFA' && c.enabled) ? 90 : 30 }]; return <div className="page"><section className="page-intro"><div><span className="eyebrow">BLUE TEAM READINESS</span><h2>Resilience score {score}/100</h2><p>Derived from the live posture and active detection, containment, recovery, and identity controls.</p></div><div className="posture"><ShieldCheck size={18} /><b>{score}</b><span>RESILIENCE</span></div></section><Panel title="Contributing control factors"><DataTable rows={factors} columns={[{ key: 'factor', label: 'Factor' }, { key: 'value', label: 'Score' }]} /></Panel></div> }

function EntityDetails() { const { drawer } = useAppStore(); if (!drawer) return <div className="page"><section className="page-intro"><div><span className="eyebrow">ENTITY INSPECTION</span><h2>No entity selected</h2><p>Select a table row or map marker, then use Open full details.</p></div></section></div>; return <div className="page"><section className="page-intro"><div><span className="eyebrow">FULL ENTITY INSPECTION</span><h2>{drawer.title}</h2><p>Data shown here is the same record used by the corresponding operational or cyber view.</p></div></section><Panel title="Current modeled state"><div className="detail-grid">{Object.entries(drawer.data).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><b>{typeof value === 'object' ? JSON.stringify(value) : String(value ?? '—')}</b></div>)}</div></Panel></div> }

function Guide() {
  const timeline = [
    { week: '1–7 Aug', title: 'Architecture and workspace', detail: 'Defined the NEXORA digital-twin architecture, React/FastAPI structure, and Docker/local runtime.' },
    { week: '8–14 Aug', title: 'Relational operational twin', detail: 'Modeled facilities, products, inventory, orders, shipments, vehicles, employees, and operational assets with deterministic seed data.' },
    { week: '15–21 Aug', title: 'Operational workflows', detail: 'Implemented inventory reservation, validated order transitions, event recording, map projections, and facility-linked operations.' },
    { week: '22–28 Aug', title: 'Cyber resilience model', detail: 'Added derived cyber assets, transparent risk calculation, controls, attack paths, and safe simulation snapshots.' },
    { week: '29 Aug–4 Sep', title: 'Control tower and SOC', detail: 'Built Admin/Cyber navigation, maps, tables, drawers, timelines, Red Team simulation, and Blue Team response.' },
    { week: '5–8 Sep', title: 'Verification and documentation', detail: 'Added What-If comparison, domain tests, Docker setup, API documentation, and final integration checks.' },
    { week: '12 Sep', title: 'Real-time AI/ML Integration', detail: 'Replaced static mock rules with real-time Random Forest predictions trained on the genuine CIC-IDS2017 dataset.' },
    { week: '29 Sep', title: 'Autonomous Red vs Blue Cyber Engine', detail: 'Added self-defending digital twin: adversary AI launches real PCAP-verified attacks, CIC-IDS2017 ML detects them, SOAR auto-mitigates with order rerouting.' },
    { week: '6 Oct', title: '80-Feature Full-Scale ML Retraining', detail: 'Retrained Random Forest on 100% of CIC-IDS2017 (2.83M records) with all 14 attack classes plus Source Port & Protocol, achieving 99.78% multi-class accuracy.' },
    { week: '14 Oct', title: 'SupplyLens AI Module Integration', detail: 'Integrated software & supplier supply chain risk intelligence: CycloneDX & SPDX SBOM ingestion, live OSV.dev and CISA KEV enrichment, deterministic 6-factor risk scoring, cyber-physical propagation mapping, and zero-hallucination AI Risk Copilot.' }
  ]

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">ACADEMIC PBL PROJECT · MANIPAL UNIVERSITY JAIPUR</span>
          <h2>CyberSecureChain with SupplyLens AI</h2>
          <p>
            A cybersecurity-driven supply chain digital twin with AI-assisted software and supplier risk intelligence.
            Modeled for NEXORA Commerce & Logistics to connect physical operations, real-time intrusion detection, and upstream software dependency risk in one unified platform.
          </p>
        </div>
      </section>

      <section className="guide-grid">
        <Panel title="Project owner">
          <div className="about-copy">
            <b>Rounak Singh</b>
            <span>Registration: 2430040169</span>
            <span>B.Tech CSE (Cyber Security)</span>
            <span>Manipal University Jaipur</span>
          </div>
        </Panel>
        <Panel title="Faculty Guide & Mentor">
          <div className="about-copy">
            <b>Mr. Ravindra Kumar Saini</b>
            <span>Project Guide & Mentor</span>
            <span>Department of Computer Science & Engineering</span>
          </div>
        </Panel>
        <Panel title="Safety boundary">
          <div className="about-copy">
            <b>Safe Simulation Only</b>
            <span>No real scanning, credential use, malicious traffic, external targets, or unauthorized exploitation. All scenarios run in isolated in-memory digital twin snapshots.</span>
          </div>
        </Panel>
      </section>

      <Panel title="SupplyLens AI: Software & Supplier Risk Intelligence">
        <div className="about-copy">
          <b>End-to-End Cyber-Physical Dependency Modeling</b>
          <p style={{ marginTop: 6, lineHeight: 1.6 }}>
            Modern supply-chain disruption frequently originates in upstream open-source packages and third-party vendors.
            SupplyLens AI eliminates the barrier between software manifests and physical logistics through:
          </p>
          <ul style={{ paddingLeft: 20, marginTop: 8, lineHeight: 1.7 }}>
            <li>
              <b>SBOM Ingestion Engine:</b> Supports industry-standard CycloneDX 1.4+ and SPDX 2.3 JSON manifests with schema validation, PURL ecosystem inference, and dependency tree extraction.
            </li>
            <li>
              <b>Threat Intelligence & CISA KEV:</b> Live enrichment querying Google's OSV.dev database and the CISA Known Exploited Vulnerabilities catalog with in-memory caching and resilient offline fallback.
            </li>
            <li>
              <b>Deterministic Explainable Risk Engine:</b> Formulates a transparent 0–100 score across 6 weighted factors (Vulnerability Severity, Known Exploitation, Business Criticality, Reachability, Supplier Risk, and Data Sensitivity) normalized over available evidence.
            </li>
            <li>
              <b>Cyber-Physical Exposure Mapping:</b> Maps software packages directly to runtime microservices, host cyber assets, physical facilities (warehouses/hubs), and customer orders (<code>Package → Service → Host → Facility → Orders</code>).
            </li>
            <li>
              <b>Zero-Hallucination AI Copilot:</b> Grounded decision support providing human-readable explanations derived exclusively from stored digital-twin records without requiring external paid API keys.
            </li>
          </ul>
        </div>
      </Panel>

      <Panel title="Dynamic AI/ML Intrusion Detection Engine">
        <div className="about-copy">
          <b>Real-Time PCAP Classification on CIC-IDS2017 (2.83M Records)</b>
          <p style={{ marginTop: 5, lineHeight: 1.6 }}>
            The simulation and live feed engines rely on real-time Artificial Intelligence models trained on massive authentic datasets:
          </p>
          <ul style={{ paddingLeft: 20, marginTop: 8, lineHeight: 1.7 }}>
            <li>
              <b>Intrusion Detection System (IDS) Random Forest:</b> Trained on 100% of the authentic CIC-IDS2017 dataset across 80 extracted features. During simulations, the engine synthesizes real-time network flow characteristics based on the active scenario and predicts the attack class (DDoS, Bot, SQL Injection, Slowloris, etc.) with 99.78% multi-class accuracy.
            </li>
            <li>
              <b>Autonomous Adversary & SOAR Defense:</b> Continuous Red Team AI injects PCAP-verified attacks while Blue Team SOAR automatically triggers containment playbooks and reroutes active customer orders to resilient facilities.
            </li>
            <li>
              <b>Business Impact Regression:</b> Dynamically calculates estimated <code>downtime_minutes</code> and non-linear <code>estimated_revenue_loss</code> based on real-time asset telemetry and active containment controls.
            </li>
          </ul>
        </div>
      </Panel>

      <Panel title="How to demonstrate the platform">
        <ol className="guide-steps">
          <li><b>Admin View:</b> Inspect the relational digital twin—physical facilities on the India map, inventory batches, orders, shipments, and IoT/OT telemetry.</li>
          <li><b>Cyber View:</b> Inspect derived asset postures, live ML packet stream, attack surfaces, controls, and autonomous Red vs Blue operations.</li>
          <li><b>Live Attack & Response:</b> Launch a simulated attack from Simulation or Hacker Remote, watch the live feed turn red, and apply SOAR containment actions in Incidents.</li>
          <li><b>SupplyLens AI Ingestion & Threat Intelligence:</b> Open SBOM Imports to ingest a CycloneDX/SPDX manifest, explore Component Inventory, and click "OSV Enrich" for live threat data.</li>
          <li><b>Cyber-Physical Linkage & Scenario Lab:</b> Trace the software propagation chain in Exposure Map, evaluate baseline vs. hardened supply-chain impact in Scenario Lab, and query the AI Risk Copilot.</li>
          <li><b>What-If Comparison:</b> Compare baseline exposure against the hardened control environment to prove security ROI.</li>
        </ol>
      </Panel>

      <Panel title="Project Development Timeline & Milestones">
        <div className="project-timeline">
          {timeline.map(item => (
            <div key={item.week}>
              <span>{item.week}</span>
              <section>
                <b>{item.title}</b>
                <p>{item.detail}</p>
              </section>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  )
}

function CyberTable({ endpoint, name, columns }: { endpoint: string; name: string; columns: any[] }) { return <ResourceTable resource={name} endpoint={endpoint} columns={columns} /> }
function Loading() { return <div className="loading"><RefreshCw size={18} />Loading twin state...</div> }
function ErrorState({ error, retry }: { error: string; retry: () => void }) { return <div className="error-state"><AlertTriangle size={20} /><b>Unable to load this view</b><p>{error}</p><button className="command-button" onClick={retry}>Try again</button></div> }

function CyberSubNav({ tabs, active, onSelect }: { tabs: string[]; active: string; onSelect: (t: string) => void }) {
  const { connected } = useLiveStore();
  return (
    <div className="cyber-subnav">
      <div className="cyber-subnav-tabs">
        {tabs.map((t, idx) => (
          <button
            key={t}
            className={`cyber-subnav-tab ${active === t ? 'active' : ''}`}
            onClick={() => onSelect(t)}
          >
            <span className="cyber-subnav-idx">[{String(idx + 1).padStart(2, '0')}]</span>
            <span>{t}</span>
          </button>
        ))}
      </div>
      <div className="cyber-subnav-telemetry">
        <span className="cyber-tech-pill live-pulse">
          <span className="pulse-dot" />
          {connected ? 'SOC Telemetry · Live' : 'SOC Telemetry · Offline'}
        </span>
        <span className="cyber-tech-pill" style={{ color: '#5ad8e5', borderColor: '#1b4b57' }}>
          CIC-IDS2017 · 99.78%
        </span>
      </div>
    </div>
  );
}

function UnifiedResilienceAndControls() {
  const { data: cyber, loading: l1, error: e1, reload: reloadCyber } = useData<CyberOverview>('/api/cyber/overview', {
    posture: 0,
    critical_assets: 0,
    high_risk_assets: 0,
    active_incidents: 0,
    external_connections: 0,
    assets: [],
  });
  const { data: controls, loading: l2, error: e2, reload: reloadControls } = useData<any[]>('/api/cyber/controls', []);

  if ((l1 || l2) && !controls.length) return <Loading />;
  if (e1 || e2) return <ErrorState error={e1 || e2} retry={() => { reloadCyber(); reloadControls(); }} />;

  const enabled = controls.filter(control => control.enabled).length;
  const score = Math.min(100, Math.round(cyber.posture * 0.55 + (enabled / Math.max(1, controls.length)) * 45));
  const factors = [
    { factor: 'Detection capability', value: controls.some(c => c.code === 'MONITORING' && c.enabled) ? 85 : 45 },
    { factor: 'Containment capability', value: controls.some(c => c.code === 'NETWORK_SEGMENTATION' && c.enabled) ? 90 : 40 },
    { factor: 'Recovery capability', value: controls.some(c => c.code === 'BACKUP' && c.enabled) ? 88 : 35 },
    { factor: 'Identity resilience', value: controls.some(c => c.code === 'MFA' && c.enabled) ? 90 : 30 },
  ];

  const toggle = async (id: number) => {
    await post(`/api/cyber/controls/${id}/toggle`);
    reloadControls();
    reloadCyber();
  };

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">BLUE TEAM READINESS & PREVENTION CONTROLS</span>
          <h2>Security Controls & Preparedness Posture</h2>
          <p>Controls directly alter reachability decisions in simulation and constrain lateral movement. Readiness factor score is derived in real time.</p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div className="posture">
            <ShieldCheck size={18} />
            <b>{score}</b>
            <span>RESILIENCE</span>
          </div>
          <div className="posture" style={{ borderColor: '#235a66', background: '#0a1d22', color: '#68d4ea' }}>
            <Shield size={18} />
            <b>{cyber.posture}</b>
            <span>POSTURE</span>
          </div>
          <button className="quiet-button" onClick={() => { reloadCyber(); reloadControls(); }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </section>

      <div className="resilience-split-grid">
        <Panel title="Readiness Factor Score Matrix">
          <div style={{ padding: '4px 0' }}>
            {factors.map(f => (
              <div className="factor-row" key={f.factor}>
                <span className="factor-name">
                  <CheckCircle2 size={13} color={f.value >= 70 ? '#5ce0c0' : '#e8bd68'} />
                  {f.factor}
                </span>
                <div className="factor-meter">
                  <div className="factor-bar">
                    <div className="factor-fill" style={{ width: `${f.value}%`, background: f.value >= 70 ? '#5ce0c0' : '#e8bd68' }} />
                  </div>
                  <span className="factor-score-val" style={{ color: f.value >= 70 ? '#5ce0c0' : '#e8bd68' }}>{f.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title={`Active Preventive Security Controls (${enabled}/${controls.length} Active)`}>
          <div className="controls-grid" style={{ padding: 14, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
            {controls.map(control => (
              <section className="control-card" key={control.id} style={{ minHeight: 'auto' }}>
                <div>
                  <Status value={control.enabled ? 'ENABLED' : 'DISABLED'} />
                  <h3 style={{ fontSize: 13, margin: '10px 0 5px' }}>{control.name}</h3>
                  <p style={{ fontSize: 11, color: '#8aa2ab' }}>{control.description}</p>
                </div>
                <button
                  className={control.enabled ? 'toggle on' : 'toggle'}
                  onClick={() => toggle(control.id)}
                  aria-label={`Toggle ${control.name}`}
                >
                  <i />
                </button>
              </section>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function UnifiedIncidentOperations() {
  const { data, loading: l1, error: e1, reload: reloadIncidents } = useData<any[]>('/api/cyber/incidents', []);
  const { data: events, loading: l2, error: e2, reload: reloadEvents } = useData<any[]>('/api/events', []);
  const [actions, setActions] = useState<Record<number, string>>({});
  const [toast, setToast] = useState<{ id: number; action: string } | null>(null);
  const [applying, setApplying] = useState<number | null>(null);
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  useEffect(() => {
    const t = setInterval(() => {
      reloadIncidents();
      reloadEvents();
    }, 5000);
    return () => clearInterval(t);
  }, []);

  if ((l1 || l2) && !data.length && !events.length) return <Loading />;
  if (e1 || e2) return <ErrorState error={e1 || e2} retry={() => { reloadIncidents(); reloadEvents(); }} />;

  const getAction = (id: number) => actions[id] || 'ISOLATE_ASSET';
  const DONE = ['CONTAINED', 'RECOVERED', 'MITIGATED', 'RESOLVED'];
  const active = data.filter(i => !DONE.includes(i.status) && !dismissed.has(i.id));
  const resolved = data.filter(i => DONE.includes(i.status));

  const respond = async (id: number) => {
    const a = getAction(id);
    setApplying(id);
    setDismissed(prev => new Set([...prev, id]));
    try {
      await post(`/api/incidents/${id}/respond`, { action: a });
      setToast({ id, action: a });
      setTimeout(() => setToast(null), 4000);
      reloadIncidents();
      reloadEvents();
    } finally {
      setApplying(null);
    }
  };

  const renderActions = (acts: any[]) => {
    if (!acts?.length) return <span style={{ color: '#555' }}>No response actions yet</span>;
    return acts.map((a: any, idx: number) => {
      const label = typeof a === 'string' ? a : (a?.action || 'UNKNOWN');
      const note = typeof a === 'object' ? a?.note : '';
      const ts = typeof a === 'object' ? a?.timestamp : '';
      return (
        <span
          key={idx}
          title={[note, ts ? new Date(ts).toLocaleTimeString() : ''].filter(Boolean).join(' · ')}
          style={{
            display: 'inline-block',
            background: 'rgba(66,183,194,0.12)',
            border: '1px solid #42b7c2',
            borderRadius: 4,
            padding: '1px 7px',
            margin: '2px 3px 2px 0',
            fontSize: 11,
            color: '#42b7c2',
            cursor: 'default',
          }}
        >
          {label}
        </span>
      );
    });
  };

  return (
    <div className="page">
      {toast && (
        <div style={{
          position: 'fixed', top: 20, right: 20, zIndex: 9999, background: '#0d2d1a', border: '1px solid #2ecc71',
          borderRadius: 8, padding: '14px 20px', display: 'flex', gap: 12, alignItems: 'center',
          boxShadow: '0 4px 24px rgba(0,0,0,0.5)', animation: 'slideIn 0.3s ease'
        }}>
          <CheckCircle2 size={20} color="#2ecc71" />
          <div>
            <b style={{ color: '#2ecc71', display: 'block' }}>Action Applied</b>
            <span style={{ color: '#aaa', fontSize: 13 }}>{toast.action.replaceAll('_', ' ')} → INC #{toast.id}</span>
          </div>
        </div>
      )}

      <section className="page-intro">
        <div>
          <span className="eyebrow">BLUE TEAM RESPONSE · SOC INCIDENTS & FORENSICS</span>
          <h2>Incident Operations & Unified Audit Trail</h2>
          <p>Live ML-IDS incidents appear automatically. Apply containment playbooks to isolate nodes and audit state changes.</p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span className="cyber-tech-pill" style={{ color: active.length ? '#ff7676' : '#5ce0c0', borderColor: active.length ? '#7a2222' : '#1e4d44' }}>
            {active.length} ACTIVE INCIDENT{active.length === 1 ? '' : 'S'}
          </span>
          <button className="quiet-button" onClick={() => { reloadIncidents(); reloadEvents(); }}>
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </section>

      {/* Active Incidents */}
      <Panel title={`Active Incidents (${active.length})`}>
        {!active.length ? (
          <div className="empty">
            <CheckCircle2 size={18} /> No active incidents. Launch an attack from Hacker Remote or Simulation Lab to test detection.
          </div>
        ) : (
          <div className="incident-list">
            {active.map(i => (
              <div key={i.id} style={{ border: '1px solid #eb6969', borderRadius: 8, padding: 16, marginBottom: 12, background: 'rgba(235,105,105,0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div>
                    <span style={{ fontWeight: 'bold', fontSize: 15, color: '#eb6969' }}>{i.code}</span>
                    <span style={{ marginLeft: 8 }}><Status value={i.severity} /></span>
                    <span style={{ marginLeft: 8 }}><Status value={i.status} /></span>
                  </div>
                  <span style={{ fontSize: 11, color: '#666' }}>{i.facility}</span>
                </div>
                <p style={{ margin: '0 0 8px', color: '#c8d9db' }}>{i.summary}</p>
                <div style={{ marginBottom: 10 }}>
                  <small style={{ color: '#888', fontSize: 11 }}>Actions applied: </small>
                  {renderActions(i.actions)}
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <select
                    value={getAction(i.id)}
                    onChange={e => setActions(prev => ({ ...prev, [i.id]: e.target.value }))}
                    style={{ background: '#0d1c21', border: '1px solid #2d4a52', color: '#c8d9db', borderRadius: 4, padding: '6px 10px', fontSize: 12, flex: 1 }}
                  >
                    {['ISOLATE_ASSET', 'DISABLE_ACCOUNT', 'BLOCK_CONNECTION', 'ENABLE_MFA', 'APPLY_SEGMENTATION', 'REDUCE_PRIVILEGE', 'INCREASE_MONITORING', 'RESTORE_BACKUP'].map(v => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                  <button
                    className="command-button"
                    onClick={() => respond(i.id)}
                    disabled={applying === i.id}
                    style={{ opacity: applying === i.id ? 0.6 : 1, whiteSpace: 'nowrap' }}
                  >
                    {applying === i.id ? 'Applying...' : 'Apply action'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>

      {/* Resolved Log */}
      {resolved.length > 0 && (
        <Panel title={`Resolved Log (${resolved.length})`}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {resolved.map(i => (
              <div key={i.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(46,204,113,0.05)', border: '1px solid rgba(46,204,113,0.2)', borderRadius: 6 }}>
                <div>
                  <span style={{ fontWeight: 'bold', fontSize: 13, color: '#aaa' }}>{i.code}</span>
                  <span style={{ marginLeft: 8, fontSize: 12, color: '#666' }}>{i.facility} · {i.summary}</span>
                </div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  {renderActions(i.actions)}
                  <Status value={i.status} />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Unified Forensic Activity Audit */}
      <Panel title="Forensic Event Stream">
        <Activity events={events} />
      </Panel>
      <style>{`@keyframes slideIn { from { opacity:0; transform:translateX(40px); } to { opacity:1; transform:translateX(0); } }`}</style>
    </div>
  );
}

function UnifiedHostAttackSurface() {
  const { data: surface, loading: l1, error: e1, reload: reloadSurface } = useData<any[]>('/api/cyber/attack-surface', []);
  const { data: paths, loading: l2, error: e2, reload: reloadPaths } = useData<any[]>('/api/cyber/assets', []);
  const { setDrawer } = useAppStore();

  if ((l1 || l2) && !surface.length && !paths.length) return <Loading />;
  if (e1 || e2) return <ErrorState error={e1 || e2} retry={() => { reloadSurface(); reloadPaths(); }} />;

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SURFACE RECONNAISSANCE & LATERAL MOVEMENT</span>
          <h2>Host Attack Surface & Lateral Propagation Paths</h2>
          <p>Catalog of reachable network assets, exposure types, and traversal weaknesses mapped across the digital twin infrastructure.</p>
        </div>
        <button className="quiet-button" onClick={() => { reloadSurface(); reloadPaths(); }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </section>

      <div style={{ display: 'grid', gap: 16 }}>
        <Panel title={`Reachable Attack Surface Assets (${surface.length})`}>
          <DataTable
            rows={surface}
            columns={[
              { key: 'code', label: 'Asset' },
              { key: 'name', label: 'Name' },
              { key: 'type', label: 'Surface' },
              { key: 'facility', label: 'Facility' },
              { key: 'risk_level', label: 'Risk', status: true }
            ]}
            onRowClick={row => setDrawer({ title: String(row.code), data: row })}
          />
        </Panel>

        <Panel title={`Lateral Propagation Paths & Vulnerability Profiles (${paths.length})`}>
          <DataTable
            rows={paths}
            columns={[
              { key: 'code', label: 'Source asset' },
              { key: 'facility', label: 'Facility' },
              { key: 'vulnerabilities', label: 'Weaknesses' },
              { key: 'controls', label: 'Controls' }
            ]}
            onRowClick={row => setDrawer({ title: String(row.code), data: row })}
          />
        </Panel>
      </div>
    </div>
  );
}

function CommandCenter({ initialTab = 'Enterprise Cyber Posture' }: { initialTab?: string }) {
  const [tab, setTab] = useState(initialTab);
  const tabs = ['Enterprise Cyber Posture', 'Software Supply Chain Posture', 'Controls & Resilience', 'Incident Operations & Audit'];

  return (
    <div>
      <CyberSubNav tabs={tabs} active={tab} onSelect={setTab} />
      {tab === 'Enterprise Cyber Posture' && <SecurityOverview />}
      {tab === 'Software Supply Chain Posture' && <SupplyLensOverview />}
      {tab === 'Controls & Resilience' && <UnifiedResilienceAndControls />}
      {tab === 'Incident Operations & Audit' && <UnifiedIncidentOperations />}
    </div>
  );
}

function UnifiedVulnerabilities({ initialTab = 'Software & Package CVEs' }: { initialTab?: string }) {
  const [tab, setTab] = useState(initialTab);
  const tabs = ['Software & Package CVEs', 'Host & Infrastructure Weaknesses'];

  return (
    <div>
      <CyberSubNav tabs={tabs} active={tab} onSelect={setTab} />
      {tab === 'Software & Package CVEs' && <FindingsView />}
      {tab === 'Host & Infrastructure Weaknesses' && (
        <CyberTable
          name="Host Vulnerabilities"
          endpoint="/api/cyber/vulnerabilities"
          columns={[
            { key: 'vulnerability', label: 'Vulnerability' },
            { key: 'asset_name', label: 'Affected asset' },
            { key: 'facility', label: 'Facility' },
            { key: 'severity', label: 'Severity', status: true },
            { key: 'recommended_control', label: 'Recommended control' }
          ]}
        />
      )}
    </div>
  );
}

function UnifiedAttackSurface({ initialTab = 'Cyber-Physical Exposure Map' }: { initialTab?: string }) {
  const [tab, setTab] = useState(initialTab);
  const tabs = ['Cyber-Physical Exposure Map', 'Host Attack Surface & Lateral Paths'];

  return (
    <div>
      <CyberSubNav tabs={tabs} active={tab} onSelect={setTab} />
      {tab === 'Cyber-Physical Exposure Map' && <ExposureMap />}
      {tab === 'Host Attack Surface & Lateral Paths' && <UnifiedHostAttackSurface />}
    </div>
  );
}

function UnifiedSimulation({ initialTab = 'Supply Chain Scenario Lab' }: { initialTab?: string }) {
  const [tab, setTab] = useState(initialTab);
  const tabs = ['Supply Chain Scenario Lab', 'What-If Facility Resilience', 'Direct Disruption Stress Test'];

  return (
    <div>
      <CyberSubNav tabs={tabs} active={tab} onSelect={setTab} />
      {tab === 'Supply Chain Scenario Lab' && <ScenarioLab />}
      {tab === 'What-If Facility Resilience' && <WhatIf />}
      {tab === 'Direct Disruption Stress Test' && <Simulation />}
    </div>
  );
}

function UnifiedInventory({ initialTab = 'Software Components (SBOM)' }: { initialTab?: string }) {
  const [tab, setTab] = useState(initialTab);
  const tabs = ['Software Components (SBOM)', 'Supplier Intelligence Register', 'Import SBOM Manifests'];

  return (
    <div>
      <CyberSubNav tabs={tabs} active={tab} onSelect={setTab} />
      {tab === 'Software Components (SBOM)' && <ComponentInventory />}
      {tab === 'Supplier Intelligence Register' && <SupplierIntelligence />}
      {tab === 'Import SBOM Manifests' && <SbomImports />}
    </div>
  );
}

function RoutedApp() {
  const location = useLocation();
  const { view, setView } = useAppStore();
  const parts = location.pathname.split('/').filter(Boolean);
  const activeView = parts[0] === 'admin' ? 'admin' : 'cyber';
  useEffect(() => setView(activeView), [activeView, setView]);
  const page = parts[0] === 'guide' ? 'guide' : parts[0] === 'details' ? 'details' : parts[1] || (activeView === 'admin' ? 'overview' : 'command-center');

  const component = useMemo(() => {
    if (page === 'guide') return <Guide />;
    if (page === 'details') return <EntityDetails />;

    if (activeView === 'admin') {
      if (page === 'overview') return <Overview />;
      if (page === 'fleet') return <Fleet />;
      if (page === 'digital-twin' || page === 'supply-chain') return <Twin />;
      const tables: Record<string, [string, string, any[]]> = {
        facilities: ['Facilities', '/api/facilities', [{ key: 'code', label: 'Facility' }, { key: 'type', label: 'Type' }, { key: 'city', label: 'Location' }, { key: 'status', label: 'Status', status: true }, { key: 'capacity', label: 'Capacity' }]],
        inventory: ['Inventory', '/api/inventory', [{ key: 'sku', label: 'SKU' }, { key: 'product', label: 'Product' }, { key: 'facility', label: 'Facility' }, { key: 'available', label: 'Available' }, { key: 'reserved', label: 'Reserved' }, { key: 'quarantined', label: 'Quarantined' }]],
        products: ['Products', '/api/products', [{ key: 'sku', label: 'SKU' }, { key: 'name', label: 'Product' }, { key: 'category', label: 'Category' }, { key: 'supplier', label: 'Supplier' }, { key: 'factory', label: 'Factory' }]],
        orders: ['Orders', '/api/orders', [{ key: 'number', label: 'Order' }, { key: 'customer', label: 'Customer' }, { key: 'origin', label: 'Origin' }, { key: 'destination', label: 'Destination' }, { key: 'status', label: 'Status', status: true }, { key: 'cyber_status', label: 'Cyber status', status: true }]],
        shipments: ['Shipments', '/api/shipments', [{ key: 'code', label: 'Shipment' }, { key: 'order', label: 'Order' }, { key: 'vehicle', label: 'Vehicle' }, { key: 'destination', label: 'Destination' }, { key: 'status', label: 'Status', status: true }, { key: 'integrity', label: 'Integrity', status: true }]],
        employees: ['Employees', '/api/employees', [{ key: 'code', label: 'Employee' }, { key: 'name', label: 'Name' }, { key: 'facility', label: 'Facility' }, { key: 'role', label: 'Role' }, { key: 'mfa', label: 'MFA', status: true }, { key: 'account_status', label: 'Account', status: true }]],
        'machines-&-robots': ['Machines & Robots', '/api/machines', [{ key: 'code', label: 'Asset' }, { key: 'name', label: 'Name' }, { key: 'facility', label: 'Facility' }, { key: 'zone', label: 'Zone' }, { key: 'criticality', label: 'Criticality' }, { key: 'cyber_status', label: 'Cyber', status: true }]],
        'iot-&-ot': ['IoT & OT', '/api/iot', [{ key: 'code', label: 'Asset' }, { key: 'name', label: 'Name' }, { key: 'facility', label: 'Facility' }, { key: 'zone', label: 'Zone' }, { key: 'network', label: 'Network' }, { key: 'cyber_status', label: 'Cyber', status: true }]],
        assets: ['Operational assets', '/api/cyber/assets', [{ key: 'code', label: 'Asset' }, { key: 'name', label: 'Name' }, { key: 'type', label: 'Type' }, { key: 'facility', label: 'Facility' }, { key: 'risk_level', label: 'Cyber risk', status: true }]]
      };
      const target = tables[page];
      return target ? <ResourceTable resource={target[0]} endpoint={target[1]} columns={target[2]} /> : <Overview />;
    }

    // 1. Auto Defense
    if (page === 'auto-defense') return <AutoDefenseCenter />;

    // 2. Command Center (Executive Security & Supply Chain Overview)
    if (page === 'command-center' || page === 'overview' || page === 'security-overview') {
      return <CommandCenter initialTab="Enterprise Cyber Posture" />;
    }
    if (page === 'sl-overview' || page === 'supplylens') {
      return <CommandCenter initialTab="Software Supply Chain Posture" />;
    }
    if (page === 'controls' || page === 'resilience' || page === 'risk') {
      return <CommandCenter initialTab="Controls & Resilience" />;
    }
    if (page === 'incidents' || page === 'timeline') {
      return <CommandCenter initialTab="Incident Operations & Audit" />;
    }

    // 3. Vulnerability & Finding Triage
    if (page === 'vulnerabilities') {
      return <UnifiedVulnerabilities initialTab="Host & Infrastructure Weaknesses" />;
    }
    if (page === 'findings') {
      return <UnifiedVulnerabilities initialTab="Software & Package CVEs" />;
    }

    // 4. Attack Surface & Exposure
    if (page === 'exposure' || page === 'exposure-map') {
      return <UnifiedAttackSurface initialTab="Cyber-Physical Exposure Map" />;
    }
    if (page === 'attack-surface' || page === 'attack-paths') {
      return <UnifiedAttackSurface initialTab="Host Attack Surface & Lateral Paths" />;
    }

    // 5. Simulation & Scenario Lab
    if (page === 'simulation-lab' || page === 'scenario-lab') {
      return <UnifiedSimulation initialTab="Supply Chain Scenario Lab" />;
    }
    if (page === 'what-if') {
      return <UnifiedSimulation initialTab="What-If Facility Resilience" />;
    }
    if (page === 'simulation') {
      return <UnifiedSimulation initialTab="Direct Disruption Stress Test" />;
    }

    // 6. Software & Supplier Inventory
    if (page === 'inventory' || page === 'components') {
      return <UnifiedInventory initialTab="Software Components (SBOM)" />;
    }
    if (page === 'suppliers') {
      return <UnifiedInventory initialTab="Supplier Intelligence Register" />;
    }
    if (page === 'sbom-imports') {
      return <UnifiedInventory initialTab="Import SBOM Manifests" />;
    }

    // 7. AI Risk Copilot
    if (page === 'ai-copilot') return <AICopilot />;

    return <CommandCenter initialTab="Enterprise Cyber Posture" />;
  }, [activeView, page]);

  return <Shell>{component}<EntityDrawer /></Shell>;
}

import { HackerRemote } from '../components/HackerRemote'

export function App() { return <BrowserRouter><Routes><Route path="/hacker-remote" element={<HackerRemote />} /><Route path="/*" element={<RoutedApp />} /><Route path="/" element={<Navigate to="/admin/overview" replace />} /></Routes></BrowserRouter> }
