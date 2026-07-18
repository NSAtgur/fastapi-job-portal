import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Socials } from '@/types';

export function SocialsPanel() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    github_profile_url: '',
    linkedin_profile_url: '',
    leetcode_profile_url: '',
    codeforces_profile_url: '',
    portfolio_profile_url: '',
  });

  const { data: socials, isLoading } = useQuery({
    queryKey: ['socials'],
    queryFn: async () => {
      try {
        const { data } = await api.get<Socials[]>('/me/socials');
        return data[0] ?? null;
      } catch {
        return null;
      }
    },
  });

  useEffect(() => {
    if (socials) {
      setForm({
        github_profile_url: socials.github_profile_url || '',
        linkedin_profile_url: socials.linkedin_profile_url || '',
        leetcode_profile_url: socials.leetcode_profile_url || '',
        codeforces_profile_url: socials.codeforces_profile_url || '',
        portfolio_profile_url: socials.portfolio_profile_url || '',
      });
    }
  }, [socials]);

  const updateMutation = useMutation({
    mutationFn: async () => {
      if (!socials) throw new Error('No socials record to update yet.');
      const { data } = await api.put(`/me/socials/${socials.id}`, form);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['socials'] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-display text-lg font-semibold text-paper">Social links</h2>

      {isLoading && <p className="text-[13px] text-paper-faint">Loading…</p>}

      {!isLoading && !socials && (
        <p className="rounded-md border border-dashed border-graphite-700 px-4 py-6 text-[13px] text-paper-faint">
          No social links on file yet. Once a socials record exists for your
          account, you'll be able to edit it here.
        </p>
      )}

      {socials && (
        <div className="flex flex-col gap-4 max-w-md">
          <Input
            label="GitHub"
            value={form.github_profile_url}
            onChange={(e) => setForm({ ...form, github_profile_url: e.target.value })}
          />
          <Input
            label="LinkedIn"
            value={form.linkedin_profile_url}
            onChange={(e) => setForm({ ...form, linkedin_profile_url: e.target.value })}
          />
          <Input
            label="LeetCode"
            value={form.leetcode_profile_url}
            onChange={(e) => setForm({ ...form, leetcode_profile_url: e.target.value })}
          />
          <Input
            label="Codeforces"
            value={form.codeforces_profile_url}
            onChange={(e) => setForm({ ...form, codeforces_profile_url: e.target.value })}
          />
          <Input
            label="Portfolio"
            value={form.portfolio_profile_url}
            onChange={(e) => setForm({ ...form, portfolio_profile_url: e.target.value })}
          />
          <Button
            size="md"
            className="w-fit"
            loading={updateMutation.isPending}
            onClick={() => updateMutation.mutate()}
          >
            Save changes
          </Button>
        </div>
      )}
    </div>
  );
}
