import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Trash2, MapPin, Banknote, Plus, Users } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Job } from '@/types';

export function ManagePosts() {
  const queryClient = useQueryClient();

  const { data: posts, isLoading } = useQuery({
    queryKey: ['recruiter-posts'],
    queryFn: async () => {
      const { data } = await api.get<Job[]>('/users/recruiter/posts');
      return data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (jobId: number) => api.delete(`/users/recruiter/posts/delete/${jobId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['recruiter-posts'] }),
  });

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight text-paper">
            Your postings
          </h1>
          <p className="mt-1 text-[14px] text-paper-dim">
            Manage the roles you've published.
          </p>
        </div>
        <Link to="/recruiter/post">
          <Button size="sm">
            <Plus className="h-3.5 w-3.5" /> New posting
          </Button>
        </Link>
      </div>

      <div className="mt-8 flex flex-col gap-3">
        {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}
        {posts?.length === 0 && (
          <p className="rounded-md border border-dashed border-graphite-700 px-4 py-10 text-center text-[13px] text-paper-faint">
            You haven't posted a job yet.
          </p>
        )}

        {posts?.map((job) => (
          <Card key={job.id} className="flex items-center justify-between gap-4 p-5">
            <div>
              <p className="text-[15px] font-semibold text-paper">{job.title}</p>
              <p className="mt-0.5 text-[13px] text-paper-dim">{job.company}</p>
              <div className="mt-2.5 flex flex-wrap items-center gap-3 font-mono text-[11px] text-paper-faint">
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> {job.location}
                </span>
                <span className="flex items-center gap-1">
                  <Banknote className="h-3 w-3" /> ₹{job.salary.toLocaleString('en-IN')}
                </span>
                <span>{job.job_type}</span>
              </div>
            </div>
            <div className="flex flex-shrink-0 items-center gap-2">
              <Link to={`/recruiter/posts/${job.id}/applications`}>
                <Button size="sm" variant="outline">
                  <Users className="h-3.5 w-3.5" /> Applications
                </Button>
              </Link>
              <button
                onClick={() => deleteMutation.mutate(job.id)}
                className="flex-shrink-0 rounded-md p-2 text-paper-faint transition-colors hover:bg-graphite-800 hover:text-status-rejected"
                aria-label="Delete posting"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
