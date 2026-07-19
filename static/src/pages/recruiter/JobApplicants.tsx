import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { StageTracker } from '@/components/StageTracker';
import { api } from '@/lib/api';
import type { Application } from '@/types';

export function JobApplicants() {
  const { jobId } = useParams<{ jobId: string }>();

  const { data: applications, isLoading, isError } = useQuery({
    queryKey: ['recruiter-applications', jobId],
    queryFn: async () => {
      const { data } = await api.get<Application[]>(
        `/users/recruiter/posts/${jobId}/applications`
      );
      return data;
    },
    enabled: !!jobId,
  });

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        to="/recruiter/posts"
        className="flex w-fit items-center gap-1.5 text-[13px] text-paper-faint transition-colors hover:text-paper"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Back to postings
      </Link>

      <h1 className="mt-3 font-display text-2xl font-bold tracking-tight text-paper">
        Applicants
      </h1>
      <p className="mt-1 text-[14px] text-paper-dim">
        Everyone who's applied to this role, most recent first.
      </p>

      <div className="mt-8 flex flex-col gap-3">
        {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}
        {isError && (
          <p className="rounded-md border border-dashed border-graphite-700 px-4 py-10 text-center text-[13px] text-paper-faint">
            No applicants yet for this posting.
          </p>
        )}

        {applications?.map((app) => (
          <Card key={app.id} className="flex items-center justify-between gap-4 p-5">
            <div>
              <p className="text-[15px] font-semibold text-paper">
                {app.user_name || `Applicant #${app.user_id}`}
              </p>
              <p className="mt-0.5 font-mono text-[11px] text-paper-faint">
                Applied {new Date(app.applied_at).toLocaleDateString()}
              </p>
              <div className="mt-3">
                <StageTracker status={app.status as any} compact />
              </div>
            </div>
            <Link to={`/recruiter/applicants/${app.user_id}`}>
              <Button size="sm" variant="outline">
                View profile <ExternalLink className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
