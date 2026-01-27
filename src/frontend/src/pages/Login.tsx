import { Shield } from 'lucide-react'

import { Card } from '../components/common/Card'
import { LoginForm } from '../features/auth/LoginForm'
import { PageHeader } from '../components/ui/PageHeader'
import { MainPanel } from '../components/layout/MainPanel'

export const Login = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="Access"
      title="Sign in"
      subtitle="Secure authentication with JWT and refresh tokens."
    />
    <div className="grid gap-4 lg:grid-cols-2">
      <Card
        variant="elevated"
        title="Welcome back"
        description="Sign in to manage your QR catalog and history."
      >
        <LoginForm />
      </Card>
      <Card
        variant="subtle"
        title="Enterprise-ready security"
        description="Sessions are protected with tokens and httpOnly cookies."
      >
        <div className="flex items-center gap-3 text-slate-700">
          <Shield className="h-6 w-6 text-[var(--brand-primary)]" />
          <p className="text-sm">
            Interceptors, protected routes, and disciplined storage make every session resilient.
          </p>
        </div>
      </Card>
    </div>
    </div>
  </MainPanel>
)
