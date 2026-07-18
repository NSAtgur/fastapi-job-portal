import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Logo } from '@/components/Logo';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

type Role = 'user' | 'recruiter';

export function Register() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const initialRole = params.get('role') === 'recruiter' ? 'recruiter' : 'user';

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<Role>(initialRole);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const registerMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/register', { name, email, password, role });
      return data;
    },
    onSuccess: () => navigate('/login'),
    onError: (err: any) => {
      setError(err?.response?.data?.detail || 'Registration failed. Try again.');
    },
  });

  function validate() {
    const errs: Record<string, string> = {};
    if (name.length < 8 || name.length > 15) {
      errs.name = 'Name must be 8–15 characters.';
    }
    if (password.length < 8) {
      errs.password = 'Password must be at least 8 characters.';
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!validate()) return;
    registerMutation.mutate();
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-graphite-950 px-6 py-12">
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
          Create your account
        </h1>
        <p className="mt-1.5 text-[14px] text-paper-dim">
          Track applications or start hiring — pick a lane below.
        </p>

        <div className="mt-6 grid grid-cols-2 gap-2 rounded-md border border-graphite-700 p-1">
          {(['user', 'recruiter'] as Role[]).map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRole(r)}
              className={`h-9 rounded-[5px] text-[13px] font-medium tracking-tight transition-colors ${
                role === r
                  ? 'bg-amber text-graphite-950'
                  : 'text-paper-dim hover:text-paper'
              }`}
            >
              {r === 'user' ? "I'm job hunting" : "I'm hiring"}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
          <Input
            label="Name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={fieldErrors.name}
            hint={!fieldErrors.name ? '8–15 characters' : undefined}
          />
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
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            hint={!fieldErrors.password ? 'At least 8 characters' : undefined}
          />

          {error && (
            <p className="text-[13px] text-status-rejected" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" size="lg" loading={registerMutation.isPending} className="mt-2 w-full">
            Create account
          </Button>
        </form>

        <p className="mt-6 text-center text-[13px] text-paper-faint">
          Already have an account?{' '}
          <Link to="/login" className="text-amber hover:underline">
            Log in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
