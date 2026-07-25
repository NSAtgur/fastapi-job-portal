import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { Socials } from '@/types';

const EMPTY_FORM = {
  github_profile_url: '',
  linkedin_profile_url: '',
  leetcode_profile_url: '',
  codeforces_profile_url: '',
  portfolio_profile_url: '',
};

export function SocialsPanel() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(EMPTY_FORM);

  const { data: socials, isLoading } = useQuery({
    queryKey: ['socials'],
    queryFn: async () => {
      try {
        const { data } = await api.get<Socials[]>('/users/me/socials');
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

  // PATCH /me/socials upserts: creates the record on first save, updates after.
  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = Object.fromEntries(
        Object.entries(form).filter(([, v]) => v.trim() !== '')
      );
      const { data } = await api.patch('/users/me/socials', payload);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['socials'] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-display text-lg font-semibold text-paper">Social links</h2>

      {isLoading ? (
        <p className="text-[13px] text-paper-faint">Loading…</p>
      ) : (
        <div className="flex max-w-md flex-col gap-4">
          <Input
            label="GitHub"
            placeholder="https://github.com/username"
            value={form.github_profile_url}
            onChange={(e) => setForm({ ...form, github_profile_url: e.target.value })}
          />
          <Input
            label="LinkedIn"
            placeholder="https://linkedin.com/in/username"
            value={form.linkedin_profile_url}
            onChange={(e) => setForm({ ...form, linkedin_profile_url: e.target.value })}
          />
          <Input
            label="LeetCode"
            placeholder="https://leetcode.com/username"
            value={form.leetcode_profile_url}
            onChange={(e) => setForm({ ...form, leetcode_profile_url: e.target.value })}
          />
          <Input
            label="Codeforces"
            placeholder="https://codeforces.com/profile/username"
            value={form.codeforces_profile_url}
            onChange={(e) => setForm({ ...form, codeforces_profile_url: e.target.value })}
          />
          <Input
            label="Portfolio"
            placeholder="https://yourname.dev"
            value={form.portfolio_profile_url}
            onChange={(e) => setForm({ ...form, portfolio_profile_url: e.target.value })}
          />

          {saveMutation.isError && (
            <p className="text-[13px] text-status-rejected">
              {(saveMutation.error as any)?.response?.data?.detail || "Couldn't save social links."}
            </p>
          )}

          <Button
            size="md"
            className="w-fit"
            loading={saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            Save changes
          </Button>
        </div>
      )}
    </div>
  );
}
