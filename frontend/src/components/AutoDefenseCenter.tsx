import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, Cpu, Database, Eye, LockKeyhole, Play, RadioTower, RefreshCw, Server, Shield, ShieldAlert, ShieldCheck, Siren, Sliders, Terminal, Truck, Zap, ZapOff } from 'lucide-react'
import { api, post } from '../services/api'
import { useLiveStore } from '../stores/live-store'

interface AutoDefenseStatus {
  adversary_enabled: boolean
  mitigation_enabled: boolean
  speed: string
  current_campaign: any
  history: any[]
  metrics: {
    total_attacks: number
    total_detected: number
    total_mitigated: number
    mitigation_rate: number
    total_orders_protected: number
    total_financial_saved_inr: number
  }
}

export function AutoDefenseCenter() {
  const { activeCampaign, campaignHistory, events, connected } = useLiveStore()
  const [status, setStatus] = useState<AutoDefenseStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionBusy, setActionBusy] = useState(false)
  const [activeTab, setActiveTab] = useState<'arena' | 'packets' | 'playbooks'>('arena')

  const fetchStatus = () => {
    api<AutoDefenseStatus>('/api/cyber/auto-defense/status')
      .then(setStatus)
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchStatus()
    const timer = setInterval(fetchStatus, 3000)
    return () => clearInterval(timer)
  }, [])

  const toggleAdversary = async () => {
    setActionBusy(true)
    try {
      await post('/api/cyber/auto-defense/toggle-adversary')
      fetchStatus()
    } finally {
      setActionBusy(false)
    }
  }

  const toggleMitigation = async () => {
    setActionBusy(true)
    try {
      await post('/api/cyber/auto-defense/toggle-mitigation')
      fetchStatus()
    } finally {
      setActionBusy(false)
    }
  }

  const setSpeed = async (speed: string) => {
    await post('/api/cyber/auto-defense/set-speed', { speed })
    fetchStatus()
  }

  const triggerAttack = async () => {
    setActionBusy(true)
    try {
      await post('/api/cyber/auto-defense/trigger-campaign')
      fetchStatus()
    } finally {
      setActionBusy(false)
    }
  }

  const triggerDefense = async () => {
    setActionBusy(true)
    try {
      await post('/api/cyber/auto-defense/trigger-defense')
      fetchStatus()
    } finally {
      setActionBusy(false)
    }
  }

  const camp = activeCampaign || status?.current_campaign
  const metrics = status?.metrics || {
    total_attacks: 0,
    total_detected: 0,
    total_mitigated: 0,
    mitigation_rate: 100,
    total_orders_protected: 0,
    total_financial_saved_inr: 0,
  }

  const stage = camp?.stage || 'STANDBY'
  const isAttacking = stage === 'ATTACK_IN_PROGRESS'
  const isDetected = stage === 'ML_IDS_DETECTED'
  const isMitigated = stage === 'MITIGATED'

  // Extract recent packet events from store
  const packetEvents = events.filter(e => e.packet_features).slice(0, 10)

  return (
    <div className="auto-defense-root">
      {/* ── TOP CONTROL BAR ─────────────────────────────────────── */}
      <section className="auto-defense-header">
        <div>
          <div className="auto-badge-row">
            <span className={`live-pulse-badge ${connected ? 'active' : 'offline'}`}>
              <span className="dot" />
              {connected ? 'AUTONOMOUS CYBER DUEL ACTIVE' : 'CONNECTING TO SOAR...'}
            </span>
            <span className="ml-badge">
              <Cpu size={12} /> CIC-IDS2017 ML (99.09% ACCURACY)
            </span>
          </div>
          <h2>Self-Defending Supply Chain Digital Twin</h2>
          <p>
            An autonomous Red Team AI continuously tests the India logistics network while a real-time
            Machine Learning IDS detects malicious network flows and triggers automated SOAR micro-isolation and order rerouting.
          </p>
        </div>

        <div className="auto-controls-cluster">
          <div className="toggle-group">
            <button
              className={`auto-toggle-btn ${status?.adversary_enabled ? 'active-red' : ''}`}
              onClick={toggleAdversary}
              disabled={actionBusy}
            >
              <Siren size={14} />
              <span>Adversary AI: <strong>{status?.adversary_enabled ? 'ON' : 'OFF'}</strong></span>
            </button>
            <button
              className={`auto-toggle-btn ${status?.mitigation_enabled ? 'active-blue' : ''}`}
              onClick={toggleMitigation}
              disabled={actionBusy}
            >
              <ShieldCheck size={14} />
              <span>Auto-SOAR: <strong>{status?.mitigation_enabled ? 'ON' : 'OFF'}</strong></span>
            </button>
          </div>

          <div className="speed-pills">
            {(['fast', 'normal', 'relaxed'] as const).map(s => (
              <button
                key={s}
                className={`speed-pill ${status?.speed === s ? 'active' : ''}`}
                onClick={() => setSpeed(s)}
              >
                {s.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="manual-actions">
            <button className="trigger-attack-btn" onClick={triggerAttack} disabled={actionBusy}>
              <Zap size={13} /> Launch Attack Now
            </button>
            <button className="trigger-defend-btn" onClick={triggerDefense} disabled={actionBusy}>
              <Shield size={13} /> Trigger SOAR Defense
            </button>
          </div>
        </div>
      </section>

      {/* ── KPI METRICS CARDS ───────────────────────────────────── */}
      <section className="metric-grid">
        <div className="metric red">
          <span>Adversary Campaigns</span>
          <strong>{metrics.total_attacks}</strong>
          <small>Automated threat attempts</small>
        </div>
        <div className="metric cyan">
          <span>Real ML Detections</span>
          <strong>{metrics.total_detected}</strong>
          <small>CIC-IDS2017 Random Forest</small>
        </div>
        <div className="metric teal">
          <span>Auto-Mitigated by SOAR</span>
          <strong>{metrics.total_mitigated} ({metrics.mitigation_rate}%)</strong>
          <small>Zero human clicks required</small>
        </div>
        <div className="metric gold">
          <span>Disruption Averted</span>
          <strong>₹{(metrics.total_financial_saved_inr / 100000).toFixed(1)}L</strong>
          <small>{metrics.total_orders_protected} orders protected &amp; rerouted</small>
        </div>
      </section>

      {/* ── VISUAL RED VS BLUE INTERACTIVE PIPELINE ────────────── */}
      <div className="pipeline-card">
        <div className="pipeline-header">
          <span>REAL-TIME AUTONOMOUS BATTLE PIPELINE</span>
          <div className="stage-pill-box">
            <span className={`stage-indicator ${stage.toLowerCase()}`}>
              {stage === 'ATTACK_IN_PROGRESS' && '⚡ ADVERSARY INGRESS ACTIVE'}
              {stage === 'ML_IDS_DETECTED' && '🧠 IDS ML CLASSIFIED THREAT'}
              {stage === 'MITIGATED' && '🛡️ THREAT CONTAINED & RESTORED'}
              {stage === 'STANDBY' && '○ STANDBY — PATROLLING TWIN'}
            </span>
          </div>
        </div>

        <div className="pipeline-nodes">
          {/* Node 1: Adversary */}
          <div className={`pipe-node ${isAttacking ? 'node-attacking' : ''}`}>
            <div className="node-icon-circle red-glow">
              <Siren size={22} />
            </div>
            <div className="node-info">
              <span className="node-role">RED TEAM · ADVERSARY</span>
              <b>{camp?.adversary || 'APT-29 (CozyBear)'}</b>
              <small>{camp?.attack_vector || 'DDoS'}</small>
            </div>
          </div>

          <div className={`pipe-link ${isAttacking ? 'laser-beam' : ''}`}>
            <ArrowRight size={18} />
          </div>

          {/* Node 2: Network Traffic Stream */}
          <div className={`pipe-node ${isAttacking || isDetected ? 'node-traffic-active' : ''}`}>
            <div className="node-icon-circle amber-glow">
              <RadioTower size={22} />
            </div>
            <div className="node-info">
              <span className="node-role">PCAP TRAFFIC STREAM</span>
              <b>{camp?.target_asset_code || 'FC-JPR-01'}</b>
              <small>{camp?.scenario || 'OT_DISRUPTION'}</small>
            </div>
          </div>

          <div className={`pipe-link ${isDetected ? 'laser-beam' : ''}`}>
            <ArrowRight size={18} />
          </div>

          {/* Node 3: ML IDS Classifier */}
          <div className={`pipe-node ${isDetected ? 'node-ml-active' : ''}`}>
            <div className="node-icon-circle cyan-glow">
              <Cpu size={22} />
            </div>
            <div className="node-info">
              <span className="node-role">CIC-IDS2017 MODEL</span>
              <b>{camp?.attack_vector || 'Random Forest'}</b>
              <small>{camp?.detection_confidence ? `${(camp.detection_confidence * 100).toFixed(1)}% Conf` : 'Scanning flows'}</small>
            </div>
          </div>

          <div className={`pipe-link ${isMitigated ? 'laser-beam-green' : ''}`}>
            <ArrowRight size={18} />
          </div>

          {/* Node 4: Blue Team SOAR */}
          <div className={`pipe-node ${isMitigated ? 'node-soar-active' : ''}`}>
            <div className="node-icon-circle green-glow">
              <ShieldCheck size={22} />
            </div>
            <div className="node-info">
              <span className="node-role">BLUE TEAM · SOAR</span>
              <b>{camp?.playbook || 'SOAR Auto-Defender'}</b>
              <small>{isMitigated ? 'Mitigation Complete' : 'Awaiting triggers'}</small>
            </div>
          </div>

          <div className={`pipe-link ${isMitigated ? 'laser-beam-green' : ''}`}>
            <ArrowRight size={18} />
          </div>

          {/* Node 5: Digital Twin Continuity */}
          <div className={`pipe-node ${isMitigated ? 'node-twin-active' : ''}`}>
            <div className="node-icon-circle blue-glow">
              <Truck size={22} />
            </div>
            <div className="node-info">
              <span className="node-role">TWIN ORDER CONTINUITY</span>
              <b>{camp?.orders_rerouted ? `${camp.orders_rerouted} Orders Rerouted` : 'Normal Fulfillment'}</b>
              <small>0 SLA Violations</small>
            </div>
          </div>
        </div>
      </div>

      {/* ── TAB SELECTOR: DOSSIER vs PACKET INSPECTION vs PLAYBOOKS ── */}
      <div className="tabs" style={{ marginBottom: 14 }}>
        <button className={activeTab === 'arena' ? 'active' : ''} onClick={() => setActiveTab('arena')}>
          <ShieldAlert size={14} /> Active Threat Dossier &amp; SOAR Actions
        </button>
        <button className={activeTab === 'packets' ? 'active' : ''} onClick={() => setActiveTab('packets')}>
          <Terminal size={14} /> Live SOC Packet Inspection HUD (ML Scored)
        </button>
        <button className={activeTab === 'playbooks' ? 'active' : ''} onClick={() => setActiveTab('playbooks')}>
          <CheckCircle2 size={14} /> Automated Defense Playbooks Catalog
        </button>
      </div>

      {/* ── TAB 1: ACTIVE THREAT DOSSIER & SOAR ACTIONS ──────────── */}
      {activeTab === 'arena' && (
        <div className="dossier-layout">
          <div className="panel dossier-panel">
            <header>
              <h2>🎯 Active Campaign Intelligence Dossier</h2>
              <span className="mini-label">{camp?.id || 'AUTOCAMP-STANDBY'}</span>
            </header>
            <div className="dossier-body">
              {camp ? (
                <>
                  <div className="dossier-grid">
                    <div>
                      <span className="meta-lbl">Threat Actor</span>
                      <b className="threat-name">{camp.adversary}</b>
                      <small>{camp.adversary_origin} · {camp.adversary_tactic}</small>
                    </div>
                    <div>
                      <span className="meta-lbl">Target Digital Twin Node</span>
                      <b style={{ color: '#dce8ea' }}>{camp.facility_code} ({camp.facility_name})</b>
                      <small>Asset: {camp.target_asset_code} · {camp.target_asset_name}</small>
                    </div>
                    <div>
                      <span className="meta-lbl">Attack Vector (CIC-IDS2017)</span>
                      <b style={{ color: '#ef6b6b' }}>{camp.attack_vector}</b>
                      <small>{camp.description}</small>
                    </div>
                    <div>
                      <span className="meta-lbl">Digital Twin Operational Impact</span>
                      <b style={{ color: '#f0c26e' }}>{camp.orders_at_risk} Orders at Risk</b>
                      <small>Est. Revenue Threat: ₹{Number(camp.estimated_loss_inr).toLocaleString()}</small>
                    </div>
                  </div>

                  <div className="soar-steps-box">
                    <span className="soar-steps-title">
                      <ShieldCheck size={14} /> AUTONOMOUS SOAR PLAYBOOK: {camp.playbook}
                    </span>
                    <ol className="soar-step-list">
                      {camp.defensive_steps?.map((step: string, idx: number) => (
                        <li key={idx} className={isMitigated ? 'done' : isDetected ? 'in-progress' : ''}>
                          <CheckCircle2 size={14} />
                          <span>{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                </>
              ) : (
                <div className="empty">No campaign running. Click "Launch Attack Now" to test.</div>
              )}
            </div>
          </div>

          {/* Recent Resolutions Audit Trail */}
          <div className="panel history-panel">
            <header>
              <h2>🛡️ SOAR Neutralization Audit Log</h2>
              <span className="mini-label">RESOLVED THREATS</span>
            </header>
            <div className="audit-timeline">
              {(campaignHistory.length ? campaignHistory : status?.history || []).map((h: any, idx: number) => (
                <div className="audit-row" key={idx}>
                  <div className="audit-dot" />
                  <div className="audit-details">
                    <b>{h.adversary} ➔ {h.facility_code}</b>
                    <span className="audit-vector">Vector: {h.attack_vector} · {h.playbook}</span>
                    <div className="audit-stats">
                      <span className="tag-green">✓ Mitigated in ~2.8s</span>
                      <span className="tag-gold">{h.orders_rerouted || h.orders_at_risk} orders protected</span>
                    </div>
                  </div>
                  <time>{h.mitigated_at ? new Date(h.mitigated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Just now'}</time>
                </div>
              ))}
              {!campaignHistory.length && (!status?.history || !status.history.length) && (
                <div className="empty">No resolved campaigns yet. Active simulation in progress...</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: LIVE SOC PACKET INSPECTION HUD ────────────────── */}
      {activeTab === 'packets' && (
        <div className="panel packet-hud-panel">
          <header>
            <h2>🔍 Live Network Packet Inspection HUD (CIC-IDS2017 Real-Time Inference)</h2>
            <span className="mini-label">{connected ? 'STREAMING VIA WEBSOCKET' : 'OFFLINE'}</span>
          </header>
          <div className="packet-hud-body">
            <div className="packet-table-wrap">
              <table className="packet-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Facility</th>
                    <th>Asset</th>
                    <th>Dst Port</th>
                    <th>Flow Duration</th>
                    <th>Total Fwd Pkts</th>
                    <th>Fwd Len Mean</th>
                    <th>Flow Bytes/s</th>
                    <th>Classification (ML Output)</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {packetEvents.map((evt, idx) => {
                    const feat = evt.packet_features || {}
                    const isThreat = evt.is_attack
                    return (
                      <tr key={idx} className={isThreat ? 'row-threat' : 'row-benign'}>
                        <td>{new Date(evt.timestamp || '').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</td>
                        <td><strong>{evt.facility_code}</strong></td>
                        <td>{evt.asset_code}</td>
                        <td><code>{feat.dst_port ?? 80}</code></td>
                        <td>{((feat.flow_duration_us || 0) / 1000).toFixed(0)} ms</td>
                        <td>{feat.total_fwd_pkts ?? 0}</td>
                        <td>{feat.fwd_len_mean ?? 0} B</td>
                        <td>{Number(feat.flow_bytes_per_s || 0).toLocaleString()}</td>
                        <td>
                          <span className={`status ${isThreat ? 'danger' : 'success'}`}>
                            {evt.label}
                          </span>
                        </td>
                        <td>
                          <div className="conf-bar-wrap">
                            <div
                              className={`conf-bar ${isThreat ? 'threat' : 'benign'}`}
                              style={{ width: `${Math.min(100, (evt.confidence || 0) * 100)}%` }}
                            />
                            <span>{((evt.confidence || 0) * 100).toFixed(1)}%</span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                  {!packetEvents.length && (
                    <tr>
                      <td colSpan={10} style={{ textAlign: 'center', padding: 30, color: '#888' }}>
                        Awaiting network packet flow arrivals from live scanner...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 3: PLAYBOOK CATALOG ─────────────────────────────── */}
      {activeTab === 'playbooks' && (
        <div className="playbooks-grid">
          <div className="playbook-card">
            <div className="pb-header">
              <Shield size={18} color="#e77878" />
              <div>
                <b>PLAYBOOK_OT_CONTAINMENT</b>
                <span>Mitigates: DDoS, DoS Hulk, OT Disruption</span>
              </div>
            </div>
            <p>Triggers when malicious traffic spikes against industrial automation or conveyor PLC networks.</p>
            <ul>
              <li>1. Auto-activates edge rate-limiting firewall rules</li>
              <li>2. Isolates OT micro-boundary from IT network</li>
              <li>3. Reroutes pending orders to nearest regional distribution hub</li>
            </ul>
          </div>

          <div className="playbook-card">
            <div className="pb-header">
              <LockKeyhole size={18} color="#e8bd68" />
              <div>
                <b>PLAYBOOK_IDENTITY_LOCKDOWN</b>
                <span>Mitigates: SSH-Patator, FTP-Patator, Brute Force</span>
              </div>
            </div>
            <p>Triggers on anomalous credential authentication velocity detected by the Random Forest model.</p>
            <ul>
              <li>1. Terminates active session token and locks account</li>
              <li>2. Enforces step-up hardware token MFA</li>
              <li>3. Reverts privileges to baseline warehouse operator profile</li>
            </ul>
          </div>

          <div className="playbook-card">
            <div className="pb-header">
              <Server size={18} color="#42b7c2" />
              <div>
                <b>PLAYBOOK_WAF_INSPECTION</b>
                <span>Mitigates: Web Attack, SQL Injection, XSS</span>
              </div>
            </div>
            <p>Detects abnormal payload lengths and malicious query parameters targeting the Inventory API.</p>
            <ul>
              <li>1. Injects dynamic WAF signature into reverse proxy</li>
              <li>2. Freezes inventory mutation privileges to read-only sandbox</li>
              <li>3. Re-verifies stock reservation hashes with ledger checkpoint</li>
            </ul>
          </div>

          <div className="playbook-card">
            <div className="pb-header">
              <RadioTower size={18} color="#61c7a5" />
              <div>
                <b>PLAYBOOK_FLEET_INTEGRITY_SAFEGUARD</b>
                <span>Mitigates: GPS Spoofing, Jamming, Infiltration</span>
              </div>
            </div>
            <p>Protects in-transit delivery vehicles from coordinate tampering and signal disruption.</p>
            <ul>
              <li>1. Compares reported coordinates with cell tower multilateration</li>
              <li>2. Driver biometric check-in challenge</li>
              <li>3. Recalculates safe ETA and normalizes dispatch telemetry</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
