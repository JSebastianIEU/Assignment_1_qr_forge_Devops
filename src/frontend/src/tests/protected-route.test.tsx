import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '../components/auth/ProtectedRoute'
import { useAuthStore } from '../store/authStore'

const renderWithRouter = (initialEntries: string[]) =>
  render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/private" element={<div>Protected content</div>} />
        </Route>
        <Route path="/login" element={<div>Login screen</div>} />
      </Routes>
    </MemoryRouter>,
  )

describe('ProtectedRoute', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.getState().logout()
  })

  it('redirects to /login when no session', async () => {
    renderWithRouter(['/private'])
    expect(await screen.findByText(/Login screen/i)).toBeInTheDocument()
  })

  it('allows access when session exists', async () => {
    useAuthStore.setState({ isAuthenticated: true })
    renderWithRouter(['/private'])
    expect(await screen.findByText(/Protected content/i)).toBeInTheDocument()
  })
})
