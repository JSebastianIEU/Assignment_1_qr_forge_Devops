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
  it('shows validation errors with empty fields', async () => {
    renderLoginForm()
    fireEvent.submit(screen.getByRole('button', { name: /Sign in/i }))

    expect(await screen.findAllByText(/Enter a valid email/i)).toHaveLength(1)
    expect(await screen.findAllByText(/Minimum 8 characters/i)).toHaveLength(1)
  })
})
