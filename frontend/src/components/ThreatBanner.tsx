import { useState, useEffect } from 'react'
import { AlertTriangle, X, ShieldCheck, Zap, Skull, Database, ServerCrash, Bug } from 'lucide-react'
import { useLiveStore } from '../stores/live-store'
import { useAppStore } from '../stores/app-store'
import { useNavigate } from 'react-router-dom'

const SCENARIO_META: Record<string, { label: string; detail: string; color: string; Icon: any }> = {
  OT_DISRUPTION:        { label: 'DDoS Attack — OT Disruption',        detail: 'Flooding OT/PLC network. Orders freezing. Facility offline.',        color: '#ffffff', Icon: ServerCrash },
  DATABASE_EXFILTRATION:{ label: 'SQL Injection — Data Exfiltration',   detail: 'Attacker querying customer DB. Records being exfiltrated.',          color: '#2ecc71', Icon: Database   },
  RANSOMWARE_IMPACT:    { label: 'Malware — Ransomware Deployed',       detail: 'LockBit 3.0 encrypting supply chain files. Systems locking down.',   color: '#ff3333', Icon: Bug        },
}

export function ThreatBanner() {
  const { alerts, activeCampaign } = useLiveStore()
  const { view } = useAppStore()
  const [dismissed, setDismissed] = useState<string[]>([])
  const [campaignDismissed, setCampaignDismissed] = useState<string | null>(null)
  const navigate = useNavigate()

  const active = alerts.find(a => a.incident_code && !dismissed.includes(a.incident_code ?? ''))

  // Campaign popup — show when a new active campaign comes in
  const campScenario = activeCampaign?.stage !== 'MITIGATED' ? activeCampaign?.scenario : null
  const campKey = activeCampaign?.id ?? activeCampaign?.scenario
  const showCampaignPopup = campScenario && campKey !== campaignDismissed
  const campMeta = campScenario ? (SCENARIO_META[campScenario] ?? {
    label: 'APT Attack — Advanced Persistent Threat',
    detail: 'Unknown adversary performing lateral movement across supply chain nodes.',
    color: '#f39c12',
    Icon: Skull,
  }) : null

  // Auto-dismiss campaign popup after 30 seconds
  useEffect(() => {
    if (!showCampaignPopup) return
    const t = setTimeout(() => setCampaignDismissed(campKey), 30000)
    return () => clearTimeout(t)
  }, [campKey, showCampaignPopup])

  // Reset dismiss when campaign clears
  useEffect(() => {
    if (!campScenario) setCampaignDismissed(null)
  }, [campScenario])

  if (view !== 'cyber') return null

  const dismiss = () => {
    if (active?.incident_code) setDismissed(d => [...d, active.incident_code!])
  }
  const respond = () => { dismiss(); navigate('/cyber/incidents') }

  return (
    <>
      {/* ML IDS Attack Banner */}
      {active && (
        <div className="threat-banner">
          <div className="threat-banner-icon"><AlertTriangle size={18} /></div>
          <div className="threat-banner-body">
            <b>LIVE ATTACK DETECTED — {active.label}</b>
            <span>
              Facility <strong>{active.facility_code}</strong> · Asset <strong>{active.asset_code}</strong> ·
              Confidence <strong>{active.confidence !== undefined ? (active.confidence * 100).toFixed(1) : '?'}%</strong>
              {active.incident_code && <> · Incident <strong>{active.incident_code}</strong></>}
              {active.auto_responded && <span className="threat-banner-auto"> · Auto-isolated <ShieldCheck size={12} /></span>}
            </span>
          </div>
          <div className="threat-banner-actions">
            <button className="threat-respond-btn" onClick={respond}><Zap size={13} /> Respond Now</button>
            <button className="threat-dismiss-btn" onClick={dismiss}><X size={14} /></button>
          </div>
        </div>
      )}

      {/* Campaign Popup — fixed bottom-right, cyber-view notification */}
      {showCampaignPopup && campMeta && (
        <div style={{
          position: 'fixed', bottom: 28, right: 28, zIndex: 99999,
          background: '#0f1923', border: `2px solid ${campMeta.color}`,
          borderRadius: 12, padding: '18px 22px', maxWidth: 360,
          boxShadow: `0 0 32px ${campMeta.color}55`,
          animation: 'slideInRight 0.35s ease',
          fontFamily: 'monospace',
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
            <campMeta.Icon size={28} color={campMeta.color} style={{ flexShrink: 0, marginTop: 2 }} />
            <div style={{ flex: 1 }}>
              <div style={{ color: campMeta.color, fontWeight: 'bold', fontSize: 14, marginBottom: 6 }}>
                ⚠ ATTACK IN PROGRESS
              </div>
              <div style={{ color: '#fff', fontSize: 13, fontWeight: 'bold', marginBottom: 4 }}>
                {campMeta.label}
              </div>
              <div style={{ color: '#aaa', fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>
                {campMeta.detail}
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => { navigate('/cyber/incidents'); setCampaignDismissed(campKey) }}
                  style={{ background: campMeta.color, color: '#000', border: 'none', borderRadius: 6,
                    padding: '6px 14px', fontSize: 12, fontWeight: 'bold', cursor: 'pointer' }}>
                  Respond Now
                </button>
                <button onClick={() => setCampaignDismissed(campKey)}
                  style={{ background: 'transparent', color: '#888', border: '1px solid #444',
                    borderRadius: 6, padding: '6px 10px', fontSize: 12, cursor: 'pointer' }}>
                  Dismiss
                </button>
              </div>
            </div>
            <button onClick={() => setCampaignDismissed(campKey)}
              style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 0 }}>
              <X size={16} />
            </button>
          </div>
          <style>{`
            @keyframes slideInRight {
              from { opacity: 0; transform: translateX(60px); }
              to   { opacity: 1; transform: translateX(0); }
            }
          `}</style>
        </div>
      )}
    </>
  )
}
