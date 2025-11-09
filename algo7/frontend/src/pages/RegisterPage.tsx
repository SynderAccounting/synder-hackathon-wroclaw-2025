import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts';
import type { RegisterCredentials } from '@/features/user';
import { getErrorMessage } from '@/features/user/utils';

export function RegisterPage() {
  const { register } = useAuth();
  const [credentials, setCredentials] = useState<RegisterCredentials>({
    username: '',
    password: '',
    email: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Validate passwords match
    if (credentials.password !== confirmPassword) {
      setError('Passwords do not match. Please try again.');
      setIsLoading(false);
      return;
    }

    // Validate password length
    if (credentials.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      setIsLoading(false);
      return;
    }

    try {
      await register(credentials);
      // Redirect to login page after successful registration
      window.location.href = '/login';
    } catch (err) {
      setError(getErrorMessage(err, 'register'));
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
            Create your account
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Sign up to get started with SellHub
          </p>
        </div>

        {/* Registration Form */}
        <form onSubmit={handleRegister} className="space-y-4">
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
              htmlFor="username"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              Username
            </label>
            <input
              id="username"
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
              placeholder="Enter your username"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              required
              value={credentials.email}
              onChange={(e) =>
                setCredentials({ ...credentials, email: e.target.value })
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
              placeholder="Enter your email"
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

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={cn(
                'w-full px-3 py-2 rounded-md border transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2'
              )}
              style={{
                backgroundColor: 'var(--bg)',
                borderColor: 'var(--border)',
                color: 'var(--text)',
              }}
              placeholder="Confirm your password"
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
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        {/* Sign In Link */}
        <div className="mt-4 text-center text-sm">
          <span style={{ color: 'var(--text-muted)' }}>
            Already have an account?{' '}
          </span>
          <a
            href="/login"
            className="font-medium hover:underline"
            style={{ color: 'var(--color-accent)' }}
          >
            Sign in
          </a>
        </div>
      </div>
    </div>
  );
}
