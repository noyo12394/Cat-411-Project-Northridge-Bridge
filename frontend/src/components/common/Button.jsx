const variants = {
  primary: 'bg-ink text-white shadow-float hover:-translate-y-0.5 hover:bg-[#0d1a2a]',
  secondary: 'bg-white text-ink ring-1 ring-slate-200 hover:-translate-y-0.5 hover:bg-slate-50',
  subtle: 'bg-ocean/8 text-ocean ring-1 ring-ocean/10 hover:bg-ocean/12',
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
