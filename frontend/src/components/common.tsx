import { AlertTriangle, ArrowUpRight, Check, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../stores/app-store'

export function Status({ value }: { value: string | number | null | undefined }) {
  const text = String(value || 'UNKNOWN').replaceAll('_', ' ')
  const cls = /critical|high|delayed|degraded|compromised/i.test(text) ? 'danger' : /medium|transit|reserved/i.test(text) ? 'warning' : 'success'
  return <span className={`status ${cls}`}>{text}</span>
}

export function Metric({ label, value, note, tone = 'cyan' }: { label: string; value: string | number; note?: string; tone?: string }) {
  return <section className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong>{note && <small>{note}</small>}</section>
}

export function Panel({ title, action, children, className = '' }: { title: string; action?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><header><h2>{title}</h2>{action}</header>{children}</section>
}

export function EntityDrawer() {
  const { drawer, setDrawer } = useAppStore(); const navigate = useNavigate()
  if (!drawer) return null
  return <aside className="drawer"><div className="drawer-head"><div><span className="eyebrow">QUICK INSPECT</span><h2>{drawer.title}</h2></div><button className="icon-button" onClick={() => setDrawer(null)} title="Close"><X size={18} /></button></div>
    <div className="drawer-body">{Object.entries(drawer.data).filter(([, value]) => typeof value !== 'object').map(([key, value]) => <div className="key-value" key={key}><span>{key.replaceAll('_', ' ')}</span><b>{String(value ?? '—')}</b></div>)}
      <div className="drawer-note"><AlertTriangle size={16} /> Details are derived from the shared digital twin.</div>
      <button className="command-button" onClick={() => navigate('/details')}>Open full details <ArrowUpRight size={15} /></button></div></aside>
}

export function Empty({ message }: { message: string }) { return <div className="empty"><Check size={18} />{message}</div> }
