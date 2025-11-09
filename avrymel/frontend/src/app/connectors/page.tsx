'use client';

import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle } from 'lucide-react';

export default function ConnectorsPage() {
  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Connectors</h1>
              <p className="text-muted-foreground">
                Manage data connectors and trigger ingestion jobs
              </p>
            </div>
            {/* Refresh button removed */}
          </div>

          {/* Error display removed */}

          {/* Connector Health Status (Placeholder Data) */}
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Connector Health Status
            </h2>
            <div className="grid gap-4 md:grid-cols-3">
              {/* Amazon */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Amazon</CardTitle>
                    <Badge variant="success" className="bg-green-500">
                      <CheckCircle className="mr-1 h-3 w-3" />
                      Healthy
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Connection:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      OK
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">API Status:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Operational
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Data Sync:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Healthy
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Check:</span>
                    <span className="font-medium">2 min ago</span>
                  </div>
                </CardContent>
              </Card>

              {/* Etsy */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Etsy</CardTitle>
                    <Badge variant="success" className="bg-green-500">
                      <CheckCircle className="mr-1 h-3 w-3" />
                      Healthy
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Connection:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      OK
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">API Status:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Operational
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Data Sync:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Healthy
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Check:</span>
                    <span className="font-medium">5 min ago</span>
                  </div>
                </CardContent>
              </Card>

              {/* Shopify */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Shopify</CardTitle>
                    <Badge variant="success" className="bg-green-500">
                      <CheckCircle className="mr-1 h-3 w-3" />
                      Healthy
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Connection:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      OK
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">API Status:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Operational
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Data Sync:</span>
                    <span className="flex items-center gap-1 text-green-600 font-medium">
                      <CheckCircle className="h-3 w-3" />
                      Healthy
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Check:</span>
                    <span className="font-medium">1 min ago</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
