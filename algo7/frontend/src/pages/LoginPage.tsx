import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts';
import type { LoginCredentials } from '@/features/user';
import { getErrorMessage } from '@/features/user/utils';

export function LoginPage() {
  const { login } = useAuth();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await login(credentials);
      // Redirect to dashboard after successful login
      window.location.href = '/dashboard';
    } catch (err) {
      setError(getErrorMessage(err, 'login'));
      setIsLoading(false);
    }
  };

  return (
    <div
      className="flex items-center justify-center px-4 pt-8"
      style={{
        backgroundColor: 'var(--bg)',
        minHeight: 'calc(100vh - 64px)' // 64px to wysokość navbara (h-16)
      }}
    >
      <div
        className="w-full max-w-sm rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        {/* Header */}
        <div className="text-center mb-6">
          <h2
            className="text-xl font-semibold mb-2"
            style={{ color: 'var(--text)' }}
          >
            Sign in to your account
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Welcome back to SellHub
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          {/* Error Message */}
          {error && (
            <div
              className="p-3 rounded-md border text-sm"
              style={{
                color: 'var(--danger)',
                borderColor: 'var(--danger)',
                backgroundColor: 'var(--bg)',
              }}
            >
              {error}
            </div>
          )}

          <div>
            <label
              htmlFor="login"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              login Address
            </label>
            <input
              id="login"
              type="text"
              required
              value={credentials.username}
              onChange={(e) =>
                setCredentials({ ...credentials, username: e.target.value })
              }
              className={cn(
                'w-full px-3 py-2 rounded-md border transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2'
              )}
              style={{
                backgroundColor: 'var(--bg)',
                borderColor: 'var(--border)',
                color: 'var(--text)',
              }}
              placeholder="Enter your login"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={credentials.password}
              onChange={(e) =>
                setCredentials({ ...credentials, password: e.target.value })
              }
              className={cn(
                'w-full px-3 py-2 rounded-md border transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2'
              )}
              style={{
                backgroundColor: 'var(--bg)',
                borderColor: 'var(--border)',
                color: 'var(--text)',
              }}
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>
          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={cn(
              'w-full px-4 py-2 rounded-md font-semibold transition-all duration-200',
              'hover:opacity-90 shadow-md hover:shadow-lg',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            style={{
              backgroundColor: 'var(--color-accent)',
              color: 'var(--bg)',
            }}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Sign Up Link */}
        <div className="mt-4 text-center text-sm">
          <span style={{ color: 'var(--text-muted)' }}>
            Don't have an account?{' '}
          </span>
          <a
            href="/register"
            className="font-medium hover:underline"
            style={{ color: 'var(--color-accent)' }}
          >
            Sign up
          </a>
        </div>
      </div>
    </div>
  );
}
