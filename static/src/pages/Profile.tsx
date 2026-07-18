import { useState } from 'react';
import { useAuthStore } from '@/store/auth';
import { ExperiencePanel } from '@/components/profile/ExperiencePanel';
import { ProjectsPanel } from '@/components/profile/ProjectsPanel';
import { SkillsPanel } from '@/components/profile/SkillsPanel';
import { SocialsPanel } from '@/components/profile/SocialsPanel';

const TABS = ['Experience', 'Projects', 'Skills', 'Socials'] as const;
type Tab = (typeof TABS)[number];

export function Profile() {
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState<Tab>('Experience');

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-graphite-800 font-display text-xl font-bold text-amber">
          {user?.name?.[0]?.toUpperCase() || '?'}
        </div>
        <div>
          <h1 className="font-display text-xl font-bold tracking-tight text-paper">
            {user?.name}
          </h1>
          <p className="text-[13px] text-paper-dim">{user?.headline || user?.email}</p>
        </div>
      </div>

      <div className="mt-8 flex gap-1 border-b border-graphite-800">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`relative px-4 py-2.5 text-[13px] font-medium transition-colors ${
              tab === t ? 'text-amber' : 'text-paper-dim hover:text-paper'
            }`}
          >
            {t}
            {tab === t && (
              <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-amber" />
            )}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === 'Experience' && <ExperiencePanel />}
        {tab === 'Projects' && <ProjectsPanel />}
        {tab === 'Skills' && <SkillsPanel />}
        {tab === 'Socials' && <SocialsPanel />}
      </div>
    </div>
  );
}
