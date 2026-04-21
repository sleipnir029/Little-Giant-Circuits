import { create } from 'zustand'

interface SpatialStore {
  selectedId: string | null
  hoveredId: string | null
  resetTick: number
  setSelected: (id: string | null) => void
  setHovered: (id: string | null) => void
  triggerReset: () => void
}

export const useSpatialStore = create<SpatialStore>((set) => ({
  selectedId: null,
  hoveredId: null,
  resetTick: 0,
  setSelected: (id) => set({ selectedId: id }),
  setHovered: (id) => set({ hoveredId: id }),
  triggerReset: () => set((s) => ({ resetTick: s.resetTick + 1 })),
}))
