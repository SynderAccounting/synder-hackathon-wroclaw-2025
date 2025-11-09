'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { HealthStatus, ComponentHealth } from '@/types';
import { healthService } from '@/lib/api/health';
import { formatDateTime } from '@/lib/utils';
import { Server, Database, Cpu, RefreshCw, CheckCircle, AlertCircle, XCircle } from 'lucide-react';

const STATUS_ICONS = {
  up: CheckCircle,
  down: XCircle,
  degraded: AlertCircle,
};

const STATUS_COLORS: Record<string, 'success' | 'warning' | 'destructive'> = {
  up: 'success',
  degraded: 'warning',
  down: 'destructive',
};

const OVERALL_STATUS_COLORS: Record<string, 'success' | 'warning' | 'destructive'> = {
  healthy: 'success',
  degraded: 'warning',
  unhealthy: 'destructive',
};

interface ComponentCardProps {
  title: string;
  icon: React.ElementType;
  health: ComponentHealth;
}

function ComponentCard({ title, icon: Icon, health }: ComponentCardProps) {
  const StatusIcon = STATUS_ICONS[health.status];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <Icon className="h-8 w-8 text-primary" />
          <Badge variant={STATUS_COLORS[health.status]}>
            {health.status}
          </Badge>
        </div>
        <CardTitle className="mt-4">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          {health.latency_ms !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Latency:</span>
              <span className="font-medium">{health.latency_ms}ms</span>
            </div>
          )}
          {health.details && (
            <div className="mt-2">
              <span className="text-muted-foreground">Details:</span>
              <p className="mt-1 text-xs">{health.details}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await healthService.getHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err.detail || 'Failed to load health status');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
              <p className="mt-2 text-sm text-muted-foreground">Checking system health...</p>
            </div>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">System Health</h1>
              <p className="text-muted-foreground">
                Monitor the status of all system components
              </p>
            </div>
            <Button onClick={loadHealth}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>

          {error ? (
            <div className="rounded-md bg-destructive/10 p-4 text-destructive">
              {error}
            </div>
          ) : health ? (
            <>
              {/* Overall Status */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Overall System Status</CardTitle>
                      <CardDescription>
                        Last checked: {formatDateTime(health.timestamp)}
                      </CardDescription>
                    </div>
                    <Badge variant={OVERALL_STATUS_COLORS[health.status]} className="text-lg px-4 py-2">
                      {health.status}
                    </Badge>
                  </div>
                </CardHeader>
              </Card>

              {/* Component Health */}
              <div>
                <h2 className="text-xl font-semibold mb-4">Component Status</h2>
                <div className="grid gap-4 md:grid-cols-3">
                  <ComponentCard
                    title="API Server"
                    icon={Server}
                    health={health.api}
                  />
                  <ComponentCard
                    title="Database"
                    icon={Database}
                    health={health.database}
                  />
                  <ComponentCard
                    title="Workers"
                    icon={Cpu}
                    health={health.workers}
                  />
                </div>
              </div>

              {/* Status Explanation */}
              <Card>
                <CardHeader>
                  <CardTitle>Status Indicators</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-3">
                      <Badge variant="success">Healthy</Badge>
                      <span className="text-muted-foreground">
                        All systems are operational
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="warning">Degraded</Badge>
                      <span className="text-muted-foreground">
                        Some components are experiencing issues but the system is still functional
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="destructive">Unhealthy</Badge>
                      <span className="text-muted-foreground">
                        Critical components are down and the system may not function properly
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : null}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
