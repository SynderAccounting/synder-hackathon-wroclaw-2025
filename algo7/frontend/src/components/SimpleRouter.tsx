import { useEffect, useState } from 'react';

interface Route {
  path: string;
  component: React.ComponentType;
}

interface SimpleRouterProps {
  routes: Route[];
  notFound?: React.ComponentType;
}

export function SimpleRouter({ routes, notFound: NotFound }: SimpleRouterProps) {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const route = routes.find((r) => r.path === currentPath);

  if (route) {
    const Component = route.component;
    return <Component />;
  }

  if (NotFound) {
    return <NotFound />;
  }

  return <div>404 - Page Not Found</div>;
}
