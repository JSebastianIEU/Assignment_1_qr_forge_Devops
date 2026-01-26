import { UserPlus } from 'lucide-react'

import { Card } from '../components/common/Card'
import { SignupForm } from '../features/auth/SignupForm'

export const Signup = () => (
  <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 sm:flex-row sm:items-start">
    <Card className="sm:w-1/2" title="Crea tu cuenta" description="Accede al generador de QR con dashboard seguro.">
      <SignupForm />
    </Card>
    <Card className="sm:w-1/2" title="¿Por qué registrarse?">
      <div className="space-y-3 text-sm text-slate-700">
        <div className="flex items-center gap-2">
          <UserPlus className="h-5 w-5 text-primary-600" />
          <span>Historial persistente y exportable.</span>
        </div>
        <div className="flex items-center gap-2">
          <UserPlus className="h-5 w-5 text-primary-600" />
          <span>Sesiones protegidas con JWT y cookies httpOnly.</span>
        </div>
      </div>
    </Card>
  </div>
)
