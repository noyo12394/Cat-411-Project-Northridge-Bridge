import { Component } from 'react'

export default class SectionErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('Section render failed:', this.props.sectionLabel, error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <section className="rounded-[32px] border border-amber-200/70 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-600">Section fallback</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
            {this.props.sectionLabel ?? 'Research section'} could not render
          </h3>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
            The rest of the dashboard is still available. This guard is here so one runtime issue does not blank the entire site.
          </p>
        </section>
      )
    }

    return this.props.children
  }
}
