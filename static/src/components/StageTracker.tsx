import type { ApplicationStatus } from '@/types';

const STAGES: { key: ApplicationStatus; label: string }[] = [
  { key: 'applied', label: 'Applied' },
  { key: 'reviewing', label: 'Reviewing' },
  { key: 'interview', label: 'Interview' },
  { key: 'offer', label: 'Offer' },
];

const STAGE_COLOR: Record<ApplicationStatus, string> = {
  applied: 'var(--color-status-applied)',
  reviewing: 'var(--color-status-reviewing)',
  interview: 'var(--color-status-interview)',
  offer: 'var(--color-status-offer)',
  rejected: 'var(--color-status-rejected)',
};

interface StageTrackerProps {
  status: ApplicationStatus;
  compact?: boolean;
}

/**
 * Horizontal stage tracker reflecting the real application pipeline
 * (applied -> reviewing -> interview -> offer), or a terminal "rejected" state.
 * Used full-size on the Applications page and compact on job cards.
 */
export function StageTracker({ status, compact = false }: StageTrackerProps) {
  if (status === 'rejected') {
    return (
      <div className="flex items-center gap-2">
        <span
          className="h-2 w-2 rounded-full"
          style={{ background: STAGE_COLOR.rejected }}
        />
        <span
          className="font-mono uppercase tracking-wider text-status-rejected"
          style={{ fontSize: compact ? 10 : 11 }}
        >
          Not moving forward
        </span>
      </div>
    );
  }

  const currentIndex = STAGES.findIndex((s) => s.key === status);

  return (
    <div className="flex items-center gap-0">
      {STAGES.map((stage, i) => {
        const reached = i <= currentIndex;
        const isLast = i === STAGES.length - 1;
        return (
          <div key={stage.key} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <span
                className="rounded-full transition-colors duration-300"
                style={{
                  width: compact ? 6 : 9,
                  height: compact ? 6 : 9,
                  background: reached ? STAGE_COLOR[stage.key] : 'var(--color-graphite-700)',
                  boxShadow: reached && i === currentIndex ? `0 0 0 3px ${STAGE_COLOR[stage.key]}22` : 'none',
                }}
              />
              {!compact && (
                <span
                  className={`font-mono uppercase tracking-wider ${
                    reached ? 'text-paper-dim' : 'text-paper-faint'
                  }`}
                  style={{ fontSize: 10 }}
                >
                  {stage.label}
                </span>
              )}
            </div>
            {!isLast && (
              <span
                className="transition-colors duration-300"
                style={{
                  width: compact ? 14 : 28,
                  height: 1.5,
                  marginBottom: compact ? 0 : 18,
                  background: i < currentIndex ? STAGE_COLOR[stage.key] : 'var(--color-graphite-700)',
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
