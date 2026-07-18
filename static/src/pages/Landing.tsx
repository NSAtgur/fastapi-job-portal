import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowUpRight, Briefcase, Users } from 'lucide-react';
import { Logo } from '@/components/Logo';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { StageTracker } from '@/components/StageTracker';

const SAMPLE_JOBS = [
  { title: 'Backend Engineer', company: 'Vector Labs', location: 'Remote', status: 'interview' as const },
  { title: 'Platform Engineer', company: 'Northstar', location: 'Bengaluru', status: 'reviewing' as const },
  { title: 'Systems Developer', company: 'Loom & Co.', location: 'Remote', status: 'applied' as const },
];

export function Landing() {
  return (
    <div className="min-h-screen bg-graphite-950">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <Logo className="text-lg" />
        <nav className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm">Get started</Button>
          </Link>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6">
        <section className="grid grid-cols-1 gap-16 py-16 md:py-24 lg:grid-cols-2 lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          >
            <span className="font-mono text-xs uppercase tracking-[0.2em] text-amber">
              Applications, tracked to the stage
            </span>
            <h1 className="mt-4 font-display text-5xl font-bold leading-[1.05] tracking-tight text-paper md:text-6xl">
              Know exactly<br />where you stand.
            </h1>
            <p className="mt-6 max-w-md text-[15px] leading-relaxed text-paper-dim">
              CareerDock replaces the mystery of "applied, then silence" with a
              pipeline you can actually see — from applied to offer, for every
              role you go after.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/register">
                <Button variant="primary" size="lg">
                  Find your next role
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/register?role=recruiter">
                <Button variant="outline" size="lg">
                  Hire talent
                </Button>
              </Link>
            </div>
            <div className="mt-10 flex items-center gap-6 text-paper-faint">
              <span className="flex items-center gap-2 text-[13px]">
                <Briefcase className="h-3.5 w-3.5" /> Live job pipeline
              </span>
              <span className="flex items-center gap-2 text-[13px]">
                <Users className="h-3.5 w-3.5" /> Built for recruiters &amp; seekers
              </span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15, ease: 'easeOut' }}
          >
            <Card className="grain p-5">
              <div className="mb-4 flex items-center justify-between">
                <span className="font-mono text-[11px] uppercase tracking-widest text-paper-faint">
                  Your applications
                </span>
                <span className="font-mono text-[11px] text-paper-faint">3 active</span>
              </div>
              <div className="flex flex-col divide-y divide-graphite-800">
                {SAMPLE_JOBS.map((job) => (
                  <div key={job.title} className="flex items-center justify-between gap-4 py-4 first:pt-0 last:pb-0">
                    <div>
                      <p className="text-sm font-medium text-paper">{job.title}</p>
                      <p className="font-mono text-[12px] text-paper-faint">
                        {job.company} · {job.location}
                      </p>
                    </div>
                    <StageTracker status={job.status} compact />
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        </section>
      </main>
    </div>
  );
}
