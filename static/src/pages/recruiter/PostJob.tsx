import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';

const JOB_TYPES = ['Full-time', 'Part-time', 'Internship', 'Contract'];

export function PostJob() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '',
    company: '',
    salary: '',
    location: '',
    job_type: JOB_TYPES[0],
    requirements: '',
  });
  const [error, setError] = useState<string | null>(null);

  const postMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/jobs', {
        title: form.title,
        company: form.company,
        salary: Number(form.salary),
        location: form.location,
        job_type: form.job_type,
        requirements: form.requirements || undefined,
      });
      return data;
    },
    onSuccess: () => navigate('/recruiter/posts'),
    onError: (err: any) => setError(err?.response?.data?.detail || 'Could not post job.'),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    postMutation.mutate();
  }

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="font-display text-2xl font-bold tracking-tight text-paper">
        Post a job
      </h1>
      <p className="mt-1 text-[14px] text-paper-dim">
        This goes out to every active job seeker on CareerDock.
      </p>

      <Card className="mt-6 p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Job title"
            hint="8–20 characters"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <Input
            label="Company"
            hint="8–30 characters"
            required
            value={form.company}
            onChange={(e) => setForm({ ...form, company: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Salary (₹/yr)"
              type="number"
              required
              value={form.salary}
              onChange={(e) => setForm({ ...form, salary: e.target.value })}
            />
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] font-medium text-paper-dim tracking-wide">
                Job type
              </label>
              <select
                value={form.job_type}
                onChange={(e) => setForm({ ...form, job_type: e.target.value })}
                className="h-10 rounded-md border border-graphite-700 bg-graphite-900 px-3 text-sm text-paper outline-none focus:border-amber"
              >
                {JOB_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <Input
            label="Location"
            hint="8+ characters, e.g. Remote / Bengaluru, India"
            required
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
          />

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-paper-dim tracking-wide">
              Full job description
            </label>
            <textarea
              value={form.requirements}
              onChange={(e) => setForm({ ...form, requirements: e.target.value })}
              rows={8}
              placeholder="Responsibilities, required skills, experience level, anything a candidate needs to know before applying…"
              className="rounded-md border border-graphite-700 bg-graphite-900 px-3 py-2.5 text-sm leading-relaxed text-paper outline-none placeholder:text-paper-faint focus:border-amber"
            />
            <span className="text-[12px] text-paper-faint">
              Shows on the job's detail page under "Full job description."
            </span>
          </div>

          {error && <p className="text-[13px] text-status-rejected">{error}</p>}

          <Button type="submit" size="lg" loading={postMutation.isPending} className="mt-2 w-fit">
            Publish posting
          </Button>
        </form>
      </Card>
    </div>
  );
}
