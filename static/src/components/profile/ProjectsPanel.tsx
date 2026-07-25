import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, GitFork, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Project } from '@/types';

export function ProjectsPanel() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', github_link: '', live_url: '' });

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      try {
        const { data } = await api.get<Project[]>('/users/me/projects');
        return data;
      } catch {
        return [] as Project[];
      }
    },
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/users/me/projects', {
        title: form.title,
        description: form.description,
        github_link: form.github_link,
        live_url: form.live_url || undefined,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setShowForm(false);
      setForm({ title: '', description: '', github_link: '', live_url: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => api.delete(`/users/me/projects/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-paper">Projects</h2>
        <Button size="sm" variant="outline" onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-3.5 w-3.5" /> Add
        </Button>
      </div>

      {showForm && (
        <Card className="flex flex-col gap-4 p-5">
          <Input
            label="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <Input
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <Input
            label="GitHub link"
            value={form.github_link}
            onChange={(e) => setForm({ ...form, github_link: e.target.value })}
          />
          <Input
            label="Live URL"
            hint="Optional"
            value={form.live_url}
            onChange={(e) => setForm({ ...form, live_url: e.target.value })}
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
      {projects?.length === 0 && !showForm && (
        <p className="rounded-md border border-dashed border-graphite-700 px-4 py-8 text-center text-[13px] text-paper-faint">
          No projects added yet.
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {projects?.map((project) => (
          <Card key={project.id} className="flex flex-col gap-2 p-5">
            <div className="flex items-start justify-between">
              <p className="text-[14px] font-semibold text-paper">{project.title}</p>
              <button
                onClick={() => deleteMutation.mutate(project.id)}
                className="flex-shrink-0 rounded-md p-1 text-paper-faint transition-colors hover:bg-graphite-800 hover:text-status-rejected"
                aria-label="Delete project"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
            <p className="text-[13px] leading-relaxed text-paper-dim">{project.description}</p>
            <div className="mt-1 flex gap-3">
              <a
                href={project.github_link}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 font-mono text-[11px] text-paper-faint hover:text-amber"
              >
                <GitFork className="h-3 w-3" /> Source
              </a>
              {project.live_url && (
                <a
                  href={project.live_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 font-mono text-[11px] text-paper-faint hover:text-amber"
                >
                  <ExternalLink className="h-3 w-3" /> Live
                </a>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
