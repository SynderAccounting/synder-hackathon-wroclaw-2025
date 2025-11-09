import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Public paths that don't require authentication
const publicPaths = ['/login', '/register', '/forgot-password'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if current path is public
  const isPublicPath = publicPaths.some(path => pathname === path || pathname.startsWith(path + '/'));

  // Check for authentication token
  const token = request.cookies.get('access_token');
  const isAuthenticated = !!token;

  // If on public path and authenticated, allow through (don't redirect away from login)
  // If on public path and not authenticated, allow through
  if (isPublicPath) {
    return NextResponse.next();
  }

  // If on protected path and not authenticated, redirect to login
  if (!isAuthenticated) {
    const loginUrl = new URL('/login', request.url);
    // Only add 'from' param if not already going to root
    if (pathname !== '/') {
      loginUrl.searchParams.set('from', pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  // Authenticated user on protected path - allow through
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, robots.txt, sitemap.xml
     * - public files (png, jpg, jpeg, gif, svg, ico, webp)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|.*\\.(?:png|jpg|jpeg|gif|svg|ico|webp)$).*)',
  ],
};
