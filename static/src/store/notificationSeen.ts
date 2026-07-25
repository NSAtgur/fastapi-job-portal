import { create } from 'zustand';

interface NotificationSeenState {
  lastSeenId: number;
  markSeen: (id: number) => void;
}

const STORAGE_KEY = 'careerdock-last-seen-notification';

function getInitial(): number {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? Number(stored) : 0;
}

// The backend doesn't expose an is_read flag or a mark-read endpoint yet, so
// "unread" here is approximated client-side: anything with a higher id than
// the last one the person actually saw in the panel counts as new. Once the
// backend adds real read-state, this can be swapped for the server value.
export const useNotificationSeenStore = create<NotificationSeenState>((set) => ({
  lastSeenId: getInitial(),
  markSeen: (id) => {
    localStorage.setItem(STORAGE_KEY, String(id));
    set({ lastSeenId: id });
  },
}));
