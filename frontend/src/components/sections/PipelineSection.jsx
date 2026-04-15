import SectionHeading from '../common/SectionHeading'

export default function PipelineSection({ pipeline }) {
  return (
    <section id="research-pipeline" className="space-y-8">
      <SectionHeading
        eyebrow="Research pipeline / data flow"
        title="From California bridge inventory to bridge-level screening, fragility, and scenario outputs"
        description="This flow mirrors the repo structure directly, using the same file names and processing steps rather than abstract placeholders."
      />
      <div className="grid gap-5 lg:grid-cols-6">
        {pipeline.map((step, index) => (
          <div key={step.file} className="relative rounded-[28px] border border-white/80 bg-white/92 p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
            <div className="absolute -left-2 top-6 hidden h-px w-4 bg-slate-300 lg:block" />
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">Step {index + 1}</p>
            <h3 className="mt-3 text-lg font-semibold tracking-[-0.03em] text-slate-950">{step.label}</h3>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="rounded-2xl border border-slate-200/80 bg-slate-50 px-3 py-2 font-mono text-xs text-slate-700">{step.file}</div>
              <p>{step.output}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
