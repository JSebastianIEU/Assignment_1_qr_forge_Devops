import { Menu, QrCode, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../utils/constants'
import { Button } from '../common/Button'

const navLinks = [
  { to: ROUTES.generator, label: 'Generar' },
  { to: ROUTES.history, label: 'Historial' },
  { to: ROUTES.profile, label: 'Perfil' },
]

export const Navbar = () => {
  const { isAuthenticated, logoutMutation } = useAuth()
  const [open, setOpen] = useState(false)

  const navItemClass =
    'rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500'

  return (
    <header className="sticky top-0 z-30 w-full bg-white/90 backdrop-blur shadow-sm">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to={ROUTES.home} className="flex items-center gap-2 font-semibold text-slate-900">
          <span className="rounded-lg bg-primary-100 p-2 text-primary-700">
            <QrCode className="h-5 w-5" />
          </span>
          <span>QR Forge</span>
        </Link>

        <div className="hidden items-center gap-2 md:flex">
          {isAuthenticated &&
            navLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={navItemClass}>
                {link.label}
              </NavLink>
            ))}

          {isAuthenticated ? (
            <Button variant="secondary" onClick={() => logoutMutation.mutate()}>
              Salir
            </Button>
          ) : (
            <>
              <Link to={ROUTES.login} className={navItemClass}>
                Ingresar
              </Link>
              <Link to={ROUTES.signup} className="btn-primary">
                Crear cuenta
              </Link>
            </>
          )}
        </div>

        <button
          className="md:hidden rounded-lg p-2 text-slate-700 hover:bg-slate-100"
          onClick={() => setOpen((v) => !v)}
          aria-label="Alternar menú"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pb-4">
          {isAuthenticated &&
            navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={`${navItemClass} block`}
                onClick={() => setOpen(false)}
              >
                {link.label}
              </NavLink>
            ))}
          <div className="mt-3 space-y-2">
            {isAuthenticated ? (
              <Button className="w-full" variant="secondary" onClick={() => logoutMutation.mutate()}>
                Salir
              </Button>
            ) : (
              <>
                <Link to={ROUTES.login} className={`${navItemClass} block`} onClick={() => setOpen(false)}>
                  Ingresar
                </Link>
                <Link to={ROUTES.signup} className="btn-primary block text-center" onClick={() => setOpen(false)}>
                  Crear cuenta
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
