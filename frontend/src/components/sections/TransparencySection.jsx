import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

function EvidenceTile({ item }) {
  return (
    <div className="overflow-hidden rounded-[26px] border border-white/80 bg-white/92 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
      <img src={item.path} alt={item.title} className="h-48 w-full object-cover" />
      <div className="border-t border-slate-200/70 p-4">
        <p className="text-sm font-semibold text-slate-950">{item.title}</p>
        <p className="mt-1 text-sm leading-6 text-slate-600">Copied from the repository figure exports for this frontend preview.</p>
      </div>
    </div>
  )
}

export default function TransparencySection({ researchData, diagnostics }) {
  return (
    <section id="transparency" className="space-y-8">
      <SectionHeading
        eyebrow="What is real vs what is conceptual"
        title="A transparency layer that explains what the browser is showing"
        description="This panel makes the data lineage explicit. The site should feel polished, but never mysterious. It also shows where the explainable-AI visuals come from and what they do and do not prove."
      />
      <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
        <div className="space-y-5">
          <InsightCard
            eyebrow="What is real"
            title="Repo-grounded pipeline and exported summaries"
            description="Project framing, notebook pipeline, statewide bridge counts, SVI / EDR portfolio summaries, damage-state results, future scenario outputs, and research figures are loaded from exported repo artifacts when available."
          >
            <ul className="space-y-3 text-sm leading-6 text-slate-600">
              <li>• Core vulnerability mode keeps PGA out of the baseline score.</li>
              <li>• ADT is reserved for prioritization / disruption logic.</li>
              <li>• NDVI appears only as optional post-event evidence.</li>
              <li>• JSON snapshots are exported from the repo into the frontend public data layer.</li>
              <li>• Feature-importance, coefficient, and calibration visuals are shown as explainable-AI artifacts rather than black-box decoration.</li>
            </ul>
          </InsightCard>
          <InsightCard
            eyebrow="What may still be adapter-based"
            title="Browser-side approximation layer"
            description="The interactive prediction engine is intentionally written as an adapter so the site can run without a backend. If a repo artifact is degenerate, the site falls back with clear labeling instead of pretending that export is production-ready."
            tone="accent"
          >
            <ul className="space-y-3 text-sm leading-6 text-slate-700">
              <li>• Live bridge animation is explanatory, not structural simulation.</li>
              <li>• The dashboard prediction engine is a faithful abstraction, not a deployed backend model.</li>
              <li>• Some exported ML tables are flagged internally when they appear unrealistically perfect or all-zero.</li>
              <li>• The contributor chips in the dashboard are local explanation cards for the prototype engine, not full SHAP-value decompositions.</li>
            </ul>
          </InsightCard>
          <InsightCard
            eyebrow="Explainable AI"
            title="Global evidence and local explanation are intentionally separated"
            description="The analytics section shows global XAI from repo-backed feature importance, coefficients, and calibration figures. The dashboard shows local explanation for the current bridge state. That separation helps the site explain model behavior without overstating certainty or causality."
          />
          <div className="rounded-[28px] border border-slate-200/80 bg-slate-50 px-5 py-4 text-sm leading-6 text-slate-600">
            {diagnostics}
          </div>
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          {researchData.evidence.slice(0, 6).map((item) => (
            <EvidenceTile key={item.file ?? item.title} item={item} />
          ))}
        </div>
      </div>
    </section>
  )
}
