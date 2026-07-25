import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, MapPin, Banknote, Briefcase, Lock, Check } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { StageTracker } from '@/components/StageTracker';
import { api } from '@/lib/api';
import type { Job, Application } from '@/types';

export function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const queryClient = useQueryClient();

  const { data: job, isLoading, isError } = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => (await api.get<Job>(`/jobs/${jobId}`)).data,
    enabled: !!jobId,
  });

  // Cross-reference the user's own applications to know if they've already
  // applied here — /jobs/{id} itself doesn't carry that.
  const { data: myApplications } = useQuery({
    queryKey: ['applications'],
    queryFn: async () => {
      try {
        return (await api.get<Application[]>('/users/me/applications')).data;
      } catch {
        return [] as Application[];
      }
    },
  });

  const existingApplication = myApplications?.find((a) => a.job_id === Number(jobId));

  const applyMutation = useMutation({
    mutationFn: async () => (await api.post(`/jobs/${jobId}/apply`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  const isClosed = job?.status === 'Closed';

  return (
    <div className="mx-auto max-w-2xl">
      <Link
        to="/dashboard/jobs"
        className="flex w-fit items-center gap-1.5 text-[13px] text-paper-faint transition-colors hover:text-paper"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Back to search
      </Link>

      {isLoading && <p className="mt-6 text-[13px] text-paper-faint">Loading…</p>}
      {isError && (
        <p className="mt-6 text-[13px] text-status-rejected">Couldn't load this posting.</p>
      )}

      {job && (
        <Card className="mt-4 p-7">
          <div className="flex items-start justify-between gap-4">
            <h1 className="font-display text-2xl font-bold leading-tight tracking-tight text-paper">
              {job.title}
            </h1>
            <Badge tone={isClosed ? 'rejected' : 'offer'}>{job.status}</Badge>
          </div>

          <p className="mt-2 text-[15px] text-paper-dim">{job.company}</p>

          <div className="mt-4 flex flex-wrap items-center gap-4 font-mono text-[12px] text-paper-faint">
            <span className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5" /> {job.location}
            </span>
            <span className="flex items-center gap-1.5">
              <Banknote className="h-3.5 w-3.5" /> ₹{job.salary.toLocaleString('en-IN')}
            </span>
            <span className="flex items-center gap-1.5">
              <Briefcase className="h-3.5 w-3.5" /> {job.job_type}
            </span>
          </div>

          {job.requirements && (
            <div className="mt-6">
              <h2 className="font-display text-[13px] font-semibold uppercase tracking-wider text-paper-faint">
                Full job description
              </h2>
              <p className="mt-3 whitespace-pre-wrap text-[14px] leading-relaxed text-paper-dim">
                {job.requirements}
              </p>
            </div>
          )}

          <div className="mt-7 border-t border-graphite-800 pt-6">
            {existingApplication ? (
              <div>
                <p className="mb-3 text-[13px] text-paper-dim">You've already applied here.</p>
                <StageTracker status={existingApplication.status} />
              </div>
            ) : isClosed ? (
              <div className="flex items-center gap-2.5 text-status-rejected">
                <Lock className="h-4 w-4 flex-shrink-0" />
                <p className="text-[13px]">
                  This position is no longer accepting applications.
                </p>
              </div>
            ) : (
              <Button
                size="lg"
                loading={applyMutation.isPending}
                disabled={applyMutation.isSuccess}
                onClick={() => applyMutation.mutate()}
              >
                {applyMutation.isSuccess ? (
                  <>
                    <Check className="h-4 w-4" /> Applied
                  </>
                ) : (
                  'Apply for this role'
                )}
              </Button>
            )}

            {applyMutation.isError && (
              <p className="mt-3 text-[13px] text-status-rejected">
                {(applyMutation.error as any)?.response?.data?.detail || "Couldn't submit application."}
              </p>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
