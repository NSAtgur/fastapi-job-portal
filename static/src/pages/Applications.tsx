import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { StageTracker } from '@/components/StageTracker';
import { api } from '@/lib/api';
import type { Application } from '@/types';

export function Applications() {
  const { data: applications, isLoading, isError } = useQuery({
    queryKey: ['applications'],
    queryFn: async () => {
      const { data } = await api.get<Application[]>('/users/me/applications');
      return data;
    },
  });

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-2xl font-bold tracking-tight text-paper">
        Your applications
      </h1>
      <p className="mt-1 text-[14px] text-paper-dim">
        Every stage, in one place — no more wondering.
      </p>

      <div className="mt-8 flex flex-col gap-4">
        {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}
        {isError && (
          <p className="text-[13px] text-status-rejected">Couldn't load your applications.</p>
        )}
        {applications?.length === 0 && (
          <p className="rounded-md border border-dashed border-graphite-700 px-4 py-10 text-center text-[13px] text-paper-faint">
            No applications yet. Head to Browse jobs to get started.
          </p>
        )}

        {applications?.map((app) => (
          <Card key={app.id} className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[15px] font-semibold text-paper">Job #{app.job_id}</p>
                <p className="mt-0.5 font-mono text-[11px] text-paper-faint">
                  Applied {new Date(app.applied_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="mt-6">
              <StageTracker status={app.status} />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
