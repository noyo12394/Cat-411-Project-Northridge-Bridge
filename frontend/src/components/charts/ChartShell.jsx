export default function ChartShell({ eyebrow, title, description, children, aside }) {
  return (
    <div className="rounded-[28px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="space-y-3">
          {eyebrow ? <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">{eyebrow}</p> : null}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-950">{title}</h3>
            {description ? <p className="max-w-xl text-sm leading-6 text-slate-600">{description}</p> : null}
          </div>
        </div>
        {aside ? <div className="text-sm text-slate-500">{aside}</div> : null}
      </div>
      <div className="mt-6 h-[320px] w-full">{children}</div>
    </div>
  )
}
