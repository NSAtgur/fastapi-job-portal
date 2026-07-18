import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Skill } from '@/types';

export function SkillsPanel() {
  const queryClient = useQueryClient();
  const [skillName, setSkillName] = useState('');
  const [showForm, setShowForm] = useState(false);

  const { data: skills, isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: async () => {
      try {
        const { data } = await api.get<Skill[]>('/me/skills');
        return data;
      } catch {
        return [] as Skill[];
      }
    },
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/me/skills', { skill_name: skillName });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skills'] });
      setSkillName('');
      setShowForm(false);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (skillName.trim()) addMutation.mutate();
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="flex items-baseline gap-2 font-display text-lg font-semibold text-paper">
          Skills
          {!!skills?.length && (
            <span className="font-mono text-[12px] font-normal text-paper-faint">
              {skills.length}
            </span>
          )}
        </h2>
        <Button size="sm" variant="outline" onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-3.5 w-3.5" /> Add skill
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            autoFocus
            placeholder="e.g. FastAPI"
            value={skillName}
            onChange={(e) => setSkillName(e.target.value)}
            className="max-w-xs"
          />
          <Button type="submit" size="md" loading={addMutation.isPending}>
            Save
          </Button>
          <Button type="button" size="md" variant="ghost" onClick={() => setShowForm(false)}>
            Cancel
          </Button>
        </form>
      )}

      {addMutation.isError && (
        <p className="text-[13px] text-status-rejected">
          {(addMutation.error as any)?.response?.data?.detail || "Couldn't add skill."}
        </p>
      )}

      {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}

      {!isLoading && skills?.length === 0 && (
        <p className="rounded-md border border-dashed border-graphite-700 px-4 py-8 text-center text-[13px] text-paper-faint">
          No skills added yet. Add the ones you want recruiters to see first —
          order matters less than having the right five or six.
        </p>
      )}

      {!!skills?.length && (
        <div className="overflow-hidden rounded-lg border border-graphite-800">
          {skills.map((skill, i) => (
            <div
              key={skill.id}
              className={`flex items-center justify-between px-4 py-3 ${
                i !== skills.length - 1 ? 'border-b border-graphite-800' : ''
              }`}
            >
              <span className="flex items-center gap-2.5 text-[14px] text-paper">
                <Sparkles className="h-3.5 w-3.5 text-amber" />
                {skill.skill_name}
              </span>
              <span className="font-mono text-[11px] uppercase tracking-wider text-paper-faint">
                #{String(i + 1).padStart(2, '0')}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
