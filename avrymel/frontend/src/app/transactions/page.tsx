'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Transaction, TransactionFilter, PaginatedResponse } from '@/types';
import { transactionsService } from '@/lib/api/transactions';
import { formatCurrency, formatDateTime } from '@/lib/utils';
import { ChevronLeft, ChevronRight, Download, Search, X } from 'lucide-react';

const STATUS_COLORS: Record<string, 'default' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  completed: 'success',
  pending: 'warning',
  failed: 'destructive',
  refunded: 'secondary',
};

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<PaginatedResponse<Transaction> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<TransactionFilter>({});
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters]);

  const loadTransactions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await transactionsService.getTransactions(page, 20, filters);
      setTransactions(data);
    } catch (err: any) {
      setError(err.detail || 'Failed to load transactions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: keyof TransactionFilter, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({});
    setPage(1);
  };

  const handleExport = async () => {
    try {
      const blob = await transactionsService.exportTransactions(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transactions-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert('Failed to export transactions');
    }
  };

  const hasActiveFilters = Object.values(filters).some((v) => v !== undefined && v !== '');

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Transactions</h1>
              <p className="text-muted-foreground">
                View and manage unified transaction data
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
                <Search className="mr-2 h-4 w-4" />
                Filters
              </Button>
              <Button variant="outline" onClick={handleExport}>
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>

          {/* Filters */}
          {showFilters && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Filters</CardTitle>
                  {hasActiveFilters && (
                    <Button variant="ghost" size="sm" onClick={clearFilters}>
                      <X className="mr-1 h-4 w-4" />
                      Clear All
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label>Search</Label>
                    <Input
                      placeholder="Order ID, email, customer..."
                      value={filters.search || ''}
                      onChange={(e) => handleFilterChange('search', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Platform</Label>
                    <Input
                      placeholder="e.g., Shopify, Amazon"
                      value={filters.platform || ''}
                      onChange={(e) => handleFilterChange('platform', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Status</Label>
                    <Input
                      placeholder="e.g., completed, pending"
                      value={filters.status || ''}
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Date From</Label>
                    <Input
                      type="date"
                      value={filters.date_from || ''}
                      onChange={(e) => handleFilterChange('date_from', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Date To</Label>
                    <Input
                      type="date"
                      value={filters.date_to || ''}
                      onChange={(e) => handleFilterChange('date_to', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Min Amount</Label>
                    <Input
                      type="number"
                      placeholder="0"
                      value={filters.min_amount || ''}
                      onChange={(e) => handleFilterChange('min_amount', e.target.value)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Transactions Table */}
          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
                    <p className="mt-2 text-sm text-muted-foreground">Loading transactions...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="p-6">
                  <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {error}
                  </div>
                </div>
              ) : !transactions || transactions.items.length === 0 ? (
                <div className="py-12 text-center text-muted-foreground">
                  No transactions found
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Order ID</TableHead>
                        <TableHead>Platform</TableHead>
                        <TableHead>Customer</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {transactions.items.map((transaction) => (
                        <TableRow key={transaction.id}>
                          <TableCell className="font-medium">
                            {transaction.order_id}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{transaction.platform}</Badge>
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{transaction.customer_name}</div>
                              <div className="text-xs text-muted-foreground">
                                {transaction.customer_email}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            {formatCurrency(transaction.amount, transaction.currency)}
                          </TableCell>
                          <TableCell>
                            <Badge variant={STATUS_COLORS[transaction.status] || 'default'}>
                              {transaction.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{formatDateTime(transaction.created_at)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  <div className="flex items-center justify-between border-t p-4">
                    <div className="text-sm text-muted-foreground">
                      Showing {(page - 1) * 20 + 1} to{' '}
                      {Math.min(page * 20, transactions.total)} of {transactions.total}{' '}
                      transactions
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Previous
                      </Button>
                      <div className="text-sm">
                        Page {page} of {transactions.pages}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => p + 1)}
                        disabled={page >= transactions.pages}
                      >
                        Next
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
