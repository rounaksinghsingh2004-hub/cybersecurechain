import { create } from 'zustand'

export type View = 'admin' | 'cyber'
export type DrawerEntity = { title: string; data: Record<string, unknown> } | null

type AppState = { view: View; setView: (view: View) => void; drawer: DrawerEntity; setDrawer: (drawer: DrawerEntity) => void }
export const useAppStore = create<AppState>((set) => ({ view: 'admin', setView: (view) => set({ view }), drawer: null, setDrawer: (drawer) => set({ drawer }) }))

