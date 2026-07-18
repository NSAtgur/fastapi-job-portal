export function Logo({ className = '' }: { className?: string }) {
  return (
    <span
      className={`font-display font-bold tracking-tight text-paper ${className}`}
      style={{ letterSpacing: '-0.02em' }}
    >
      career<span className="text-amber">dock</span>
    </span>
  );
}
