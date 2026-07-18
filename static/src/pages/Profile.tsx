import { Card } from '@/components/ui/Card';
import { ProfileHeader } from '@/components/profile/ProfileHeader';
import { ExperiencePanel } from '@/components/profile/ExperiencePanel';
import { ProjectsPanel } from '@/components/profile/ProjectsPanel';
import { SkillsPanel } from '@/components/profile/SkillsPanel';
import { SocialsPanel } from '@/components/profile/SocialsPanel';

export function Profile() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-5">
      <ProfileHeader />

      <Card className="p-6">
        <ExperiencePanel />
      </Card>

      <Card className="p-6">
        <ProjectsPanel />
      </Card>

      <Card className="p-6">
        <SkillsPanel />
      </Card>

      <Card className="p-6">
        <SocialsPanel />
      </Card>
    </div>
  );
}
