import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';
import type { Skill } from '@/types';

export function SkillsPanel() {
  const queryClient = useQueryClient();
  const [skillName, setSkillName] = useState('');

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
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (skillName.trim()) addMutation.mutate();
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-display text-lg font-semibold text-paper">Skills</h2>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          placeholder="e.g. FastAPI"
          value={skillName}
          onChange={(e) => setSkillName(e.target.value)}
          className="max-w-xs"
        />
        <Button type="submit" size="md" loading={addMutation.isPending}>
          <Plus className="h-3.5 w-3.5" /> Add
        </Button>
      </form>

      {addMutation.isError && (
        <p className="text-[13px] text-status-rejected">
          {(addMutation.error as any)?.response?.data?.detail || "Couldn't add skill."}
        </p>
      )}

      {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}

      <div className="flex flex-wrap gap-2">
        {skills?.map((skill) => (
          <Badge key={skill.id} tone="amber">
            {skill.skill_name}
          </Badge>
        ))}
        {skills?.length === 0 && (
          <p className="text-[13px] text-paper-faint">No skills added yet.</p>
        )}
      </div>
    </div>
  );
}
