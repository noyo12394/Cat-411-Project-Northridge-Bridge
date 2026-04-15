import { Building2 } from 'lucide-react'
import Button from '../common/Button'

const navItems = [
  { label: 'Objectives', href: '#objectives' },
  { label: 'Methodology', href: '#methodology' },
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Analytics', href: '#analytics' },
]

export default function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div className="mx-auto mt-4 w-full max-w-[1440px] px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between gap-4 rounded-[28px] border border-white/80 bg-white/75 px-5 py-4 shadow-soft backdrop-blur-xl">
          <a href="#top" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ink text-white shadow-soft">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <p className="font-display text-base font-semibold tracking-[-0.03em] text-ink">
                Bridge Vulnerability Project
              </p>
              <p className="text-xs uppercase tracking-[0.2em] text-muted">Research Demo Platform</p>
            </div>
          </a>

          <nav className="hidden items-center gap-5 lg:flex">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-muted transition hover:text-ink"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <span className="hidden rounded-full border border-ocean/15 bg-ocean/5 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.24em] text-ocean md:inline-flex">
              Intrinsic model mode
            </span>
            <Button href="#dashboard" className="px-4 py-2.5">
              Open Dashboard
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
