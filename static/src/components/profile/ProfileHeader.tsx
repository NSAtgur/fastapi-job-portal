import { useRef, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Camera, Pencil, GraduationCap, Briefcase, X, Check } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

export function ProfileHeader() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    name: user?.name || '',
    headline: user?.headline || '',
    bio: user?.bio || '',
    education: user?.education || '',
    experience_years: user?.experience_years?.toString() || '',
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const body = new FormData();
      body.append('file', file);
      const { data } = await api.post('/profile/upload', body, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
    onSuccess: (data) => {
      if (user) setUser({ ...user, profile_pic: data.image_url });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.patch('/users/me', {
        name: form.name,
        headline: form.headline,
        bio: form.bio,
        education: form.education,
        experience_years: form.experience_years === '' ? undefined : Number(form.experience_years),
      });
      return data;
    },
    onSuccess: (data) => {
      if (user) setUser({ ...user, ...data });
      queryClient.invalidateQueries();
      setEditing(false);
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
  }

  return (
    <div className="overflow-hidden rounded-lg border border-graphite-800 bg-graphite-900">
      <div className="grain h-24 bg-gradient-to-r from-graphite-800 to-graphite-850" />

      <div className="px-6 pb-6">
        <div className="flex items-end justify-between">
          <div className="relative -mt-10">
            <div className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full border-4 border-graphite-900 bg-graphite-800 font-display text-2xl font-bold text-amber">
              {user?.profile_pic ? (
                <img src={user.profile_pic} alt={user.name} className="h-full w-full object-cover" />
              ) : (
                user?.name?.[0]?.toUpperCase() || '?'
              )}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadMutation.isPending}
              aria-label="Change photo"
              className="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full border border-graphite-700 bg-graphite-800 text-paper-dim transition-colors hover:text-amber"
            >
              <Camera className="h-3 w-3" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {!editing && (
            <Button size="sm" variant="outline" onClick={() => setEditing(true)}>
              <Pencil className="h-3.5 w-3.5" /> Edit
            </Button>
          )}
        </div>

        <div className="mt-4">
          <h1 className="font-display text-xl font-bold tracking-tight text-paper">
            {user?.name}
          </h1>

          {!editing ? (
            <>
              <p className="mt-1 text-[14px] text-paper-dim">
                {user?.headline || 'Add a headline to tell recruiters what you do.'}
              </p>
              {user?.bio && (
                <p className="mt-3 max-w-2xl text-[13px] leading-relaxed text-paper-dim">
                  {user.bio}
                </p>
              )}
              <div className="mt-4 flex flex-wrap items-center gap-4 font-mono text-[11px] uppercase tracking-wider text-paper-faint">
                {user?.education && (
                  <span className="flex items-center gap-1.5">
                    <GraduationCap className="h-3.5 w-3.5" /> {user.education}
                  </span>
                )}
                {user?.experience_years != null && (
                  <span className="flex items-center gap-1.5">
                    <Briefcase className="h-3.5 w-3.5" /> {user.experience_years} yrs experience
                  </span>
                )}
              </div>
            </>
          ) : (
            <div className="mt-4 flex flex-col gap-4">
              <Input
                label="Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
              <Input
                label="Headline"
                value={form.headline}
                onChange={(e) => setForm({ ...form, headline: e.target.value })}
                placeholder="e.g. Backend Engineer · FastAPI & distributed systems"
              />
              <Input
                label="Education"
                value={form.education}
                onChange={(e) => setForm({ ...form, education: e.target.value })}
                placeholder="e.g. B.Tech CS, VIT Bhopal"
              />
              <Input
                label="Years of experience"
                type="number"
                min={0}
                value={form.experience_years}
                onChange={(e) => setForm({ ...form, experience_years: e.target.value })}
              />
              <div className="flex flex-col gap-1.5">
                <label className="text-[13px] font-medium text-paper-dim tracking-wide">Bio</label>
                <textarea
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  rows={3}
                  className="rounded-md border border-graphite-700 bg-graphite-900 px-3 py-2 text-sm text-paper outline-none focus:border-amber"
                />
              </div>

              {updateMutation.isError && (
                <p className="text-[13px] text-status-rejected">
                  {(updateMutation.error as any)?.response?.data?.detail || "Couldn't save changes."}
                </p>
              )}

              <div className="flex gap-2">
                <Button size="sm" loading={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
                  <Check className="h-3.5 w-3.5" /> Save
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
                  <X className="h-3.5 w-3.5" /> Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
