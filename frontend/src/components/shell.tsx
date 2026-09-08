import { Activity, Boxes, Building2, ChevronRight, CircleHelp, Cpu, Factory, Gauge, Map, Package, Radar, ShieldAlert, ShieldCheck, Truck, Users } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAppStore, type View } from '../stores/app-store'

const admin = [{ label: 'Overview', icon: Gauge }, { label: 'Supply Chain', icon: Map }, { label: 'Facilities', icon: Building2 }, { label: 'Inventory', icon: Boxes }, { label: 'Products', icon: Package }, { label: 'Orders', icon: Package }, { label: 'Shipments', icon: Truck }, { label: 'Fleet', icon: Truck }, { label: 'Employees', icon: Users }, { label: 'Machines & Robots', icon: Cpu }, { label: 'IoT & OT', icon: Radar }, { label: 'Digital Twin', icon: Radar }]
const cyber = [{ label: 'Security Overview', icon: ShieldCheck }, { label: 'Attack Surface', icon: Radar }, { label: 'Vulnerabilities', icon: ShieldAlert }, { label: 'Incidents', icon: Activity }, { label: 'Attack Paths', icon: Map }, { label: 'Risk', icon: Gauge }, { label: 'Resilience', icon: ShieldCheck }, { label: 'Simulation', icon: Factory }, { label: 'Controls', icon: ShieldCheck }, { label: 'What-If', icon: ChevronRight }, { label: 'Timeline', icon: Activity }]
const slug = (label: string) => label.toLowerCase().replaceAll(' ', '-')

export function Shell({ children }: { children: React.ReactNode }) {
  const { view, setView } = useAppStore(); const location = useLocation(); const navigate = useNavigate(); const nav = view === 'admin' ? admin : cyber
  const switchView = (next: View) => { setView(next); navigate(next === 'admin' ? '/admin/overview' : '/cyber/security-overview') }
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-mark"><ShieldCheck size={20} /></div><div><b>NEXORA</b><span>CYBERSECURECHAIN</span></div></div>
    <div className="view-switch"><button className={view === 'admin' ? 'selected' : ''} onClick={() => switchView('admin')}>ADMIN</button><button className={view === 'cyber' ? 'selected' : ''} onClick={() => switchView('cyber')}>CYBER</button></div>
    <nav>{nav.map(item => { const Icon = item.icon; const target = `/${view}/${slug(item.label)}`; return <Link className={location.pathname === target ? 'active' : ''} to={target} key={item.label}><Icon size={16} />{item.label}</Link> })}<Link className={location.pathname === '/guide' ? 'active' : ''} to="/guide"><CircleHelp size={16} />About & Guide</Link></nav>
    <div className="sidebar-foot"><span className="live-dot" /> SYNTHETIC TWIN · LIVE</div></aside><main className="workspace"><header className="topbar"><div><span className="eyebrow">NEXORA COMMERCE & LOGISTICS</span><h1>{view === 'admin' ? 'Operations Control Tower' : 'Cyber Resilience Center'}</h1></div><div className="top-actions"><span className="safety">SAFE SIMULATION ONLY</span><span className="avatar">AS</span></div></header>{children}</main></div>
}
