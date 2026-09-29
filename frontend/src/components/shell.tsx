import { Activity, Boxes, Building2, ChevronRight, CircleHelp, Cpu, Factory, Gauge, Map, Package, Radar, ShieldAlert, ShieldCheck, Truck, Users, Wifi, WifiOff, Zap } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LiveFeed } from './LiveFeed'
import { ThreatBanner } from './ThreatBanner'
import { useAppStore, type View } from '../stores/app-store'
import { useLiveStore } from '../stores/live-store'

const admin = [{ label: 'Overview', icon: Gauge }, { label: 'Supply Chain', icon: Map }, { label: 'Facilities', icon: Building2 }, { label: 'Inventory', icon: Boxes }, { label: 'Products', icon: Package }, { label: 'Orders', icon: Package }, { label: 'Shipments', icon: Truck }, { label: 'Fleet', icon: Truck }, { label: 'Employees', icon: Users }, { label: 'Machines & Robots', icon: Cpu }, { label: 'IoT & OT', icon: Radar }, { label: 'Digital Twin', icon: Radar }]
const cyber = [{ label: 'Auto Defense', icon: Zap }, { label: 'Security Overview', icon: ShieldCheck }, { label: 'Simulation', icon: Factory }, { label: 'Attack Surface', icon: Radar }, { label: 'Vulnerabilities', icon: ShieldAlert }, { label: 'Incidents', icon: Activity }, { label: 'Attack Paths', icon: Map }, { label: 'Risk', icon: Gauge }, { label: 'Resilience', icon: ShieldCheck }, { label: 'Controls', icon: ShieldCheck }, { label: 'What-If', icon: ChevronRight }, { label: 'Timeline', icon: Activity }]
const slug = (label: string) => label.toLowerCase().replaceAll(' ', '-').replaceAll('&', '').replaceAll('  ', '-')

export function Shell({ children }: { children: React.ReactNode }) {
  const { view, setView } = useAppStore()
  const { connected, alerts, activeCampaign } = useLiveStore()
  const location = useLocation()
  const navigate = useNavigate()
  const nav = view === 'admin' ? admin : cyber
  const switchView = (next: View) => { setView(next); navigate(next === 'admin' ? '/admin/overview' : '/cyber/security-overview') }

  const activeCamp = activeCampaign?.stage !== 'MITIGATED' ? activeCampaign : null
  const scenario = activeCamp?.scenario

  let overlayClass = ''
  if (scenario === 'RANSOMWARE_IMPACT') overlayClass = 'attack-ransomware'
  else if (scenario === 'OT_DISRUPTION') overlayClass = 'attack-ddos'
  else if (scenario === 'DATABASE_EXFILTRATION') overlayClass = 'attack-sqli'
  else if (scenario) overlayClass = 'attack-general'

  return (
    <div className={`app-shell ${overlayClass}`}>
      <style>{`
        /* Shared Overlay Styles */
        .attack-ransomware main.workspace,
        .attack-ddos main.workspace,
        .attack-sqli main.workspace,
        .attack-general main.workspace {
          position: relative;
        }
        
        .attack-ransomware main.workspace::after,
        .attack-ddos main.workspace::after,
        .attack-sqli main.workspace::after,
        .attack-general main.workspace::after {
          white-space: pre-wrap;
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          z-index: 9999;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          font-family: monospace;
          font-size: 32px;
          font-weight: bold;
          backdrop-filter: blur(4px);
          pointer-events: none;
        }

        /* 1. Ransomware */
        .attack-ransomware main.workspace { animation: glitch 0.5s infinite; }
        .attack-ransomware main.workspace::after {
          content: 'SYSTEM ENCRYPTED BY LOCKBIT 3.0 \\A PAY 50 BTC TO DECRYPT SUPPLY CHAIN';
          background: rgba(20, 0, 0, 0.85);
          color: #ff3333;
        }

        /* 2. DDoS */
        .attack-ddos main.workspace { animation: shake 0.2s infinite; opacity: 0.8; filter: grayscale(0.8); }
        .attack-ddos main.workspace::after {
          content: '503 SERVICE UNAVAILABLE \\A CONNECTION TIMEOUT - OT NETWORK OFFLINE';
          background: rgba(0, 0, 0, 0.9);
          color: #fff;
          font-size: 28px;
        }

        /* 3. SQL Injection */
        .attack-sqli main.workspace::after {
          content: 'DATABASE COMPROMISED \\A EXFILTRATING CUSTOMER RECORDS...';
          background: rgba(0, 20, 0, 0.85);
          color: #2ecc71;
          animation: blink 1s infinite;
        }

        /* 4. General APT */
        .attack-general main.workspace::after {
          content: 'UNAUTHORIZED ACCESS DETECTED \\A APT LATERAL MOVEMENT IN PROGRESS';
          background: rgba(20, 10, 0, 0.85);
          color: #f39c12;
        }

        @keyframes glitch {
          0% { filter: hue-rotate(0deg) contrast(1); }
          50% { filter: hue-rotate(90deg) contrast(2) invert(0.2); }
          100% { filter: hue-rotate(0deg) contrast(1); }
        }
        @keyframes shake {
          0% { transform: translate(1px, 1px) rotate(0deg); }
          50% { transform: translate(-1px, -2px) rotate(-1deg); }
          100% { transform: translate(1px, -1px) rotate(0deg); }
        }
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0.4; }
          100% { opacity: 1; }
        }
      `}</style>
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={20} /></div>
          <div><b>NEXORA</b><span>CYBERSECURECHAIN</span></div>
        </div>
        <LiveFeed />
        <div className="view-switch">
          <button className={view === 'admin' ? 'selected' : ''} onClick={() => switchView('admin')}>ADMIN</button>
          <button className={view === 'cyber' ? 'selected' : ''} onClick={() => switchView('cyber')}>CYBER</button>
        </div>
        <nav>
          {nav.map(item => {
            const Icon = item.icon
            const target = `/${view}/${slug(item.label)}`
            return <Link className={location.pathname === target ? 'active' : ''} to={target} key={item.label}><Icon size={16} />{item.label}</Link>
          })}
          <Link className={location.pathname === '/guide' ? 'active' : ''} to="/guide"><CircleHelp size={16} />About & Guide</Link>
        </nav>
        <div className="sidebar-foot">
          <span className={`live-dot${connected ? '' : ' offline'}`} />
          {connected ? 'IDS ML · LIVE' : 'IDS ML · OFFLINE'}
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">NEXORA COMMERCE &amp; LOGISTICS</span>
            <h1>{view === 'admin' ? 'Operations Control Tower' : 'Cyber Resilience Center'}</h1>
          </div>
          <div className="top-actions">
            <span className={`ws-status ${connected ? 'online' : 'offline'}`}>
              {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
              {connected ? 'LIVE' : 'OFFLINE'}
            </span>
            {alerts.length > 0 && (
              <span className="alert-badge" onClick={() => navigate('/cyber/incidents')} style={{ cursor: 'pointer' }}>
                ⚠ {alerts.length} ALERT{alerts.length > 1 ? 'S' : ''}
              </span>
            )}
            <span className="safety">SAFE SIMULATION ONLY</span>
            <span className="avatar">RS</span>
          </div>
        </header>
        <ThreatBanner />
        {children}
      </main>
    </div>
  )
}
