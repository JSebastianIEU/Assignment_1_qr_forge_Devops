import { create } from 'zustand'

import type { QRPreviewResponse } from '../types/api.types'

interface QRState {
  preview: QRPreviewResponse | null
  setPreview: (preview: QRPreviewResponse) => void
  clearPreview: () => void
}

export const useQRStore = create<QRState>()((set) => ({
  preview: null,
  setPreview: (preview) => set({ preview }),
  clearPreview: () => set({ preview: null }),
}))
