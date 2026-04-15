export default function SurfaceCard({ children, className = '' }) {
  return <div className={`surface-card relative z-10 p-6 ${className}`}>{children}</div>
}
