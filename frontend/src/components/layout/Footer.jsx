export default function Footer() {
  return (
    <footer className="mx-auto mt-20 max-w-[1440px] px-4 pb-12 sm:px-6 lg:px-8">
      <div className="rounded-[32px] border border-slate-200/70 bg-slate-950 px-6 py-8 text-slate-300 shadow-[0_24px_80px_rgba(15,23,42,0.25)] sm:px-8 lg:px-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl space-y-3">
            <p className="font-mono text-[11px] uppercase tracking-[0.32em] text-blue-200">Research demo footer</p>
            <h3 className="text-2xl font-semibold tracking-[-0.04em] text-white">Conceptual decision-support tool for bridge vulnerability assessment</h3>
            <p className="text-sm leading-6 text-slate-400">
              Built from the repository workflow, processed engineering outputs, and frontend adapter layers that separate intrinsic vulnerability, event damage, and prioritization logic.
            </p>
          </div>
          <div className="space-y-2 text-sm text-slate-400">
            <p>California National Bridge Inventory + Northridge ShakeMap + HAZUS / SVI / NDVI / ML context</p>
            <p>Some dashboard modules run in adapter mode when full trained-model artifacts are not browser-ready.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
