import { Menu } from 'lucide-react'
import { useState } from 'react'

import { BackgroundLayer } from './BackgroundLayer'
import { Sidebar } from '../nav/Sidebar'
import { MainPanel } from './MainPanel'
//
import { Footer } from './Footer'

interface AppShellProps {
  children: React.ReactNode
}

export const AppShell = ({ children }: AppShellProps) => {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="flex flex-col h-[100dvh] overflow-hidden bg-transparent text-slate-900">
      <BackgroundLayer />

      {/* Header con navbar */}
      <div className="relative z-20 shrink-0 h-12 border-b border-white/20 bg-white/55 backdrop-blur-2xl">
        <div className="mx-auto w-full max-w-[1200px] px-6 py-2">
          <div className="flex items-center gap-3 lg:hidden">
            <button
              onClick={() => setMobileNavOpen((v) => !v)}
              className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/70 text-slate-900 shadow-glass-sm backdrop-blur focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--brand-primary)]"
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">QR Forge</p>
              <p className="text-sm font-semibold text-slate-900">Control</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar + MainPanel shell - flexible middle section */}
      <div className="relative z-10 flex-1 overflow-hidden">
        <div className="mx-auto grid h-full max-w-[1200px] grid-cols-[260px_1fr] gap-6 px-6 py-6">
          <Sidebar openMobile={mobileNavOpen} onCloseMobile={() => setMobileNavOpen(false)} />
          <MainPanel>
            {children}
          </MainPanel>
        </div>
      </div>

      {/* Footer fijo al final */}
      <Footer />
    </div>
  )
}
