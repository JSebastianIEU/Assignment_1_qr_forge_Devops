import { UserPlus } from 'lucide-react'

import { Card } from '../components/common/Card'
import { SignupForm } from '../features/auth/SignupForm'
import { PageHeader } from '../components/ui/PageHeader'
import { MainPanel } from '../components/layout/MainPanel'

export const Signup = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="Sign up"
      title="Create your account"
      subtitle="Access the generator with history, exports, and secure sessions."
    />
    <div className="grid gap-4 lg:grid-cols-2">
      <Card variant="elevated" title="Start building" description="A secure dashboard for your QR operations.">
        <SignupForm />
      </Card>
      <Card className="space-y-3" variant="subtle" title="Why sign up?">
        <div className="flex items-center gap-2 text-sm text-slate-700">
          <UserPlus className="h-5 w-5 text-[var(--brand-primary)]" />
          <span>Persistent, exportable history.</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-700">
          <UserPlus className="h-5 w-5 text-[var(--brand-primary)]" />
          <span>Sessions secured with JWT and httpOnly cookies.</span>
        </div>
      </Card>
    </div>
    </div>
  </MainPanel>
)
