import type { ReactNode } from 'react';

const tones = {
  neutral: 'bg-graphite-800 text-paper-dim border-graphite-700',
  amber: 'bg-amber/10 text-amber border-amber/30',
  applied: 'bg-status-applied/10 text-status-applied border-status-applied/30',
  reviewing: 'bg-status-reviewing/10 text-status-reviewing border-status-reviewing/30',
  interview: 'bg-status-interview/10 text-status-interview border-status-interview/30',
  offer: 'bg-status-offer/10 text-status-offer border-status-offer/30',
  rejected: 'bg-status-rejected/10 text-status-rejected border-status-rejected/30',
};

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode;
  tone?: keyof typeof tones;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 font-mono text-[11px] uppercase tracking-wider ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
