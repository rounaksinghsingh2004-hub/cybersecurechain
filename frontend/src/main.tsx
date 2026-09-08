import 'leaflet/dist/leaflet.css'
import './styles.css'
import './guide.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App'

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
