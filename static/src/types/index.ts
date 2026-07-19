export type Role = 'user' | 'recruiter' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
  profile_pic: string | null;
  is_active: boolean;
  is_verified: boolean;
  experience_years: number | null;
  bio: string | null;
  headline: string | null;
  education: string | null;
  created_at: string;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  salary: number;
  location: string;
  job_type: string;
  created_at: string;
}

export type ApplicationStatus =
  | 'Pending'
  | 'In Review'
  | 'Interview Scheduled'
  | 'Accepted'
  | 'Rejected';

export interface Application {
  id: number;
  user_name: string | null;
  user_id: number;
  job_id: number;
  status: ApplicationStatus;
  applied_at: string;
}

export interface Notification {
  id: number;
  message: string;
  created_at: string;
}

export interface Experience {
  id: number;
  organization_name: string;
  role: string;
  start_date: string;
  end_date: string;
  contribution: string;
  currently_working: boolean;
  skills_used: string | null;
  created_at: string;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  github_link: string;
  live_url: string | null;
  created_at: string;
}

export interface Skill {
  id: number;
  skill_name: string | null;
  created_at: string;
}

export interface Socials {
  id: number;
  github_profile_url: string | null;
  linkedin_profile_url: string | null;
  leetcode_profile_url: string | null;
  codeforces_profile_url: string | null;
  portfolio_profile_url: string | null;
  created_at: string;
}
