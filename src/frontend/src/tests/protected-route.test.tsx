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
          <Route path="/private" element={<div>Contenido protegido</div>} />
        </Route>
        <Route path="/login" element={<div>Pantalla login</div>} />
      </Routes>
    </MemoryRouter>,
  )

describe('ProtectedRoute', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.getState().logout()
  })

  it('redirecciona a /login cuando no hay sesión', async () => {
    renderWithRouter(['/private'])
    expect(await screen.findByText(/Pantalla login/i)).toBeInTheDocument()
  })

  it('permite acceder cuando hay sesión', async () => {
    useAuthStore.setState({ isAuthenticated: true })
    renderWithRouter(['/private'])
    expect(await screen.findByText(/Contenido protegido/i)).toBeInTheDocument()
  })
})
