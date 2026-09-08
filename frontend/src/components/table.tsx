import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Status } from './common'

export function DataTable({ rows, columns, onRowClick }: { rows: Record<string, unknown>[]; columns: { key: string; label: string; status?: boolean }[]; onRowClick?: (row: Record<string, unknown>) => void }) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => rows.filter(row => JSON.stringify(row).toLowerCase().includes(query.toLowerCase())), [rows, query])
  return <><label className="table-search"><Search size={15} /><input placeholder="Filter results" value={query} onChange={event => setQuery(event.target.value)} /></label><div className="table-wrap"><table><thead><tr>{columns.map(column => <th key={column.key}>{column.label}</th>)}</tr></thead><tbody>{filtered.slice(0, 70).map((row, index) => <tr key={String(row.id ?? index)} onClick={() => onRowClick?.(row)}>{columns.map(column => <td key={column.key}>{column.status ? <Status value={String(row[column.key] ?? '')} /> : String(row[column.key] ?? '—')}</td>)}</tr>)}{!filtered.length && <tr><td colSpan={columns.length}>No matching records</td></tr>}</tbody></table></div></>
}

