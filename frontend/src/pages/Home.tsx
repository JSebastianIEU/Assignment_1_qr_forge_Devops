import { ArrowRight, ShieldCheck, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { ROUTES } from '../utils/constants'

const valueProps = [
  { title: 'Seguridad primero', icon: ShieldCheck, text: 'Autenticación JWT y cookies httpOnly, lista para producción.' },
  { title: 'Rápido y fiable', icon: Zap, text: 'Vite + React Query para vistas optimistas y datos siempre frescos.' },
]

export const Home = () => (
  <div className="w-full">
    <section className="grid gap-8 rounded-3xl bg-gradient-to-br from-primary-50 via-white to-accent-50 px-6 py-10 shadow-inner lg:grid-cols-2 lg:items-center">
      <div className="space-y-6">
        <p className="inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-1 text-xs font-semibold uppercase text-primary-700 shadow-sm">
          SPA React + FastAPI
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Genera y gestiona códigos QR con calidad enterprise.
        </h1>
        <p className="text-lg text-slate-700">
          Panel unificado para crear, previsualizar y descargar códigos QR. Listo para tu pipeline de CI/CD en Azure
          Container Instances.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to={ROUTES.signup}>
            <Button>
              Comenzar gratis
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link to={ROUTES.generator} className="btn-secondary">
            Ver generador
          </Link>
        </div>
        <div className="flex flex-wrap gap-3 text-sm text-slate-600">
          <span>JWT con refresh</span>
          <span className="h-1 w-1 rounded-full bg-slate-400" />
          <span>Historial exportable</span>
          <span className="h-1 w-1 rounded-full bg-slate-400" />
          <span>Diseño responsive</span>
        </div>
      </div>
      <Card className="lg:ml-auto lg:max-w-md">
        <h3 className="text-lg font-semibold text-slate-900">Flujo en 3 pasos</h3>
        <ol className="mt-4 space-y-4 text-sm text-slate-700">
          <li>
            <span className="font-semibold text-primary-700">1.</span> Inicia sesión con tu cuenta segura.
          </li>
          <li>
            <span className="font-semibold text-primary-700">2.</span> Configura colores, tamaño y destino de tu QR.
          </li>
          <li>
            <span className="font-semibold text-primary-700">3.</span> Previsualiza, guarda y exporta cuando quieras.
          </li>
        </ol>
      </Card>
    </section>

    <section className="mt-10 grid gap-4 sm:grid-cols-2">
      {valueProps.map(({ title, icon: Icon, text }) => (
        <Card key={title} title={title} description={text}>
          <Icon className="h-10 w-10 text-primary-600" aria-hidden />
        </Card>
      ))}
    </section>
  </div>
)
