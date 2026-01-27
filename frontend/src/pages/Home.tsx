import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { PageHeader } from '../components/ui/PageHeader'
import { ROUTES } from '../utils/constants'
import { MainPanel } from '../components/layout/MainPanel'

const capsuleLabels = ['Free forever', 'Unlimited exports', 'SVG & PNG']
const flowSteps = [
  'Sign in securely.',
  'Set destination, colors, and size.',
  'Preview, save, download, or export.',
]

export const Home = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="Dashboard"
      title="Generate and manage production-ready QR codes"
      subtitle="Create, preview, save, and export QR codes built for production—free forever."
    />

    <div className="grid gap-5 lg:grid-cols-[1.15fr,0.85fr]">
      <Card
        variant="elevated"
        className="flex flex-col gap-4 border border-white/60 bg-white/75 p-6 text-slate-900 shadow-[0_12px_28px_rgba(15,23,42,0.14)]"
        title="Custom QR codes, ready for production"
        description="Design and deliver QR codes that meet enterprise standards. Preview instantly, download SVG/PNG, and keep a full history with CSV export."
      >
        <div className="flex flex-wrap gap-2">
          <Link to={ROUTES.generator}>
            <Button variant="primary">
              Try the generator
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link to={ROUTES.signup}>
            <Button variant="ghost">Create account</Button>
          </Link>
        </div>
      </Card>

      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap gap-2">
          {capsuleLabels.map((label) => (
            <span key={label} className="badge-pill">
              {label}
            </span>
          ))}
        </div>
        <div className="relative mx-auto w-full max-w-[420px] pl-8 text-slate-800 sm:mx-0">
          <div className="absolute left-4 top-3 h-[calc(100%-1rem)] w-px bg-slate-200" aria-hidden />
          <h3 className="text-base font-semibold text-slate-900">Flow in 3 steps</h3>
          <ol className="space-y-4 text-sm text-slate-800">
            {flowSteps.map((text, idx) => (
              <li key={text} className="relative flex items-start gap-3">
                <span className="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-white text-xs font-bold text-slate-900 shadow-sm">
                  {idx + 1}
                </span>
                <span className="text-slate-800">{text}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
    </div>
  </MainPanel>
)
