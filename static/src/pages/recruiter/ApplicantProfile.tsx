import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  GraduationCap,
  Briefcase,
  Building2,
  GitFork,
  ExternalLink,
  Sparkles,
  Link2,
  Code2,
  Globe,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { api } from '@/lib/api';
import type { User, Experience, Project, Skill, Socials } from '@/types';

function useApplicantData(userId?: string) {
  const profile = useQuery({
    queryKey: ['applicant-profile', userId],
    queryFn: async () => (await api.get<User>(`/users/${userId}`)).data,
    enabled: !!userId,
  });
  const experience = useQuery({
    queryKey: ['applicant-experience', userId],
    queryFn: async () => {
      try {
        return (await api.get<Experience[]>(`/user/${userId}/experience`)).data;
      } catch {
        return [] as Experience[];
      }
    },
    enabled: !!userId,
  });
  const projects = useQuery({
    queryKey: ['applicant-projects', userId],
    queryFn: async () => {
      try {
        return (await api.get<Project[]>(`/user/${userId}/projects`)).data;
      } catch {
        return [] as Project[];
      }
    },
    enabled: !!userId,
  });
  const skills = useQuery({
    queryKey: ['applicant-skills', userId],
    queryFn: async () => {
      try {
        return (await api.get<Skill[]>(`/user/${userId}/skills`)).data;
      } catch {
        return [] as Skill[];
      }
    },
    enabled: !!userId,
  });
  const socials = useQuery({
    queryKey: ['applicant-socials', userId],
    queryFn: async () => {
      try {
        const data = (await api.get<Socials[]>(`/user/${userId}/socials`)).data;
        return data[0] ?? null;
      } catch {
        return null;
      }
    },
    enabled: !!userId,
  });

  return { profile, experience, projects, skills, socials };
}

export function ApplicantProfile() {
  const { userId } = useParams<{ userId: string }>();
  const { profile, experience, projects, skills, socials } = useApplicantData(userId);
  const user = profile.data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-5">
      <Link
        to="/recruiter/posts"
        className="flex w-fit items-center gap-1.5 text-[13px] text-paper-faint transition-colors hover:text-paper"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Back
      </Link>

      {profile.isLoading && <p className="text-[13px] text-paper-faint">Loading profile…</p>}
      {profile.isError && (
        <p className="text-[13px] text-status-rejected">Couldn't load this applicant's profile.</p>
      )}

      {user && (
        <Card className="overflow-hidden">
          <div className="grain h-20 bg-gradient-to-r from-graphite-800 to-graphite-850" />
          <div className="px-6 pb-6">
            <div className="-mt-9 flex h-18 w-18 items-center justify-center overflow-hidden rounded-full border-4 border-graphite-900 bg-graphite-800 font-display text-2xl font-bold text-amber">
              {user.profile_pic ? (
                <img src={user.profile_pic} alt={user.name} className="h-full w-full object-cover" />
              ) : (
                user.name?.[0]?.toUpperCase()
              )}
            </div>
            <h1 className="mt-4 font-display text-xl font-bold tracking-tight text-paper">
              {user.name}
            </h1>
            <p className="mt-1 text-[14px] text-paper-dim">
              {user.headline || user.email}
            </p>
            {user.bio && (
              <p className="mt-3 max-w-2xl text-[13px] leading-relaxed text-paper-dim">
                {user.bio}
              </p>
            )}
            <div className="mt-4 flex flex-wrap items-center gap-4 font-mono text-[11px] uppercase tracking-wider text-paper-faint">
              {user.education && (
                <span className="flex items-center gap-1.5">
                  <GraduationCap className="h-3.5 w-3.5" /> {user.education}
                </span>
              )}
              {user.experience_years != null && (
                <span className="flex items-center gap-1.5">
                  <Briefcase className="h-3.5 w-3.5" /> {user.experience_years} yrs experience
                </span>
              )}
            </div>
          </div>
        </Card>
      )}

      {!!experience.data?.length && (
        <Card className="p-6">
          <h2 className="font-display text-lg font-semibold text-paper">Experience</h2>
          <div className="mt-4 flex flex-col gap-5">
            {experience.data.map((exp) => (
              <div key={exp.id} className="flex gap-3">
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
            ))}
          </div>
        </Card>
      )}

      {!!projects.data?.length && (
        <Card className="p-6">
          <h2 className="font-display text-lg font-semibold text-paper">Projects</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            {projects.data.map((project) => (
              <div key={project.id} className="rounded-md border border-graphite-800 p-4">
                <p className="text-[14px] font-semibold text-paper">{project.title}</p>
                <p className="mt-1 text-[13px] leading-relaxed text-paper-dim">
                  {project.description}
                </p>
                <div className="mt-2 flex gap-3">
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
              </div>
            ))}
          </div>
        </Card>
      )}

      {!!skills.data?.length && (
        <Card className="p-6">
          <h2 className="font-display text-lg font-semibold text-paper">Skills</h2>
          <div className="mt-4 overflow-hidden rounded-lg border border-graphite-800">
            {skills.data.map((skill, i) => (
              <div
                key={skill.id}
                className={`flex items-center gap-2.5 px-4 py-3 ${
                  i !== skills.data!.length - 1 ? 'border-b border-graphite-800' : ''
                }`}
              >
                <Sparkles className="h-3.5 w-3.5 text-amber" />
                <span className="text-[14px] text-paper">{skill.skill_name}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {socials.data && (
        <Card className="p-6">
          <h2 className="font-display text-lg font-semibold text-paper">Elsewhere</h2>
          <div className="mt-4 flex flex-col gap-3">
            {socials.data.github_profile_url && (
              <a
                href={socials.data.github_profile_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-[13px] text-paper-dim hover:text-amber"
              >
                <GitFork className="h-3.5 w-3.5" /> GitHub
              </a>
            )}
            {socials.data.linkedin_profile_url && (
              <a
                href={socials.data.linkedin_profile_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-[13px] text-paper-dim hover:text-amber"
              >
                <Link2 className="h-3.5 w-3.5" /> LinkedIn
              </a>
            )}
            {socials.data.leetcode_profile_url && (
              <a
                href={socials.data.leetcode_profile_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-[13px] text-paper-dim hover:text-amber"
              >
                <Code2 className="h-3.5 w-3.5" /> LeetCode
              </a>
            )}
            {socials.data.portfolio_profile_url && (
              <a
                href={socials.data.portfolio_profile_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-[13px] text-paper-dim hover:text-amber"
              >
                <Globe className="h-3.5 w-3.5" /> Portfolio
              </a>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
