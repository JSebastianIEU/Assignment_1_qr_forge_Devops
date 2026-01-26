import { Shield } from 'lucide-react'

import { Card } from '../components/common/Card'
import { LoginForm } from '../features/auth/LoginForm'

export const Login = () => (
  <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 sm:flex-row sm:items-start">
    <Card className="sm:w-1/2" title="Bienvenido de vuelta" description="Ingresa para gestionar tus códigos QR.">
      <LoginForm />
    </Card>
    <Card
      className="sm:w-1/2"
      title="Seguridad empresarial"
      description="Tu sesión se protege con tokens JWT y cookies httpOnly."
    >
      <div className="flex items-center gap-3 text-slate-700">
        <Shield className="h-6 w-6 text-primary-600" />
        <p className="text-sm">
          Este frontend usa interceptores de token y rutas protegidas para mantener tus datos seguros.
        </p>
      </div>
    </Card>
  </div>
)
