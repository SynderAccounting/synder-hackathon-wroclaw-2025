import { Sun, Moon } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { useTheme } from '@/contexts';
import { cn } from '@/lib/utils';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className="flex items-center gap-2">
      <Sun
        className={cn(
          'w-4 h-4 transition-colors duration-200',
          !isDark ? 'text-[var(--color-accent)]' : 'text-[var(--text-muted)]'
        )}
      />
      <Switch
        checked={isDark}
        onCheckedChange={toggleTheme}
        style={{
          backgroundColor: isDark ? 'var(--color-accent)' : 'var(--border)',
        }}
      />
      <Moon
        className={cn(
          'w-4 h-4 transition-colors duration-200',
          isDark ? 'text-[var(--color-accent)]' : 'text-[var(--text-muted)]'
        )}
      />
    </div>
  );
}
