import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import type { Role } from '@/types';

interface ProtectedRouteProps {
  allow?: Role[];
}

export function ProtectedRoute({ allow }: ProtectedRouteProps) {
  const { accessToken, user } = useAuthStore();

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }
  if (allow && user && !allow.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}
