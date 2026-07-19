import type { ApplicationStatus } from '@/types';

const STAGES: { key: ApplicationStatus; label: string }[] = [
  { key: 'Pending', label: 'Pending' },
  { key: 'In Review', label: 'In Review' },
  { key: 'Interview Scheduled', label: 'Interview' },
  { key: 'Accepted', label: 'Accepted' },
];

const STAGE_COLOR: Record<ApplicationStatus, string> = {
  Pending: 'var(--color-status-applied)',
  'In Review': 'var(--color-status-reviewing)',
  'Interview Scheduled': 'var(--color-status-interview)',
  Accepted: 'var(--color-status-offer)',
  Rejected: 'var(--color-status-rejected)',
};

interface StageTrackerProps {
  status: ApplicationStatus;
  compact?: boolean;
}

/**
 * Horizontal stage tracker reflecting the real ApplicationStatus pipeline
 * (Pending -> In Review -> Interview Scheduled -> Accepted), or a terminal
 * "Rejected" state. Used full-size on the Applications page and compact on
 * job cards / applicant rows.
 */
export function StageTracker({ status, compact = false }: StageTrackerProps) {
  if (status === 'Rejected') {
    return (
      <div className="flex items-center gap-2">
        <span
          className="h-2 w-2 rounded-full"
          style={{ background: STAGE_COLOR.Rejected }}
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
