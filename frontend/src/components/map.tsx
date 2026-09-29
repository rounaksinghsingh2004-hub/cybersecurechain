import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet'
import { useLiveStore } from '../stores/live-store'

type Facility = {
  id: number
  code: string
  name: string
  type: string
  latitude: number
  longitude: number
  cyber_risk: number
  status: string
}

type Vehicle = {
  id: number
  code: string
  latitude: number
  longitude: number
  status: string
  integrity: string
}

export function TwinMap({
  facilities,
  vehicles = [],
  onSelect,
  onVehicleSelect,
}: {
  facilities: Facility[]
  vehicles?: Vehicle[]
  onSelect?: (f: Facility) => void
  onVehicleSelect?: (v: Vehicle) => void
}) {
  const { compromisedFacilities, liveVehicles } = useLiveStore()

  // Use live simulated vehicles if available
  const displayVehicles = liveVehicles.length > 0 ? liveVehicles : vehicles

  const routes = facilities
    .slice(0, 8)
    .map((facility, index) =>
      index
        ? [
            [facilities[index - 1].latitude, facilities[index - 1].longitude],
            [facility.latitude, facility.longitude],
          ]
        : null
    )
    .filter(Boolean) as [number, number][][]

  return (
    <MapContainer
      center={[22.9, 78.4]}
      zoom={4.35}
      className="map"
      zoomControl={false}
      attributionControl={false}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {routes.map((points, index) => (
        <Polyline
          key={index}
          positions={points}
          pathOptions={{ color: '#258db0', weight: 1.5, dashArray: '4 7', opacity: 0.75 }}
        />
      ))}

      {facilities.map(f => {
        const isCompromised = compromisedFacilities.has(f.code)
        const isHighRisk = f.cyber_risk > 60 || isCompromised
        const color = isCompromised ? '#ff4d4d' : isHighRisk ? '#eb6969' : '#60c5b8'
        const radius = isCompromised ? 11 : isHighRisk ? 8 : 6

        return (
          <CircleMarker
            key={f.id}
            center={[f.latitude, f.longitude]}
            radius={radius}
            pathOptions={{
              color: color,
              fillColor: color,
              fillOpacity: isCompromised ? 1.0 : 0.85,
              weight: isCompromised ? 3 : 1.5,
            }}
            eventHandlers={{ click: () => onSelect?.(f) }}
          >
            <Tooltip>
              <div style={{ fontSize: 11 }}>
                <b>{f.code}</b> {isCompromised && <span style={{ color: '#ff4d4d', fontWeight: 700 }}>[UNDER ATTACK]</span>}
                <br />
                {f.name} ({f.type})
                <br />
                Cyber Risk: {f.cyber_risk}/100
              </div>
            </Tooltip>
          </CircleMarker>
        )
      })}

      {displayVehicles.map(v => (
        <CircleMarker
          key={`vehicle-${v.id}`}
          center={[v.latitude, v.longitude]}
          radius={5}
          pathOptions={{
            color: '#e8bd68',
            fillColor: '#ffd166',
            fillOpacity: 1,
            weight: 2,
          }}
          eventHandlers={{ click: () => onVehicleSelect?.(v) }}
        >
          <Tooltip>
            <b>{v.code}</b> · {v.status}
            <br />
            GPS: {v.latitude.toFixed(3)}, {v.longitude.toFixed(3)} ({v.integrity})
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}
