import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet'

type Facility = { id: number; code: string; name: string; type: string; latitude: number; longitude: number; cyber_risk: number; status: string }
type Vehicle = { id: number; code: string; latitude: number; longitude: number; status: string; integrity: string }

export function TwinMap({ facilities, vehicles = [], onSelect, onVehicleSelect }: { facilities: Facility[]; vehicles?: Vehicle[]; onSelect?: (f: Facility) => void; onVehicleSelect?: (v: Vehicle) => void }) {
  const routes = facilities.slice(0, 8).map((facility, index) => index ? [[facilities[index - 1].latitude, facilities[index - 1].longitude], [facility.latitude, facility.longitude]] : null).filter(Boolean) as [number, number][][]
  return <MapContainer center={[22.9, 78.4]} zoom={4.35} className="map" zoomControl={false} attributionControl={false}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {routes.map((points, index) => <Polyline key={index} positions={points} pathOptions={{ color: '#258db0', weight: 1.5, dashArray: '4 7', opacity: .75 }} />)}
    {facilities.map(f => <CircleMarker key={f.id} center={[f.latitude, f.longitude]} radius={f.cyber_risk > 60 ? 8 : 6} pathOptions={{ color: f.cyber_risk > 60 ? '#eb6969' : '#60c5b8', fillColor: f.cyber_risk > 60 ? '#eb6969' : '#60c5b8', fillOpacity: .9 }} eventHandlers={{ click: () => onSelect?.(f) }}><Tooltip><b>{f.code}</b><br />{f.name}</Tooltip></CircleMarker>)}
    {vehicles.map(v => <CircleMarker key={`vehicle-${v.id}`} center={[v.latitude, v.longitude]} radius={4} pathOptions={{ color: '#e8bd68', fillColor: '#e8bd68', fillOpacity: 1 }} eventHandlers={{ click: () => onVehicleSelect?.(v) }}><Tooltip>{v.code} · {v.status}</Tooltip></CircleMarker>)}
  </MapContainer>
}
