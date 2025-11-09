import { useEffect, useState, useMemo } from 'react';
import { getAllOrders } from '../api/orders';
import type { OrdersDTO } from '../api/orders';

type SortField =
  | 'id'
  | 'shoesType'
  | 'shoesSize'
  | 'shoesPrice'
  | 'status'
  | 'date'
  | 'quantity'
  | 'totalPrice'
  | 'totalProfit';
type SortDirection = 'asc' | 'desc';

export function OrdersList() {
  const [orders, setOrders] = useState<OrdersDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('id');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedMonth, setSelectedMonth] = useState<string>('all');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await getAllOrders();
        setOrders(response.orders);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load orders');
        console.error('Error fetching orders:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  // Handle column header click for sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Get unique months from orders
  const availableMonths = useMemo(() => {
    const monthsSet = new Set<string>();
    orders.forEach((order) => {
      const date = new Date(order.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      monthsSet.add(monthKey);
    });
    return Array.from(monthsSet).sort().reverse(); // Most recent first
  }, [orders]);

  // Filter orders by selected month
  const filteredOrders = useMemo(() => {
    if (selectedMonth === 'all') {
      return orders;
    }

    if (selectedMonth === 'last-month') {
      const now = new Date();
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const lastMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);

      return orders.filter((order) => {
        const orderDate = new Date(order.date);
        return orderDate >= lastMonth && orderDate <= lastMonthEnd;
      });
    }

    return orders.filter((order) => {
      const date = new Date(order.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      return monthKey === selectedMonth;
    });
  }, [orders, selectedMonth]);

  // Sort filtered orders based on current sort field and direction
  const sortedOrders = useMemo(() => {
    const sorted = [...filteredOrders].sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      if (sortField === 'totalPrice') {
        aValue = a.shoesPrice * a.quantity;
        bValue = b.shoesPrice * b.quantity;
      } else if (sortField === 'totalProfit') {
        aValue = (a.shoesPrice - a.shoesProductionPrice) * a.quantity;
        bValue = (b.shoesPrice - b.shoesProductionPrice) * a.quantity;
      } else {
        aValue = a[sortField];
        bValue = b[sortField];
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc'
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });

    return sorted;
  }, [filteredOrders, sortField, sortDirection]);

  // Calculate statistics
  const stats = useMemo(() => {
    const totalOrders = sortedOrders.length;
    const totalRevenue = sortedOrders.reduce(
      (sum, order) => sum + order.shoesPrice * order.quantity,
      0
    );
    const totalProfit = sortedOrders.reduce(
      (sum, order) => sum + (order.shoesPrice - order.shoesProductionPrice) * order.quantity,
      0
    );
    const totalItems = sortedOrders.reduce((sum, order) => sum + order.quantity, 0);

    return { totalOrders, totalRevenue, totalProfit, totalItems };
  }, [sortedOrders]);

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'delivered':
        return 'var(--success)';
      case 'pending':
      case 'processing':
        return 'var(--warning)';
      case 'cancelled':
      case 'refunded':
        return 'var(--text-error)';
      default:
        return 'var(--text-muted)';
    }
  };

  // Render sort indicator
  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return (
      <span className="ml-1" style={{ color: 'var(--primary)' }}>
        {sortDirection === 'asc' ? '↑' : '↓'}
      </span>
    );
  };

  if (loading) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>Loading orders...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-error)' }}>Error: {error}</p>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>No orders found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Month Filter */}
      <div
        className="rounded-lg shadow border p-4"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <label className="font-medium" style={{ color: 'var(--text)' }}>
            Filter by Month:
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedMonth('all')}
              className="px-4 py-2 rounded transition-all font-medium"
              style={{
                backgroundColor: selectedMonth === 'all' ? 'var(--info)' : 'var(--bg-light)',
                color: selectedMonth === 'all' ? 'white' : 'var(--text)',
                border: `2px solid ${selectedMonth === 'all' ? 'var(--info)' : 'var(--border)'}`,
              }}
            >
              All Time
            </button>
            <button
              onClick={() => setSelectedMonth('last-month')}
              className="px-4 py-2 rounded transition-all font-medium"
              style={{
                backgroundColor: selectedMonth === 'last-month' ? 'var(--info)' : 'var(--bg-light)',
                color: selectedMonth === 'last-month' ? 'white' : 'var(--text)',
                border: `2px solid ${selectedMonth === 'last-month' ? 'var(--info)' : 'var(--border)'}`,
              }}
            >
              Last Month
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

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Orders
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text)' }}>
            {stats.totalOrders}
          </p>
        </div>

        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Items
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text)' }}>
            {stats.totalItems}
          </p>
        </div>

        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Revenue
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--primary)' }}>
            ${stats.totalRevenue}
          </p>
        </div>

        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Profit
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--success)' }}>
            ${stats.totalProfit}
          </p>
        </div>
      </div>

      {/* Orders Table */}
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text)' }}>
            All Orders ({sortedOrders.length})
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Click column headers to sort
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr
                className="border-b"
                style={{
                  borderColor: 'var(--border)',
                }}
              >
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('id')}
                >
                  Order ID
                  <SortIndicator field="id" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('shoesType')}
                >
                  Shoe Type
                  <SortIndicator field="shoesType" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('shoesSize')}
                >
                  Size
                  <SortIndicator field="shoesSize" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('quantity')}
                >
                  Quantity
                  <SortIndicator field="quantity" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('shoesPrice')}
                >
                  Unit Price
                  <SortIndicator field="shoesPrice" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('totalPrice')}
                >
                  Total Price
                  <SortIndicator field="totalPrice" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('totalProfit')}
                >
                  Profit
                  <SortIndicator field="totalProfit" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('status')}
                >
                  Status
                  <SortIndicator field="status" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('date')}
                >
                  Date
                  <SortIndicator field="date" />
                </th>
                <th className="text-left py-3 px-4" style={{ color: 'var(--text)' }}>
                  Description
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedOrders.map((order) => {
                const totalPrice = order.shoesPrice * order.quantity;
                const totalProfit =
                  (order.shoesPrice - order.shoesProductionPrice) * order.quantity;

                return (
                  <tr
                    key={order.id}
                    className="border-b hover:bg-opacity-50"
                    style={{
                      borderColor: 'var(--border)',
                    }}
                  >
                    <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>
                      #{order.id}
                    </td>
                    <td className="py-3 px-4 font-medium" style={{ color: 'var(--text)' }}>
                      {order.shoesType}
                    </td>
                    <td className="py-3 px-4" style={{ color: 'var(--text)' }}>
                      {order.shoesSize}
                    </td>
                    <td className="py-3 px-4 font-semibold" style={{ color: 'var(--text)' }}>
                      {order.quantity}
                    </td>
                    <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>
                      ${order.shoesPrice}
                    </td>
                    <td className="py-3 px-4 font-semibold" style={{ color: 'var(--primary)' }}>
                      ${totalPrice}
                    </td>
                    <td
                      className="py-3 px-4 font-medium"
                      style={{
                        color: totalProfit > 0 ? 'var(--success)' : 'var(--text-error)',
                      }}
                    >
                      ${totalProfit}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className="px-2 py-1 rounded text-xs font-medium"
                        style={{
                          backgroundColor: `${getStatusColor(order.status)}20`,
                          color: getStatusColor(order.status),
                        }}
                      >
                        {order.status}
                      </span>
                    </td>
                    <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>
                      {new Date(order.date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate" style={{ color: 'var(--text-muted)' }}>
                      {order.description || '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
