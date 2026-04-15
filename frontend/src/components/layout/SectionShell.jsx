export default function SectionShell({ id, className = '', children }) {
  return (
    <section id={id} className={`section-shell scroll-mt-28 ${className}`}>
      <div className="section-grid" />
      <div className="relative z-10 p-6 sm:p-8 lg:p-10">{children}</div>
    </section>
  )
}
