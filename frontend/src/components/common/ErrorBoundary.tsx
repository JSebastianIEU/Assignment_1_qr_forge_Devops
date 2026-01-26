import type { PropsWithChildren, ReactNode } from 'react'
import { Component } from 'react'
import { Alert } from './Alert'
import { Button } from './Button'

interface ErrorBoundaryProps extends PropsWithChildren {
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    // Log for observability; in production we could send to monitoring
    console.error('ErrorBoundary caught', error)
  }

  handleReset = () => {
    this.setState({ hasError: false })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="mx-auto max-w-2xl py-12">
            <Alert tone="error" title="Algo salió mal">
              <p className="mt-2 text-sm text-slate-700">
                Recarga la página o vuelve al inicio. Si el problema persiste, contacta al equipo.
              </p>
              <div className="mt-4 flex gap-3">
                <Button onClick={this.handleReset}>Recargar</Button>
                <Button variant="secondary" onClick={() => (window.location.href = '/')}>
                  Ir al inicio
                </Button>
              </div>
            </Alert>
          </div>
        )
      )
    }
    return this.props.children
  }
}
