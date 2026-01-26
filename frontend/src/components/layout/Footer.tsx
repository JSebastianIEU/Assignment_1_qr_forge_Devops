export const Footer = () => (
  <footer className="mt-auto border-t border-slate-200 bg-white">
    <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
      <p>© {new Date().getFullYear()} QR Forge. All rights reserved.</p>
      <div className="flex items-center gap-3">
        <a
          href="https://github.com/"
          target="_blank"
          rel="noreferrer"
          className="hover:text-primary-600"
        >
          Repo
        </a>
        <a href="/docs" className="hover:text-primary-600">
          API Docs
        </a>
      </div>
    </div>
  </footer>
)
