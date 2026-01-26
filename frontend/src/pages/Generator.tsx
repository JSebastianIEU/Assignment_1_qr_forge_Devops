import { GeneratorView } from '../features/qr/GeneratorView'

export const Generator = () => (
  <div className="w-full">
    <div className="mb-6">
      <h1 className="text-3xl font-bold text-slate-900">Generador de QR</h1>
      <p className="text-slate-600">Crea, prueba y guarda tus códigos listos para producción.</p>
    </div>
    <GeneratorView />
  </div>
)
