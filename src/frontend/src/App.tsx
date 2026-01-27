import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom'

import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { AppShell } from './components/layout/AppShell'
import { MobileComingSoon } from './components/layout/MobileComingSoon'
import { Generator } from './pages/Generator'
import { History } from './pages/History'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { Profile } from './pages/Profile'
import { Signup } from './pages/Signup'
import { ROUTES } from './utils/constants'

// Wrapper que maneja mobile/tablet vs desktop
const AppLayout = () => (
  <>
    {/* Mobile/Tablet Coming Soon (global) */}
    <div className="lg:hidden">
      <MobileComingSoon />
    </div>

    {/* Desktop App */}
    <div className="hidden lg:block">
      <AppShell>
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </AppShell>
    </div>
  </>
)

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: ROUTES.login, element: <Login /> },
      { path: ROUTES.signup, element: <Signup /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: ROUTES.generator, element: <Generator /> },
          { path: ROUTES.history, element: <History /> },
          { path: ROUTES.profile, element: <Profile /> },
        ],
      },
      { path: '*', element: <NotFound /> },
    ],
  },
])

const App = () => <RouterProvider router={router} />

export default App
