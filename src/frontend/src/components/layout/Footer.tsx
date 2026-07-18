import { Github } from 'lucide-react'

export const Footer = () => (
  <footer className="relative z-10 shrink-0 h-12 border-t border-white/20 bg-white/55 backdrop-blur-2xl shadow-[0_-12px_24px_rgba(15,23,42,0.08)]">
    <div className="mx-auto flex h-full w-full max-w-[1200px] items-center justify-between gap-2 px-6 text-xs text-slate-700">
      <p className="text-slate-800 text-xs">© 2025 QR Forge • Built by Juan Sebastian Peña</p>
      <a
        href="https://github.com/JSebastianIEU/qr_forge"
        target="_blank"
        rel="noreferrer"
        className="flex h-7 w-7 items-center justify-center rounded-full border border-white/30 bg-white/60 text-slate-900 transition hover:bg-white/80"
        aria-label="QR Forge GitHub"
      >
        <Github className="h-3.5 w-3.5" />
      </a>
    </div>
  </footer>
)
