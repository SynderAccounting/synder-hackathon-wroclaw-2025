import { useEffect, useState, useMemo } from 'react';
import { useAuth } from '../contexts';
import { getAllOrders } from '../api/orders';
import type { OrdersDTO } from '../api/orders';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export function StatisticsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const [orders, setOrders] = useState<OrdersDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<string>('');

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      window.history.pushState({}, '', '/login');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  }, [isAuthenticated, isLoading]);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await getAllOrders();
        setOrders(response.orders);

        // Set default month to current month
        const now = new Date();
        const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        setSelectedMonth(currentMonth);

        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load orders');
        console.error('Error fetching orders:', err);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchOrders();
    }
  }, [isAuthenticated]);

  // Get unique months from orders
  const availableMonths = useMemo(() => {
    const monthsSet = new Set<string>();
    orders.forEach((order) => {
      const date = new Date(order.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      monthsSet.add(monthKey);
    });
    return Array.from(monthsSet).sort().reverse();
  }, [orders]);

  // Filter orders by selected month or last 30 days
  const monthOrders = useMemo(() => {
    if (!selectedMonth) return [];

    if (selectedMonth === 'last-30-days') {
      const now = new Date();
      const thirtyDaysAgo = new Date(now);
      thirtyDaysAgo.setDate(now.getDate() - 30);

      return orders.filter((order) => {
        const orderDate = new Date(order.date);
        return orderDate >= thirtyDaysAgo && orderDate <= now;
      });
    }

    return orders.filter((order) => {
      const date = new Date(order.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      return monthKey === selectedMonth;
    });
  }, [orders, selectedMonth]);

  // Prepare daily revenue data for line chart
  const dailyRevenueData = useMemo(() => {
    if (selectedMonth === 'last-30-days') {
      // For last 30 days, use date-based grouping
      const revenueByDate = new Map<string, number>();

      monthOrders.forEach((order) => {
        const date = new Date(order.date);
        const dateKey = `${date.getMonth() + 1}/${date.getDate()}`;
        const profit = (order.shoesPrice - order.shoesProductionPrice) * order.quantity;

        revenueByDate.set(dateKey, (revenueByDate.get(dateKey) || 0) + profit);
      });

      // Create data for last 30 days
      const now = new Date();
      const data = [];
      for (let i = 29; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(now.getDate() - i);
        const dateKey = `${date.getMonth() + 1}/${date.getDate()}`;
        data.push({
          day: dateKey,
          profit: revenueByDate.get(dateKey) || 0,
        });
      }

      return data;
    }

    // For specific month
    const revenueByDay = new Map<number, number>();

    monthOrders.forEach((order) => {
      const date = new Date(order.date);
      const day = date.getDate();
      const profit = (order.shoesPrice - order.shoesProductionPrice) * order.quantity;

      revenueByDay.set(day, (revenueByDay.get(day) || 0) + profit);
    });

    // Get number of days in selected month
    const [year, month] = selectedMonth.split('-').map(Number);
    const daysInMonth = new Date(year, month, 0).getDate();

    // Create data for all days in month
    const data = [];
    for (let day = 1; day <= daysInMonth; day++) {
      data.push({
        day: day.toString(),
        profit: revenueByDay.get(day) || 0,
      });
    }

    return data;
  }, [monthOrders, selectedMonth]);

  // Prepare shoes type data for bar chart
  const shoesTypeData = useMemo(() => {
    const typeCount = new Map<string, number>();

    monthOrders.forEach((order) => {
      const type = order.shoesType;
      typeCount.set(type, (typeCount.get(type) || 0) + order.quantity);
    });

    return Array.from(typeCount.entries())
      .map(([type, count]) => ({
        type,
        count,
      }))
      .sort((a, b) => b.count - a.count);
  }, [monthOrders]);

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

  if (loading) {
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
            Statistics
          </h1>
          <div
            className="rounded-lg shadow-lg border p-6"
            style={{
              backgroundColor: 'var(--bg-light)',
              borderColor: 'var(--border)',
            }}
          >
            <p style={{ color: 'var(--text-muted)' }}>Loading statistics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
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
            Statistics
          </h1>
          <div
            className="rounded-lg shadow-lg border p-6"
            style={{
              backgroundColor: 'var(--bg-light)',
              borderColor: 'var(--border)',
            }}
          >
            <p style={{ color: 'var(--text-error)' }}>Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  const selectedMonthName = selectedMonth === 'last-30-days'
    ? 'Last 30 Days'
    : selectedMonth
    ? new Date(`${selectedMonth}-01`).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
      })
    : '';

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
          Statistics
        </h1>

        {/* Month Selector */}
        <div
          className="rounded-lg shadow border p-4 mb-6"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <div className="flex flex-wrap items-center gap-3">
            <label className="font-medium" style={{ color: 'var(--text)' }}>
              Select Period:
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedMonth('last-30-days')}
                className="px-4 py-2 rounded transition-all font-medium"
                style={{
                  backgroundColor: selectedMonth === 'last-30-days' ? 'var(--info)' : 'var(--bg-light)',
                  color: selectedMonth === 'last-30-days' ? 'white' : 'var(--text)',
                  border: `2px solid ${selectedMonth === 'last-30-days' ? 'var(--info)' : 'var(--border)'}`,
                }}
              >
                Last 30 Days
              </button>
              {availableMonths.map((month) => {
                const [year, monthNum] = month.split('-');
                const monthName = new Date(`${year}-${monthNum}-01`).toLocaleDateString('en-US', {
                  month: 'long',
                  year: 'numeric',
                });

                return (
                  <button
                    key={month}
                    onClick={() => setSelectedMonth(month)}
                    className="px-4 py-2 rounded transition-all font-medium"
                    style={{
                      backgroundColor: selectedMonth === month ? 'var(--info)' : 'var(--bg-light)',
                      color: selectedMonth === month ? 'white' : 'var(--text)',
                      border: `2px solid ${selectedMonth === month ? 'var(--info)' : 'var(--border)'}`,
                    }}
                  >
                    {monthName}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Charts */}
        {selectedMonth && (
          <div className="space-y-6">
            {/* Daily Profit Line Chart */}
            <div
              className="rounded-lg shadow-lg border p-6"
              style={{
                backgroundColor: 'var(--bg-light)',
                borderColor: 'var(--border)',
              }}
            >
              <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text)' }}>
                Daily Profit in {selectedMonthName}
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={dailyRevenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis
                    dataKey="day"
                    stroke="var(--text-muted)"
                    label={{ value: 'Day of Month', position: 'insideBottom', offset: -5, fill: 'var(--text)' }}
                  />
                  <YAxis
                    stroke="var(--text-muted)"
                    label={{ value: 'Profit ($)', angle: -90, position: 'insideLeft', fill: 'var(--text)' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg)',
                      borderColor: 'var(--border)',
                      color: 'var(--text)',
                    }}
                    labelStyle={{ color: 'var(--text)' }}
                  />
                  <Legend wrapperStyle={{ color: 'var(--text)' }} />
                  <Line
                    type="monotone"
                    dataKey="profit"
                    stroke="var(--success)"
                    strokeWidth={2}
                    dot={{ fill: 'var(--success)' }}
                    activeDot={{ r: 8 }}
                    name="Profit"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Shoes Type Bar Chart */}
            <div
              className="rounded-lg shadow-lg border p-6"
              style={{
                backgroundColor: 'var(--bg-light)',
                borderColor: 'var(--border)',
              }}
            >
              <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text)' }}>
                Shoes Sold by Type in {selectedMonthName}
              </h2>
              {shoesTypeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={shoesTypeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis
                      dataKey="type"
                      stroke="var(--text-muted)"
                      label={{ value: 'Shoe Type', position: 'insideBottom', offset: -5, fill: 'var(--text)' }}
                    />
                    <YAxis
                      stroke="var(--text-muted)"
                      label={{ value: 'Quantity Sold', angle: -90, position: 'insideLeft', fill: 'var(--text)' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg)',
                        borderColor: 'var(--border)',
                        color: 'var(--text)',
                      }}
                      labelStyle={{ color: 'var(--text)' }}
                    />
                    <Legend wrapperStyle={{ color: 'var(--text)' }} />
                    <Bar dataKey="count" fill="var(--info)" name="Quantity Sold" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No sales data for this month.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
