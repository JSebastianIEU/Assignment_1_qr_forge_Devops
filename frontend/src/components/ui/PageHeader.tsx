interface PageHeaderProps {
  title: string
  subtitle?: string
  kicker?: string
}

export const PageHeader = ({ title, subtitle, kicker }: PageHeaderProps) => (
  <header className="space-y-1.5">
    {kicker && (
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">{kicker}</p>
    )}
    <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">{title}</h1>
    {subtitle && <p className="text-sm text-slate-600">{subtitle}</p>}
  </header>
)
