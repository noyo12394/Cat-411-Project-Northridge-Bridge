export default function SectionHeading({ eyebrow, title, description, align = 'left', actions }) {
  return (
    <div className={`flex flex-col gap-5 ${align === 'center' ? 'items-center text-center' : ''}`}>
      {eyebrow ? (
        <span className="inline-flex w-fit items-center rounded-full border border-slate-200/80 bg-white/75 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500 shadow-sm">
          {eyebrow}
        </span>
      ) : null}
      <div className="space-y-4">
        <h2 className="max-w-4xl font-display text-3xl font-semibold tracking-[-0.05em] text-slate-950 sm:text-4xl lg:text-[3rem]">
          {title}
        </h2>
        {description ? (
          <p className="max-w-3xl text-base leading-7 text-slate-600 sm:text-lg">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
    </div>
  )
}
