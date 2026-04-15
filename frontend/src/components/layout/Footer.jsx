export default function Footer() {
  return (
    <footer className="mx-auto mt-8 w-full max-w-[1440px] px-4 pb-10 sm:px-6 lg:px-8">
      <div className="section-shell overflow-hidden">
        <div className="section-grid" />
        <div className="relative z-10 flex flex-col gap-6 p-6 sm:p-8 lg:flex-row lg:items-end lg:justify-between lg:p-10">
          <div className="space-y-3">
            <p className="eyebrow">Research project footer</p>
            <h3 className="font-display text-2xl font-semibold tracking-[-0.04em] text-ink">
              Conceptual decision-support tool for bridge vulnerability assessment
            </h3>
            <p className="max-w-3xl text-sm leading-7 text-muted">
              This website is designed as a polished academic demo for bridge vulnerability prediction, inspection prioritization,
              and comparative catastrophe-model reasoning. The current dashboard uses a transparent mock scoring engine so it can
              later be replaced with a trained model without changing the overall interface.
            </p>
          </div>
          <div className="grid gap-3 text-sm text-muted sm:grid-cols-2 lg:text-right">
            <p>Core model uses intrinsic structural features.</p>
            <p>PGA is intentionally excluded from the primary vulnerability input set.</p>
            <p>NDVI is optional and post-event only.</p>
            <p>Traffic importance is reserved for prioritization and consequence logic.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
