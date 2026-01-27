import { History, Home, LogIn, LogOut, QrCode, Settings, UserPlus, Wand2 } from 'lucide-react'
import { Link, NavLink } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../utils/constants'
import { Button } from '../ui/Button'

interface SidebarProps {
  openMobile: boolean
  onCloseMobile: () => void
}

const navItems = [
  { to: ROUTES.home, label: 'Home', icon: Home },
  { to: ROUTES.generator, label: 'Generator', icon: Wand2 },
  { to: ROUTES.history, label: 'History', icon: History },
  { to: ROUTES.profile, label: 'Profile', icon: Settings },
]

export const Sidebar = ({ openMobile, onCloseMobile }: SidebarProps) => {
  const { isAuthenticated, logoutMutation } = useAuth()

  const navContent = (
    <div className="glass-nav flex h-full w-[260px] min-h-0 flex-col gap-2 rounded-[24px] border border-white/30 bg-white/55 p-3 text-slate-900 backdrop-blur-2xl shadow-[0_14px_28px_rgba(15,23,42,0.10)]">
      <Link to={ROUTES.home} className="flex items-center gap-1" onClick={onCloseMobile}>
        <span className="rounded-xl bg-[var(--brand-primary)]/90 p-1.5 shadow-sm">
          <QrCode className="h-4 w-4 text-white" />
        </span>
        <div className="hidden sm:block">
          <p className="text-xs text-slate-500">QR Forge</p>
          <p className="text-sm font-semibold text-slate-900">Control</p>
        </div>
      </Link>

      <nav className="space-y-1">
        {(isAuthenticated ? navItems : [navItems[0], navItems[1]]).map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              [
                'flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-semibold transition',
                isActive
                  ? 'bg-white/70 text-[var(--brand-primary)] shadow-sm'
                  : 'text-slate-500 hover:text-slate-800',
              ].join(' ')
            }
          >
            <Icon className="h-4 w-4 text-current" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto space-y-1.5">
        {isAuthenticated ? (
          <Button variant="secondary" fullWidth onClick={() => logoutMutation.mutate()}>
            <LogOut className="mr-2 h-4 w-4" />
            Sign out
          </Button>
        ) : (
          <>
            <Link to={ROUTES.login} onClick={onCloseMobile}>
              <Button variant="primary" fullWidth>
                <LogIn className="mr-2 h-4 w-4" />
                Sign in
              </Button>
            </Link>
            <Link to={ROUTES.signup} onClick={onCloseMobile}>
              <Button variant="ghost" fullWidth>
                <UserPlus className="mr-2 h-4 w-4 text-slate-700" />
                Create account
              </Button>
            </Link>
          </>
        )}
      </div>
    </div>
  )

  return (
    <>
      <div className="hidden h-full min-h-0 lg:block">{navContent}</div>
      {openMobile && <div className="lg:hidden">{navContent}</div>}
    </>
  )
}
