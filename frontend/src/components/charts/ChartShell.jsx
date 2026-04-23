export default function ChartShell({ eyebrow, title, description, children, aside }) {
  return (
    <div className="paper-panel rounded-[28px] p-6">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="space-y-3">
          {eyebrow ? <p className="paper-eyebrow">{eyebrow}</p> : null}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-900">{title}</h3>
            {description ? <p className="max-w-xl paper-copy">{description}</p> : null}
          </div>
        </div>
        {aside ? <div className="text-sm text-slate-600">{aside}</div> : null}
      </div>
      <div className="mt-6 h-[320px] w-full">{children}</div>
    </div>
  )
}
