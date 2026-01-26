import type { PropsWithChildren } from 'react'

import { Footer } from './Footer'
import { Navbar } from './Navbar'

export const Shell = ({ children }: PropsWithChildren) => (
  <div className="flex min-h-screen flex-col bg-gradient-to-b from-slate-50 to-slate-100">
    <Navbar />
    <main className="mx-auto flex w-full max-w-6xl flex-1 px-4 py-6 sm:py-10">{children}</main>
    <Footer />
  </div>
)
