import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Search, MapPin, Banknote, Briefcase, Check } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Job } from '@/types';

export function Jobs() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const queryClient = useQueryClient();

  const { data: jobs, isLoading, isError } = useQuery({
    queryKey: ['jobs', submittedQuery],
    queryFn: async () => {
      const { data } = await api.get<Job[]>('/search', {
        params: { title: submittedQuery },
      });
      return data;
    },
    enabled: submittedQuery.length > 0,
  });

  const applyMutation = useMutation({
    mutationFn: async (jobId: number) => {
      const { data } = await api.post(`/apply/${jobId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSubmittedQuery(query.trim());
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-2xl font-bold tracking-tight text-paper">
        Browse jobs
      </h1>
      <p className="mt-1 text-[14px] text-paper-dim">
        Search by title to find your next role.
      </p>

      <form onSubmit={handleSearch} className="mt-6 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-paper-faint" />
          <Input
            placeholder="e.g. Backend Engineer"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button type="submit" size="md">
          Search
        </Button>
      </form>

      <div className="mt-6 flex flex-col gap-3">
        {!submittedQuery && (
          <p className="rounded-md border border-dashed border-graphite-700 px-4 py-8 text-center text-[13px] text-paper-faint">
            Search for a role to see open postings.
          </p>
        )}

        {isLoading && (
          <p className="px-1 text-[13px] text-paper-faint">Searching…</p>
        )}

        {isError && (
          <p className="px-1 text-[13px] text-status-rejected">
            Couldn't load jobs. Try again.
          </p>
        )}

        {submittedQuery && jobs?.length === 0 && (
          <p className="rounded-md border border-dashed border-graphite-700 px-4 py-8 text-center text-[13px] text-paper-faint">
            No roles match "{submittedQuery}".
          </p>
        )}

        {jobs?.map((job) => (
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
                <span className="flex items-center gap-1">
                  <Briefcase className="h-3 w-3" /> {job.job_type}
                </span>
              </div>
            </div>
            <Button
              variant={applyMutation.variables === job.id && applyMutation.isSuccess ? 'outline' : 'primary'}
              size="sm"
              loading={applyMutation.isPending && applyMutation.variables === job.id}
              disabled={applyMutation.isSuccess && applyMutation.variables === job.id}
              onClick={() => applyMutation.mutate(job.id)}
            >
              {applyMutation.isSuccess && applyMutation.variables === job.id ? (
                <>
                  <Check className="h-3.5 w-3.5" /> Applied
                </>
              ) : (
                'Apply'
              )}
            </Button>
          </Card>
        ))}
      </div>

      {applyMutation.isError && (
        <p className="mt-3 text-[13px] text-status-rejected">
          {(applyMutation.error as any)?.response?.data?.detail || "Couldn't submit application."}
        </p>
      )}
    </div>
  );
}
