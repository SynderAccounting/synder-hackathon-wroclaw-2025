import { useState } from 'react';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme';
import { cn } from '@/lib/utils';
import { Menu } from 'lucide-react';

interface NavbarProps {
  className?: string;
  userComponent?: React.ReactNode;
  isLoggedIn?: boolean;
}

const navigationItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/orders', label: 'Orders' },
  { href: '/statistics', label: 'Statistics' },
  { href: '/refunds', label: 'Refunds' },
  { href: '/invoices', label: 'Invoices' },
];

export function Navbar({ className, userComponent, isLoggedIn = false }: NavbarProps) {
  const [open, setOpen] = useState(false);

  return (
    <header
      className={cn(
        'sticky top-0 z-50 w-full border-b transition-colors duration-300 m-0',
        className
      )}
      style={{
        backgroundColor: 'var(--bg)',
        borderColor: 'var(--border)'
      }}
    >
      <div className="container flex h-16 items-center justify-between px-4 mx-auto">
        {/* Logo / Brand with Mobile Menu Button */}
        <div className="flex items-center gap-3">
          {/* Mobile Menu Button - only show when logged in and on small screens */}
          {isLoggedIn && (
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon">
                  <Menu className="h-6 w-6" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-64"
                style={{
                  backgroundColor: 'var(--bg)',
                  borderColor: 'var(--border)'
                }}
              >
                <SheetHeader>
                  <SheetTitle>
                    <span style={{ color: 'var(--color-accent)' }}>SellHub</span>
                  </SheetTitle>
                </SheetHeader>
                <nav className="flex flex-col gap-4 mt-8">
                  {navigationItems.map((item) => (
                    <a
                      key={item.href}
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className={cn(
                        'px-4 py-2 rounded-md text-base font-medium transition-colors',
                        'hover:bg-[var(--bg-light)] hover:text-[var(--color-accent)]',
                        'no-underline'
                      )}
                      style={{ color: 'var(--text)' }}
                    >
                      {item.label}
                    </a>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
          )}

          <a
            href={isLoggedIn ? "/dashboard" : "/"}
            className="flex items-center gap-2 no-underline hover:opacity-80 transition-opacity"
          >
            <h1 className="text-2xl font-bold m-0" style={{ color: 'var(--color-accent)' }}>
              SellHub
            </h1>
          </a>
        </div>

        {/* Desktop Navigation Menu - only show when logged in */}
        {isLoggedIn && (
          <NavigationMenu className="hidden md:flex">
            <NavigationMenuList>
              {navigationItems.map((item) => (
                <NavigationMenuItem key={item.href}>
                  <NavigationMenuLink
                    href={item.href}
                    className={cn(
                      navigationMenuTriggerStyle(),
                      'transition-colors duration-200',
                      'hover:bg-[var(--bg-light)] hover:text-[var(--color-accent)]'
                    )}
                  >
                    {item.label}
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        )}

        {/* User Component & Theme Toggle (always theme toggle on far right) */}
        <div className="flex items-center gap-4">
          {userComponent}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
