import { User, LogOut, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts';
import { tokenStorage } from '../api';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function Login() {
  const { user, isAuthenticated, logout } = useAuth();

  const handleLoginClick = async () => {
    // Check if we have a saved token
    const token = tokenStorage.getToken();

    if (token) {
      try {
        // Try to verify the token
        const response = await fetch('http://localhost:8080/api/v1/authorized/user', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          // Token is valid, redirect to home
          window.location.href = '/';
          return;
        } else {
          // Token is invalid, clear it
          tokenStorage.removeToken();
        }
      } catch (error) {
        // Error verifying token, clear it
        tokenStorage.removeToken();
      }
    }

    // No token or invalid token, redirect to login page
    window.location.href = '/login';
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  if (isAuthenticated && user) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-md transition-all duration-200',
              'border hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2'
            )}
            style={{
              backgroundColor: 'var(--bg-light)',
              borderColor: 'var(--border)',
              color: 'var(--text)',
            }}
          >
            <User className="w-4 h-4" style={{ color: 'var(--color-accent)' }} />
            <span className="text-sm font-medium">{user.name || user.username}</span>
            <ChevronDown className="w-4 h-4" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel style={{ color: 'var(--text)' }}>
            My Account
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <div className="px-2 py-1.5">
            <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>
              {user.name}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              @{user.username}
            </p>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={handleLogout}
            className="cursor-pointer"
            style={{ color: 'var(--danger)' }}
          >
            <LogOut className="w-4 h-4 mr-2" />
            <span>Logout</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <button
      onClick={handleLoginClick}
      className={cn(
        'flex items-center gap-2 px-4 py-2 rounded-md transition-all duration-200',
        'border shadow-sm hover:shadow-md'
      )}
      style={{
        backgroundColor: 'var(--color-accent)',
        borderColor: 'var(--border)',
        color: 'var(--bg)',
      }}
    >
      <User className="w-4 h-4" />
      <span className="text-sm font-semibold">Login</span>
    </button>
  );
}
