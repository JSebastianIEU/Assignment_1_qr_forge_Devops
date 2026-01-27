import { Github, Briefcase } from 'lucide-react'

export const MobileComingSoon = () => (
  <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 z-50 overflow-hidden">
    <div className="space-y-6 max-w-sm px-6 text-center">
      {/* QR Forge Title */}
      <h1 className="text-4xl font-bold text-slate-900">QR Forge</h1>

      {/* Coming Soon */}
      <div className="space-y-2">
        <p className="text-2xl font-semibold text-slate-800">Coming Soon</p>
        <p className="text-base text-slate-600">
          Only desktop site at the moment
        </p>
      </div>

      {/* Links */}
      <div className="flex flex-col gap-3 pt-4">
        <a
          href="https://github.com/JSebastianIEU"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors font-medium"
        >
          <Github className="h-5 w-5" />
          Visit GitHub
        </a>
        <a
          href="https://juansebastianpena.dev/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium"
        >
          <Briefcase className="h-5 w-5" />
          Visit Portfolio
        </a>
      </div>
    </div>
  </div>
)
