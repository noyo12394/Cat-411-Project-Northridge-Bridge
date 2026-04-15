const links = [
  { label: 'Logic', href: '#feature-discipline' },
  { label: 'Engine', href: '#vulnerability-engine' },
  { label: 'Pipeline', href: '#research-pipeline' },
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Analytics', href: '#analytics' },
  { label: 'Transparency', href: '#transparency' },
]

export default function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between rounded-full border border-white/70 bg-white/75 px-5 py-3 shadow-[0_18px_50px_rgba(15,23,42,0.12)] backdrop-blur-xl">
        <a href="#top" className="flex items-center gap-3 text-sm font-semibold tracking-[-0.02em] text-slate-950">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 via-indigo-500 to-violet-500 text-white shadow-lg shadow-blue-500/30">
            BV
          </span>
          <span className="hidden sm:block">Bridge Vulnerability Lab</span>
        </a>
        <nav className="hidden items-center gap-5 md:flex">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-sm font-medium text-slate-600 transition hover:text-slate-950">
              {link.label}
            </a>
          ))}
        </nav>
        <a
          href="#dashboard"
          className="inline-flex items-center rounded-full bg-slate-950 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-slate-900/15 transition hover:-translate-y-0.5"
        >
          Explore Dashboard
        </a>
      </div>
    </header>
  )
}
