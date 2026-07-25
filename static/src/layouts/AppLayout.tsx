import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Briefcase,
  ClipboardList,
  User,
  LogOut,
  PlusCircle,
  ListChecks,
  Users,
} from 'lucide-react';
import { Logo } from '@/components/Logo';
import { ThemeToggle } from '@/components/ThemeToggle';
import { NotificationBell, NotificationCenter } from '@/components/NotificationCenter';
import { useNotificationSeenStore } from '@/store/notificationSeen';
import { useAuthStore } from '@/store/auth';

const NAV_BY_ROLE: Record<string, { to: string; label: string; icon: typeof Briefcase }[]> = {
  user: [
    { to: '/dashboard/jobs', label: 'Browse jobs', icon: Briefcase },
    { to: '/dashboard/applications', label: 'Applications', icon: ClipboardList },
    { to: '/dashboard/profile', label: 'Profile', icon: User },
  ],
  recruiter: [
    { to: '/recruiter/post', label: 'Post a job', icon: PlusCircle },
    { to: '/recruiter/posts', label: 'Your postings', icon: ListChecks },
    { to: '/dashboard/profile', label: 'Profile', icon: User },
  ],
  admin: [
    { to: '/admin/users', label: 'Users', icon: Users },
    { to: '/dashboard/profile', label: 'Profile', icon: User },
  ],
};

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [notifOpen, setNotifOpen] = useState(false);
  const [newestId, setNewestId] = useState<number | null>(null);
  const lastSeenId = useNotificationSeenStore((s) => s.lastSeenId);

  const navItems = NAV_BY_ROLE[user?.role || 'user'];
  const hasUnread = !!newestId && newestId > lastSeenId;

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="flex min-h-screen bg-graphite-950">
      <aside className="flex w-60 flex-shrink-0 flex-col border-r border-graphite-800 px-4 py-6">
        <div className="px-2">
          <Logo className="text-base" />
        </div>

        <nav className="mt-8 flex flex-1 flex-col gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-md px-3 py-2 text-[13px] font-medium transition-colors ${
                  isActive
                    ? 'bg-graphite-800 text-amber'
                    : 'text-paper-dim hover:bg-graphite-900 hover:text-paper'
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center justify-between border-t border-graphite-800 pt-4">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-graphite-800 font-mono text-[11px] text-amber">
              {user?.name?.[0]?.toUpperCase() || '?'}
            </div>
            <span className="truncate text-[13px] text-paper-dim">{user?.name}</span>
          </div>
          <button
            onClick={handleLogout}
            aria-label="Log out"
            className="flex-shrink-0 rounded-md p-1.5 text-paper-faint transition-colors hover:bg-graphite-800 hover:text-status-rejected"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 flex-shrink-0 items-center justify-between border-b border-graphite-800 px-6">
          <span className="font-mono text-[11px] uppercase tracking-widest text-paper-faint">
            {user?.role === 'recruiter' ? 'Recruiter workspace' : user?.role === 'admin' ? 'Admin console' : 'Job seeker workspace'}
          </span>
          <div className="flex items-center gap-1">
            <ThemeToggle />
            <NotificationBell onClick={() => setNotifOpen((v) => !v)} hasUnread={hasUnread} />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-8 py-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <NotificationCenter
        open={notifOpen}
        onClose={() => setNotifOpen(false)}
        onNewestId={setNewestId}
      />
    </div>
  );
}
