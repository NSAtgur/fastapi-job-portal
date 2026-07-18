import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { UserX, UserCheck } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { User } from '@/types';

export function AdminUsers() {
  const queryClient = useQueryClient();

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const { data } = await api.get<User[]>('/admin/users');
      return data;
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: async (userId: number) =>
      api.patch('/admin/user/deactivate', null, { params: { user_id: userId } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] }),
  });

  const activateMutation = useMutation({
    mutationFn: async (userId: number) =>
      api.patch('/admin/user/activate', null, { params: { user_id: userId } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] }),
  });

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="font-display text-2xl font-bold tracking-tight text-paper">Users</h1>
      <p className="mt-1 text-[14px] text-paper-dim">
        Manage account access across CareerDock.
      </p>

      <Card className="mt-6 overflow-hidden">
        <table className="w-full text-left text-[13px]">
          <thead>
            <tr className="border-b border-graphite-800 text-paper-faint">
              <th className="px-5 py-3 font-mono text-[11px] font-medium uppercase tracking-wider">Name</th>
              <th className="px-5 py-3 font-mono text-[11px] font-medium uppercase tracking-wider">Email</th>
              <th className="px-5 py-3 font-mono text-[11px] font-medium uppercase tracking-wider">Role</th>
              <th className="px-5 py-3 font-mono text-[11px] font-medium uppercase tracking-wider">Status</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-paper-faint">
                  Loading…
                </td>
              </tr>
            )}
            {users?.map((u) => (
              <tr key={u.id} className="border-b border-graphite-800 last:border-0">
                <td className="px-5 py-3 text-paper">{u.name}</td>
                <td className="px-5 py-3 text-paper-dim">{u.email}</td>
                <td className="px-5 py-3">
                  <Badge tone="neutral">{u.role}</Badge>
                </td>
                <td className="px-5 py-3">
                  <Badge tone={u.is_active ? 'offer' : 'rejected'}>
                    {u.is_active ? 'Active' : 'Deactivated'}
                  </Badge>
                </td>
                <td className="px-5 py-3 text-right">
                  {u.is_active ? (
                    <Button
                      size="sm"
                      variant="danger"
                      loading={deactivateMutation.isPending && deactivateMutation.variables === u.id}
                      onClick={() => deactivateMutation.mutate(u.id)}
                    >
                      <UserX className="h-3.5 w-3.5" /> Deactivate
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      loading={activateMutation.isPending && activateMutation.variables === u.id}
                      onClick={() => activateMutation.mutate(u.id)}
                    >
                      <UserCheck className="h-3.5 w-3.5" /> Activate
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
