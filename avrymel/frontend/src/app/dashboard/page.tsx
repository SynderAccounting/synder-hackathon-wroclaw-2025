'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { dashboardService } from '@/lib/api/dashboard';
import { DashboardMetrics } from '@/types';
import {
  Receipt,
  Cable,
  MessageSquare,
  Activity,
  Settings,
  Users,
  TrendingUp,
  DollarSign,
  ShoppingCart,
  Zap,
  ArrowRight
} from 'lucide-react';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await dashboardService.getMetrics();
        setMetrics(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err);
        setError('Failed to load dashboard metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const stats = metrics ? [
    {
      name: 'Total Revenue',
      value: formatCurrency(metrics.total_revenue),
      change: `${formatCurrency(metrics.revenue_today)} today`,
      icon: DollarSign,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      name: 'Transactions',
      value: formatNumber(metrics.total_transactions),
      change: `${formatNumber(metrics.transactions_today)} today`,
      icon: ShoppingCart,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      name: 'Active Connectors',
      value: metrics.active_connectors.toString(),
      change: 'All operational',
      icon: Cable,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
      name: 'Pending Jobs',
      value: metrics.pending_jobs.toString(),
      change: 'In progress',
      icon: Zap,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    },
  ] : [];

  const mainActions = [
    {
      name: 'Chat Assistant',
      description: 'Ask questions about your retail data',
      href: '/chat',
      icon: MessageSquare,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      hoverBg: 'hover:bg-blue-100 dark:hover:bg-blue-900/40',
      featured: true,
    },
    {
      name: 'Manage Connectors',
      description: 'Configure data source connections',
      href: '/connectors',
      icon: Cable,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      hoverBg: 'hover:bg-purple-100 dark:hover:bg-purple-900/40',
    },
    {
      name: 'System Health',
      description: 'Monitor API, database, and workers',
      href: '/health',
      icon: Activity,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      hoverBg: 'hover:bg-green-100 dark:hover:bg-green-900/40',
    },
    {
      name: 'Settings',
      description: 'Update your profile and preferences',
      href: '/settings',
      icon: Settings,
      color: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-50 dark:bg-gray-800',
      hoverBg: 'hover:bg-gray-100 dark:hover:bg-gray-700',
    },
    {
      name: 'Admin Panel',
      description: 'Manage users and permissions',
      href: '/admin',
      icon: Users,
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      hoverBg: 'hover:bg-red-100 dark:hover:bg-red-900/40',
    },
  ];

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Welcome to your retail data unification platform
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-lg border bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800 animate-pulse"
                >
                  <div className="flex items-center justify-between">
                    <div className="h-12 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                    <div className="text-right space-y-2">
                      <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  </div>
                </div>
              ))
            ) : error ? (
              // Error state
              <div className="col-span-full rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-900/20">
                <p className="text-red-600 dark:text-red-400">{error}</p>
              </div>
            ) : (
              // Stats cards
              stats.map((stat) => (
                <div
                  key={stat.name}
                  className="rounded-lg border bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
                >
                  <div className="flex items-center justify-between">
                    <div className={`rounded-lg p-3 ${stat.bgColor}`}>
                      <stat.icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {stat.name}
                      </p>
                      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                        {stat.value}
                      </p>
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {stat.change}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Main Actions */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Quick Access
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {mainActions.map((action) => (
                <Link
                  key={action.name}
                  href={action.href}
                  className={`group relative rounded-lg border p-6 transition-all ${action.bgColor} ${action.hoverBg} dark:border-gray-700 ${
                    action.featured ? 'ring-2 ring-blue-500 dark:ring-blue-400' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className={`inline-flex rounded-lg p-3 ${action.bgColor}`}>
                        <action.icon className={`h-6 w-6 ${action.color}`} />
                      </div>
                      <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
                        {action.name}
                      </h3>
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {action.description}
                      </p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors" />
                  </div>
                  {action.featured && (
                    <div className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                      NEW
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </div>

          {/* Info Banner */}
          <div className="rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 border border-blue-200 dark:border-blue-800">
            <div className="flex items-start">
              <TrendingUp className="h-6 w-6 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div className="ml-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Platform Status
                </h3>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  All systems operational. Backend running at localhost:8000. Click Chat Assistant to start asking questions about your data.
                </p>
              </div>
            </div>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
