import { describe, expect, it } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { LoginForm } from '../features/auth/LoginForm'

const renderLoginForm = () =>
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <LoginForm />
      </MemoryRouter>
    </QueryClientProvider>,
  )

describe('LoginForm', () => {
  it('muestra errores de validación con campos vacíos', async () => {
    renderLoginForm()
    fireEvent.submit(screen.getByRole('button', { name: /Ingresar/i }))

    expect(await screen.findAllByText(/Ingresa un email válido/i)).toHaveLength(1)
    expect(await screen.findAllByText(/Mínimo 8 caracteres/i)).toHaveLength(1)
  })
})
