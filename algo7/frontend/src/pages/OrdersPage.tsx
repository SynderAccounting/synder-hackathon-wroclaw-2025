import { useEffect } from 'react';
import { useAuth } from '../contexts';
import { OrdersList } from '../components/OrdersList';

export function OrdersPage() {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      window.history.pushState({}, '', '/login');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  }, [isAuthenticated, isLoading]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div
        className="min-h-screen pt-8 flex items-center justify-center"
        style={{
          backgroundColor: 'var(--bg)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>Loading...</p>
      </div>
    );
  }

  // Don't render content if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div
      className="min-h-screen pt-8"
      style={{
        backgroundColor: 'var(--bg)',
      }}
    >
      <div className="container mx-auto px-4 py-8">
        <h1
          className="text-3xl font-bold mb-6"
          style={{ color: 'var(--text)' }}
        >
          Orders
        </h1>

        <OrdersList />
      </div>
    </div>
  );
}
