import { useEffect, useRef } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell, X, BellOff } from 'lucide-react';
import { api } from '@/lib/api';
import { groupByRecency } from '@/lib/groupByRecency';
import { useNotificationSeenStore } from '@/store/notificationSeen';
import type { Notification } from '@/types';

const PAGE_SIZE = 15;

function timeAgo(dateStr: string) {
  const diffMs = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diffMs / 60_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

interface NotificationCenterProps {
  open: boolean;
  onClose: () => void;
  onNewestId: (id: number | null) => void;
}

export function NotificationCenter({ open, onClose, onNewestId }: NotificationCenterProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const markSeen = useNotificationSeenStore((s) => s.markSeen);

  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['notifications-feed'],
    queryFn: async ({ pageParam }) => {
      const { data } = await api.get<Notification[]>('/users/me/notifications', {
        params: { skip: pageParam * PAGE_SIZE, limit: PAGE_SIZE },
      });
      return data;
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === PAGE_SIZE ? allPages.length : undefined,
    refetchInterval: open ? false : 30_000,
  });

  const allNotifications = data?.pages.flat() ?? [];

  useEffect(() => {
    onNewestId(allNotifications[0]?.id ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allNotifications[0]?.id]);

  // Mark everything currently loaded as seen shortly after the panel opens.
  useEffect(() => {
    if (open && allNotifications.length) {
      const t = setTimeout(() => markSeen(allNotifications[0].id), 600);
      return () => clearTimeout(t);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, allNotifications[0]?.id]);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    if (open) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open, onClose]);

  const groups = groupByRecency(allNotifications, (n) => n.created_at);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-[1px]"
          />
          <motion.div
            ref={panelRef}
            initial={{ x: 24, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 24, opacity: 0 }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            className="elevated fixed right-4 top-16 z-50 flex max-h-[75vh] w-96 flex-col overflow-hidden rounded-xl border border-graphite-800 bg-graphite-900"
          >
            <div className="flex flex-shrink-0 items-center justify-between border-b border-graphite-800 px-4 py-3.5">
              <span className="font-display text-[14px] font-semibold text-paper">
                Notifications
              </span>
              <button
                onClick={onClose}
                aria-label="Close notifications"
                className="rounded-md p-1 text-paper-faint transition-colors hover:bg-graphite-800 hover:text-paper"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto">
              {isLoading && (
                <div className="flex flex-col gap-3 p-4">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-3 w-3/4 rounded bg-graphite-800" />
                      <div className="mt-2 h-2.5 w-1/4 rounded bg-graphite-800" />
                    </div>
                  ))}
                </div>
              )}

              {isError && (
                <p className="px-4 py-8 text-center text-[13px] text-status-rejected">
                  Couldn't load notifications.
                </p>
              )}

              {!isLoading && !isError && allNotifications.length === 0 && (
                <div className="flex flex-col items-center gap-2 px-4 py-14 text-center">
                  <BellOff className="h-5 w-5 text-paper-faint" />
                  <p className="text-[13px] text-paper-faint">
                    You're all caught up. Nothing here yet.
                  </p>
                </div>
              )}

              {groups.map((group) => (
                <div key={group.label}>
                  <div className="sticky top-0 bg-graphite-900/95 px-4 py-2 backdrop-blur-sm">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-paper-faint">
                      {group.label}
                    </span>
                  </div>
                  {group.items.map((n) => (
                    <div
                      key={n.id}
                      className="border-b border-graphite-800/70 px-4 py-3 transition-colors last:border-0 hover:bg-graphite-850"
                    >
                      <p className="text-[13px] leading-snug text-paper">{n.message}</p>
                      <p className="mt-1 font-mono text-[10.5px] text-paper-faint">
                        {timeAgo(n.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              ))}

              {hasNextPage && (
                <button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="w-full py-3 text-center font-mono text-[11px] uppercase tracking-wider text-paper-faint transition-colors hover:bg-graphite-850 hover:text-amber disabled:opacity-50"
                >
                  {isFetchingNextPage ? 'Loading…' : 'Load earlier'}
                </button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export function NotificationBell({
  onClick,
  hasUnread,
}: {
  onClick: () => void;
  hasUnread: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className="relative rounded-md p-2 text-paper-dim transition-colors hover:bg-graphite-800 hover:text-paper"
      aria-label="Notifications"
    >
      <Bell className="h-4 w-4" />
      {hasUnread && (
        <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-amber ring-2 ring-graphite-900" />
      )}
    </button>
  );
}
