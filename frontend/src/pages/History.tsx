import { HistoryView } from '../features/qr/HistoryView'

export const History = () => (
  <div className="w-full space-y-4">
    <div>
      <h1 className="text-3xl font-bold text-slate-900">Historial</h1>
      <p className="text-slate-600">Consulta y exporta los QR generados previamente.</p>
    </div>
    <HistoryView />
  </div>
)
