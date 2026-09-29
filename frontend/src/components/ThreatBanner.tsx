import { useState } from 'react'
import { AlertTriangle, X, ShieldCheck, Zap } from 'lucide-react'
import { useLiveStore } from '../stores/live-store'
import { useNavigate } from 'react-router-dom'

/**
 * ThreatBanner — full-width alert banner that renders at the top of the
 * workspace area whenever the live ML scanner detects an active attack.
 * Shows the attack classification, affected facility, confidence score,
 * and a Respond Now button that navigates to the Incidents tab.
 */
export function ThreatBanner() {
  const { alerts, compromisedFacilities, clearAlerts } = useLiveStore()
  const [dismissed, setDismissed] = useState<string[]>([])
  const navigate = useNavigate()

  // The most recent non-dismissed alert
  const active = alerts.find(a => a.incident_code && !dismissed.includes(a.incident_code ?? ''))

  if (!active) return null

  const dismiss = () => {
    if (active.incident_code) setDismissed(d => [...d, active.incident_code!])
  }

  const respond = () => {
    dismiss()
    navigate('/cyber/incidents')
  }

  return (
    <div className="threat-banner">
      <div className="threat-banner-icon">
        <AlertTriangle size={18} />
      </div>
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
        <button className="threat-respond-btn" onClick={respond}>
          <Zap size={13} /> Respond Now
        </button>
        <button className="threat-dismiss-btn" onClick={dismiss}>
          <X size={14} />
        </button>
      </div>
    </div>
  )
}
