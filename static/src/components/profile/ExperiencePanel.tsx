import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Building2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Experience } from '@/types';

export function ExperiencePanel() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    organization_name: '',
    role: '',
    start_date: '',
    end_date: '',
    contribution: '',
    currently_working: false,
    skills_used: '',
  });

  const { data: experiences, isLoading } = useQuery({
    queryKey: ['experience'],
    queryFn: async () => {
      const { data } = await api.get<Experience[]>('/me/experience');
      return data ?? [];
    },
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/me/experience', {
        ...form,
        start_date: new Date(form.start_date).toISOString(),
        end_date: form.currently_working
          ? new Date().toISOString()
          : new Date(form.end_date).toISOString(),
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experience'] });
      setShowForm(false);
      setForm({
        organization_name: '',
        role: '',
        start_date: '',
        end_date: '',
        contribution: '',
        currently_working: false,
        skills_used: '',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => api.delete(`/me/experience/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['experience'] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-paper">Experience</h2>
        <Button size="sm" variant="outline" onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-3.5 w-3.5" /> Add
        </Button>
      </div>

      {showForm && (
        <Card className="flex flex-col gap-4 p-5">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Organization"
              value={form.organization_name}
              onChange={(e) => setForm({ ...form, organization_name: e.target.value })}
            />
            <Input
              label="Role"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            />
            <Input
              label="Start date"
              type="date"
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            />
            <Input
              label="End date"
              type="date"
              value={form.end_date}
              disabled={form.currently_working}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 text-[13px] text-paper-dim">
            <input
              type="checkbox"
              checked={form.currently_working}
              onChange={(e) => setForm({ ...form, currently_working: e.target.checked })}
              className="h-3.5 w-3.5 accent-amber"
            />
            I currently work here
          </label>
          <Input
            label="Contribution"
            value={form.contribution}
            onChange={(e) => setForm({ ...form, contribution: e.target.value })}
          />
          <Input
            label="Skills used"
            hint="Comma separated"
            value={form.skills_used}
            onChange={(e) => setForm({ ...form, skills_used: e.target.value })}
          />
          <div className="flex justify-end gap-2">
            <Button size="sm" variant="ghost" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button size="sm" loading={addMutation.isPending} onClick={() => addMutation.mutate()}>
              Save
            </Button>
          </div>
        </Card>
      )}

      {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}
      {experiences?.length === 0 && !showForm && (
        <p className="rounded-md border border-dashed border-graphite-700 px-4 py-8 text-center text-[13px] text-paper-faint">
          No experience added yet.
        </p>
      )}

      {experiences?.map((exp) => (
        <Card key={exp.id} className="flex items-start justify-between gap-4 p-5">
          <div className="flex gap-3">
            <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-md bg-graphite-800 text-amber">
              <Building2 className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[14px] font-semibold text-paper">{exp.role}</p>
              <p className="text-[13px] text-paper-dim">{exp.organization_name}</p>
              <p className="mt-1 font-mono text-[11px] text-paper-faint">
                {new Date(exp.start_date).toLocaleDateString()} —{' '}
                {exp.currently_working ? 'Present' : new Date(exp.end_date).toLocaleDateString()}
              </p>
              {exp.contribution && (
                <p className="mt-2 text-[13px] leading-relaxed text-paper-dim">{exp.contribution}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => deleteMutation.mutate(exp.id)}
            className="flex-shrink-0 rounded-md p-1.5 text-paper-faint transition-colors hover:bg-graphite-800 hover:text-status-rejected"
            aria-label="Delete experience"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </Card>
      ))}
    </div>
  );
}
