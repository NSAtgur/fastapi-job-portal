import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Logo } from '@/components/Logo';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: async () => {
      // /login expects OAuth2PasswordRequestForm: x-www-form-urlencoded
      const body = new URLSearchParams();
      body.set('username', email);
      body.set('password', password);
      const { data } = await api.post<LoginResponse>('/login', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return data;
    },
    onSuccess: async (data) => {
      setAuth(data.access_token);
      try {
        const { data: profile } = await api.get('/users/me/profile');
        useAuthStore.getState().setUser(profile);
        navigate(profile.role === 'recruiter' ? '/recruiter' : profile.role === 'admin' ? '/admin' : '/dashboard/jobs');
      } catch {
        navigate('/dashboard/jobs');
      }
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || 'Something went wrong. Try again.');
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    loginMutation.mutate();
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-graphite-950 px-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-sm"
      >
        <Link to="/" className="mb-8 block w-fit">
          <Logo className="text-base" />
        </Link>

        <h1 className="font-display text-2xl font-bold tracking-tight text-paper">
          Welcome back
        </h1>
        <p className="mt-1.5 text-[14px] text-paper-dim">
          Log in to pick up where you left off.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            label="Password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && (
            <p className="text-[13px] text-status-rejected" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" size="lg" loading={loginMutation.isPending} className="mt-2 w-full">
            Log in
          </Button>
        </form>

        <p className="mt-6 text-center text-[13px] text-paper-faint">
          New to CareerDock?{' '}
          <Link to="/register" className="text-amber hover:underline">
            Create an account
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
