const variants = {
  primary: 'bg-ink text-white shadow-float hover:-translate-y-0.5 hover:bg-[#0d1a2a]',
  secondary: 'bg-white text-slate-800 ring-1 ring-slate-200/90 hover:-translate-y-0.5 hover:bg-slate-50',
  subtle: 'bg-ocean/10 text-sky-800 ring-1 ring-ocean/20 hover:bg-ocean/14',
}

export default function Button({
  children,
  href,
  onClick,
  type = 'button',
  variant = 'primary',
  className = '',
  icon,
}) {
  const sharedClassName = `inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition duration-200 ${variants[variant]} ${className}`

  if (href) {
    return (
      <a href={href} className={sharedClassName}>
        <span>{children}</span>
        {icon}
      </a>
    )
  }

  return (
    <button type={type} onClick={onClick} className={sharedClassName}>
      <span>{children}</span>
      {icon}
    </button>
  )
}
