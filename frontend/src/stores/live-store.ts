/**
 * Live IDS Feed & Autonomous Cyber Center Store — Zustand store
 * Manages WebSocket connection, real-time ML traffic classifications,
 * autonomous adversary campaigns, SOAR mitigation states, and live fleet telemetry.
 */
import { create } from 'zustand'

export type LiveEventType =
  | 'CONNECTED'
  | 'TRAFFIC_NORMAL'
  | 'ATTACK_DETECTED'
  | 'PROPAGATION'
  | 'FACILITY_RECOVERED'
  | 'HEARTBEAT'
  | 'CAMPAIGN_LAUNCHED'
  | 'CAMPAIGN_DETECTED'
  | 'CAMPAIGN_MITIGATED'
  | 'FLEET_UPDATE'

export interface PacketFeatures {
  dst_port?: number
  flow_duration_us?: number
  total_fwd_pkts?: number
  fwd_len_mean?: number
  flow_bytes_per_s?: number
  flow_pkts_per_s?: number
}

export interface LiveEvent {
  type: LiveEventType
  facility_code?: string
  asset_code?: string
  label?: string
  confidence?: number
  is_attack?: boolean
  scenario?: string
  timestamp?: string
  incident_code?: string
  incident_severity?: string
  auto_responded?: boolean
  message?: string
  packet_features?: PacketFeatures
  campaign?: any
  vehicles?: any[]
  orders_protected?: number
  fallback_facility?: string
  financial_saved_inr?: number
}

export interface LiveVehicle {
  id: number
  code: string
  latitude: number
  longitude: number
  status: string
  integrity: string
}

interface LiveState {
  events: LiveEvent[]
  alerts: LiveEvent[]
  compromisedFacilities: Set<string>
  connected: boolean
  activeCampaign: any | null
  campaignHistory: any[]
  liveVehicles: LiveVehicle[]
  addEvent: (event: LiveEvent) => void
  clearAlerts: () => void
  setActiveCampaign: (camp: any) => void
}

const MAX_EVENTS = 50

export const useLiveStore = create<LiveState>((set, get) => ({
  events: [],
  alerts: [],
  compromisedFacilities: new Set(),
  connected: false,
  activeCampaign: null,
  campaignHistory: [],
  liveVehicles: [],

  addEvent: (event: LiveEvent) => {
    const state = get()
    const events = [event, ...state.events].slice(0, MAX_EVENTS)

    let alerts = state.alerts
    let compromisedFacilities = new Set(state.compromisedFacilities)
    let activeCampaign = state.activeCampaign
    let campaignHistory = state.campaignHistory
    let liveVehicles = state.liveVehicles

    if (event.type === 'ATTACK_DETECTED' && event.facility_code) {
      alerts = [event, ...state.alerts].slice(0, 10)
      compromisedFacilities.add(event.facility_code)
    } else if (event.type === 'FACILITY_RECOVERED' && event.facility_code) {
      compromisedFacilities.delete(event.facility_code)
    } else if (event.type === 'CAMPAIGN_LAUNCHED' && event.campaign) {
      activeCampaign = event.campaign
      if (event.campaign.facility_code) {
        compromisedFacilities.add(event.campaign.facility_code)
      }
    } else if (event.type === 'CAMPAIGN_DETECTED' && event.campaign) {
      activeCampaign = { ...state.activeCampaign, ...event.campaign }
    } else if (event.type === 'CAMPAIGN_MITIGATED' && event.campaign) {
      activeCampaign = { ...state.activeCampaign, ...event.campaign, stage: 'MITIGATED' }
      campaignHistory = [activeCampaign, ...campaignHistory].slice(0, 15)
      if (event.campaign.facility_code) {
        compromisedFacilities.delete(event.campaign.facility_code)
      }
    } else if (event.type === 'FLEET_UPDATE' && event.vehicles) {
      liveVehicles = event.vehicles
    }

    set({
      events,
      alerts,
      compromisedFacilities,
      activeCampaign,
      campaignHistory,
      liveVehicles,
    })
  },

  clearAlerts: () => set({ alerts: [] }),
  setActiveCampaign: (camp: any) => set({ activeCampaign: camp }),
}))

// ---------------------------------------------------------------------------
// WebSocket client — singleton, auto-reconnects with exponential backoff
// ---------------------------------------------------------------------------

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectAttempts = 0
const MAX_RECONNECT_DELAY = 30_000

function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return

  const wsUrl = window.location.hostname === 'localhost'
    ? 'ws://localhost:8000/ws/live'
    : 'wss://cybersecurechain-api.onrender.com/ws/live'

  try { ws = new WebSocket(wsUrl) } catch { scheduleReconnect(); return }

  ws.onopen = () => {
    useLiveStore.setState({ connected: true })
    reconnectAttempts = 0
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
    const ping = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) ws.send('ping')
      else clearInterval(ping)
    }, 20_000)
  }

  ws.onmessage = (e) => {
    try {
      const event: LiveEvent = JSON.parse(e.data)
      useLiveStore.getState().addEvent(event)
    } catch {}
  }

  ws.onclose = () => { useLiveStore.setState({ connected: false }); scheduleReconnect() }
  ws.onerror = () => { ws?.close() }
}

function scheduleReconnect() {
  if (reconnectTimer) return
  const delay = Math.min(2_000 * Math.pow(1.5, reconnectAttempts), MAX_RECONNECT_DELAY)
  reconnectAttempts++
  reconnectTimer = setTimeout(() => { reconnectTimer = null; connectWebSocket() }, delay)
}

// Reconnect immediately when tab becomes visible (handles Render free-tier cold starts)
if (typeof document !== 'undefined') {
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && (!ws || ws.readyState !== WebSocket.OPEN)) {
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
      reconnectAttempts = 0
      connectWebSocket()
    }
  })
}

connectWebSocket()
