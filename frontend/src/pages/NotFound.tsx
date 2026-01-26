import { Link } from 'react-router-dom'

import { Button } from '../components/common/Button'

export const NotFound = () => (
  <div className="mx-auto flex max-w-xl flex-col items-center gap-4 text-center">
    <p className="text-sm font-semibold uppercase text-primary-700">404</p>
    <h1 className="text-3xl font-bold text-slate-900">Página no encontrada</h1>
    <p className="text-slate-600">La ruta solicitada no existe o ya no está disponible.</p>
    <Link to="/">
      <Button>Volver al inicio</Button>
    </Link>
  </div>
)
