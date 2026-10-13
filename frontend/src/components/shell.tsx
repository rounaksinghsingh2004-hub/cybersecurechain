import { useState, useEffect } from 'react'
import { Activity, Boxes, Box, Brain, Building2, ChevronRight, CircleHelp, Cpu, Factory, FileCode, Gauge, GitBranch, Map, Network, Package, Radar, RefreshCw, ShieldAlert, ShieldCheck, Truck, Users, Wifi, WifiOff, Zap } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LiveFeed } from './LiveFeed'
import { ThreatBanner } from './ThreatBanner'
import { useAppStore, type View } from '../stores/app-store'
import { useLiveStore } from '../stores/live-store'
import { post } from '../services/api'

type NavItem = { label: string; icon?: any; section?: boolean; path?: string }

const admin: NavItem[] = [
  { label: 'Overview', icon: Gauge },
  { label: 'Supply Chain', icon: Map },
  { label: 'Facilities', icon: Building2 },
  { label: 'Inventory', icon: Boxes },
  { label: 'Products', icon: Package },
  { label: 'Orders', icon: Package },
  { label: 'Shipments', icon: Truck },
  { label: 'Fleet', icon: Truck },
  { label: 'Employees', icon: Users },
  { label: 'Machines & Robots', icon: Cpu },
  { label: 'IoT & OT', icon: Radar },
  { label: 'Digital Twin', icon: Radar },
]

const cyber: NavItem[] = [
  { label: 'Auto Defense', icon: Zap, path: '/cyber/auto-defense' },
  { label: 'Command Center', icon: ShieldCheck, path: '/cyber/command-center' },
  { label: 'Vulnerabilities & Findings', icon: ShieldAlert, path: '/cyber/vulnerabilities' },
  { label: 'Attack Surface & Exposure', icon: GitBranch, path: '/cyber/exposure' },
  { label: 'Simulation & Scenario Lab', icon: RefreshCw, path: '/cyber/simulation-lab' },
  { label: 'Software & Supplier Inventory', icon: Box, path: '/cyber/inventory' },
  { label: 'AI Risk Copilot', icon: Brain, path: '/cyber/ai-copilot' },
]

const slug = (label: string) => label.toLowerCase().replaceAll(' ', '-').replaceAll('&', '').replaceAll('  ', '-')

export function Shell({ children }: { children: React.ReactNode }) {
  const { view, setView } = useAppStore()
  const { connected, alerts, activeCampaign } = useLiveStore()
  const location = useLocation()
  const navigate = useNavigate()
  const [damage, setDamage] = useState(0)

  const isCyber = view === 'cyber' || view === 'supplylens'
  const nav = view === 'admin' ? admin : cyber

  const switchView = (next: View) => {
    setView(next)
    if (next === 'admin') navigate('/admin/overview')
    else navigate('/cyber/command-center')
  }

  const showOverlay = view === 'admin' && activeCampaign?.stage !== 'MITIGATED'
  const scenario = showOverlay ? activeCampaign?.scenario : null

  useEffect(() => {
    if (!showOverlay) {
      setDamage(0)
      return
    }
    const timer = setInterval(() => {
      setDamage(d => d + 45000 + Math.floor(Math.random() * 10000))
    }, 1000)
    return () => clearInterval(timer)
  }, [showOverlay])

  let overlayClass = ''
  if (scenario === 'RANSOMWARE_IMPACT') overlayClass = 'attack-ransomware'
  else if (scenario === 'OT_DISRUPTION') overlayClass = 'attack-ddos'
  else if (scenario === 'DATABASE_EXFILTRATION') overlayClass = 'attack-sqli'
  else if (scenario) overlayClass = 'attack-general'

  const isItemActive = (item: NavItem) => {
    if (item.path && location.pathname === item.path) return true
    if (item.path === '/cyber/command-center') {
      return ['/cyber/command-center', '/cyber/security-overview', '/cyber/overview', '/cyber/sl-overview', '/cyber/risk', '/cyber/resilience', '/cyber/controls', '/cyber/incidents', '/cyber/timeline'].some(p => location.pathname.startsWith(p))
    }
    if (item.path === '/cyber/vulnerabilities') {
      return ['/cyber/vulnerabilities', '/cyber/findings'].some(p => location.pathname.startsWith(p))
    }
    if (item.path === '/cyber/exposure') {
      return ['/cyber/exposure', '/cyber/exposure-map', '/cyber/attack-surface', '/cyber/attack-paths'].some(p => location.pathname.startsWith(p))
    }
    if (item.path === '/cyber/simulation-lab') {
      return ['/cyber/simulation-lab', '/cyber/scenario-lab', '/cyber/what-if', '/cyber/simulation'].some(p => location.pathname.startsWith(p))
    }
    if (item.path === '/cyber/inventory') {
      return ['/cyber/inventory', '/cyber/components', '/cyber/suppliers', '/cyber/sbom-imports'].some(p => location.pathname.startsWith(p))
    }
    return item.path ? location.pathname.startsWith(item.path) : location.pathname === `/${view}/${slug(item.label)}`
  }

  return (
    <div className={`app-shell ${overlayClass}`} data-damage={damage.toLocaleString()}>
      <style>{`
        /* Shared Overlay Styles */
        .attack-ransomware::after,
        .attack-ddos::after,
        .attack-sqli::after,
        .attack-general::after {
          white-space: pre-wrap;
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          z-index: 999999;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          font-family: monospace;
          font-size: 36px;
          font-weight: bold;
          backdrop-filter: blur(8px);
          pointer-events: none;
        }

        .attack-ransomware { animation: glitch 0.5s infinite; }
        .attack-ransomware::after {
          content: 'SYSTEM ENCRYPTED BY LOCKBIT 3.0 \\A PAY 50 BTC TO DECRYPT SUPPLY CHAIN \\A \\A FINANCIAL DAMAGE: ₹' attr(data-damage);
          background: rgba(20, 0, 0, 0.85);
          color: #ff3333;
        }

        .attack-ddos { animation: shake 0.2s infinite; filter: grayscale(0.8); }
        .attack-ddos::after {
          content: '503 SERVICE UNAVAILABLE \\A CONNECTION TIMEOUT - OT NETWORK OFFLINE \\A \\A FINANCIAL DAMAGE: ₹' attr(data-damage);
          background: rgba(0, 0, 0, 0.95);
          color: #fff;
        }

        .attack-sqli::after {
          content: 'DATABASE COMPROMISED \\A EXFILTRATING CUSTOMER RECORDS... \\A \\A FINANCIAL DAMAGE: ₹' attr(data-damage);
          background: rgba(0, 20, 0, 0.9);
          color: #2ecc71;
          animation: blink 1s infinite;
        }

        .attack-general::after {
          content: 'UNAUTHORIZED ACCESS DETECTED \\A APT LATERAL MOVEMENT IN PROGRESS \\A \\A FINANCIAL DAMAGE: ₹' attr(data-damage);
          background: rgba(20, 10, 0, 0.9);
          color: #f39c12;
        }

        @keyframes glitch {
          0% { filter: hue-rotate(0deg) contrast(1); }
          50% { filter: hue-rotate(90deg) contrast(2) invert(0.2); }
          100% { filter: hue-rotate(0deg) contrast(1); }
        }
        @keyframes shake {
          0% { transform: translate(2px, 2px) rotate(0deg); }
          50% { transform: translate(-2px, -3px) rotate(-1deg); }
          100% { transform: translate(2px, -2px) rotate(0deg); }
        }
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0.2; }
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
          <button className={isCyber ? 'selected' : ''} onClick={() => switchView('cyber')}>CYBER</button>
        </div>
        <nav>
          {nav.map((item) => {
            const Icon = item.icon
            const target = item.path || `/${view}/${slug(item.label)}`
            const isActive = isItemActive(item)
            return (
              <Link className={isActive ? 'active' : ''} to={target} key={item.label}>
                <Icon size={16} />
                {item.label}
              </Link>
            )
          })}
          <Link className={location.pathname === '/guide' ? 'active' : ''} to="/guide">
            <CircleHelp size={16} />
            About &amp; Guide
          </Link>
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
            <h1>{view === 'admin' ? 'Operations Control Tower' : 'Cyber Resilience & SupplyLens AI Command'}</h1>
          </div>
          <div className="top-actions">
            <span className={`ws-status ${connected ? 'online' : 'offline'}`}>
              {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
              {connected ? 'LIVE' : 'OFFLINE'}
            </span>
            {alerts.length > 0 && (
              <span className="alert-badge" onClick={() => navigate('/cyber/command-center')} style={{ cursor: 'pointer' }}>
                ⚠ {alerts.length} ALERT{alerts.length > 1 ? 'S' : ''}
              </span>
            )}
            <button
              className="reset-demo-btn"
              onClick={() => { post('/api/cyber/auto-defense/trigger-defense'); useLiveStore.getState().clearAlerts() }}
              style={{ background: '#42b7c2', color: '#000', border: 'none', padding: '4px 10px', borderRadius: 4, fontSize: 11, fontWeight: 'bold', cursor: 'pointer' }}
            >
              Reset Demo
            </button>
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
