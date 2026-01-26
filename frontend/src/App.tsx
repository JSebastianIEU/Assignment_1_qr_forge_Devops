import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom'

import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { Shell } from './components/layout/Shell'
import { Generator } from './pages/Generator'
import { History } from './pages/History'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { Profile } from './pages/Profile'
import { Signup } from './pages/Signup'
import { ROUTES } from './utils/constants'

const AppLayout = () => (
  <Shell>
    <ErrorBoundary>
      <Outlet />
    </ErrorBoundary>
  </Shell>
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
