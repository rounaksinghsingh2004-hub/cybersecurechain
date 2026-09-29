import { useLiveStore } from '../stores/live-store'

/**
 * LiveFeed — compact sidebar ticker that shows the last 5 ML classification events.
 * Green dot = BENIGN traffic, red dot = ATTACK detected.
 * Pulses the dot when an attack event arrives.
 */
export function LiveFeed() {
  const { events, connected } = useLiveStore()

  const recent = events.slice(0, 6)

  return (
    <div className="live-feed">
      <div className="live-feed-header">
        <span className={`live-feed-dot ${connected ? 'connected' : 'disconnected'}`} />
        <span className="live-feed-title">IDS ML LIVE</span>
      </div>
      {recent.length === 0 && (
        <div className="live-feed-empty">Connecting to scanner…</div>
      )}
      {recent.map((e, i) => (
        <div key={i} className={`live-feed-row ${e.is_attack ? 'attack' : 'normal'}`}>
          <span className={`live-feed-row-dot ${e.is_attack ? 'attack' : 'normal'}`} />
          <div className="live-feed-row-content">
            <b>{e.label ?? 'SCANNING'}</b>
            <span>{e.facility_code ?? '—'}</span>
          </div>
          {e.confidence !== undefined && (
            <span className="live-feed-conf">{(e.confidence * 100).toFixed(0)}%</span>
          )}
        </div>
      ))}
    </div>
  )
}
