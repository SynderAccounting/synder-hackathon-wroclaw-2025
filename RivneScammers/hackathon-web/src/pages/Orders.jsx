import { useState, useMemo, useEffect } from 'react';
import { Search } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import RefreshButton from '../components/RefreshButton';
import Pagination from '../components/Pagination';
import { useOrders } from '../hooks/api/useOrders';
import { QUERY_KEYS } from '../constants';
import { getOrderAdminUrl } from '../utils/shopify';

const ITEMS_PER_PAGE = 15;

const Orders = () => {
  const queryClient = useQueryClient();
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch orders from API
  const { data, isLoading, isError, refetch, isFetching } = useOrders({
    page: currentPage,
    limit: ITEMS_PER_PAGE,
    search: searchTerm,
    status: statusFilter !== 'all' ? statusFilter : undefined,
  }, {
    refetchOnWindowFocus: false,
    staleTime: 0,
  });

  const orders = data?.orders || [];
  const totalOrders = data?.total || 0;

  // Helper function to check if order is within date range
  const isWithinDateRange = (orderDate, range) => {
    if (!orderDate) return false;

    const now = new Date();
    const orderDateObj = new Date(orderDate);

    switch (range) {
      case 'today': {
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        return orderDateObj >= today;
      }
      case 'week': {
        const weekAgo = new Date(now);
        weekAgo.setDate(now.getDate() - 7);
        return orderDateObj >= weekAgo;
      }
      case 'month': {
        const monthAgo = new Date(now);
        monthAgo.setMonth(now.getMonth() - 1);
        return orderDateObj >= monthAgo;
      }
      default:
        return true;
    }
  };

  // Filter orders locally for search, status, and date
  const filteredOrders = useMemo(() => {
    let filtered = [...orders];

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(order =>
        order.orderNumber?.toLowerCase().includes(searchLower) ||
        order.customerName?.toLowerCase().includes(searchLower) ||
        order.id?.toString().toLowerCase().includes(searchLower)
      );
    }

    // Status filter - улучшенная логика
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => {
        const fulfillment = (order.fulfillmentStatus || '').toLowerCase();
        const financial = (order.financialStatus || '').toLowerCase();
        const filterLower = statusFilter.toLowerCase();

        return fulfillment.includes(filterLower) || financial.includes(filterLower);
      });
    }

    // Date filter
    if (dateFilter !== 'all') {
      filtered = filtered.filter(order => isWithinDateRange(order.createdAt, dateFilter));
    }

    return filtered;
  }, [orders, searchTerm, statusFilter, dateFilter]);

  // Pagination
  const totalPages = Math.ceil(totalOrders / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;

  // Auto-refresh on mount
  useEffect(() => {
    handleRefresh();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Invalidate the cache and refetch
      await queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ORDERS] });
      await refetch();
    } finally {
      // Ensure button shows animation for at least 500ms
      setTimeout(() => {
        setIsRefreshing(false);
      }, 500);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleStatusChange = (value) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  const handleDateChange = (value) => {
    setDateFilter(value);
    setCurrentPage(1);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const getStatusColor = (status) => {
    const statusLower = (status || '').toLowerCase();
    if (statusLower.includes('fulfilled') || statusLower.includes('paid') || statusLower.includes('completed')) {
      return 'bg-green-500/10 text-green-200 border border-green-500/20';
    }
    if (statusLower.includes('pending') || statusLower.includes('unfulfilled')) {
      return 'bg-yellow-500/10 text-yellow-200 border border-yellow-500/20';
    }
    if (statusLower.includes('cancelled') || statusLower.includes('refunded')) {
      return 'bg-rose-500/10 text-rose-200 border border-rose-500/20';
    }
    return 'bg-slate-500/10 text-slate-200 border border-slate-500/20';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">Orders</h1>
          <p className="text-slate-400 mt-1">Manage and analyze your orders</p>
        </div>
        <RefreshButton
          onRefresh={handleRefresh}
          isRefreshing={isLoading || isFetching || isRefreshing}
          disabled={isLoading || isFetching}
        />
      </div>

      {/* Filters and Search */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              type="search"
              placeholder="Search by order number, customer name, or ID..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
            />
          </div>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="px-4 py-2 rounded-xl bg-slate-800 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition cursor-pointer hover:border-indigo-500/40"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" className="bg-slate-800 text-slate-200">All Status</option>
          <option value="pending" className="bg-slate-800 text-slate-200">Pending</option>
          <option value="paid" className="bg-slate-800 text-slate-200">Paid</option>
          <option value="cancelled" className="bg-slate-800 text-slate-200">Cancelled</option>
          <option value="refunded" className="bg-slate-800 text-slate-200">Refunded</option>
        </select>

        <select
          value={dateFilter}
          onChange={(e) => handleDateChange(e.target.value)}
          className="px-4 py-2 rounded-xl bg-slate-800 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition cursor-pointer hover:border-indigo-500/40"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" className="bg-slate-800 text-slate-200">All Time</option>
          <option value="today" className="bg-slate-800 text-slate-200">Today</option>
          <option value="week" className="bg-slate-800 text-slate-200">This Week</option>
          <option value="month" className="bg-slate-800 text-slate-200">This Month</option>
        </select>
      </div>

      {/* Orders Table */}
      <div className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-r-transparent"></div>
              <p className="text-slate-400 mt-4">Loading orders...</p>
            </div>
          </div>
        ) : isError ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <p className="text-rose-400 text-lg">Failed to load orders</p>
              <p className="text-slate-500 text-sm mt-1">Please try refreshing the page</p>
              <button
                onClick={handleRefresh}
                className="mt-4 px-4 py-2 rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition"
              >
                Retry
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-indigo-500/20">
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Order ID</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Order Number</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Customer</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Created At</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Amount</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Fulfillment</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Payment</th>
                  <th className="px-4 py-3 text-sm font-medium text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order) => (
                  <tr key={order.id} className="border-b border-indigo-500/20">
                    <td className="px-4 py-3 font-mono text-indigo-300">{order.id || '—'}</td>
                    <td className="px-4 py-3 font-medium text-slate-200">{order.orderNumber}</td>
                    <td className="px-4 py-3 text-slate-200">{order.customerName}</td>
                    <td className="px-4 py-3 text-slate-400">{formatDate(order.createdAt)}</td>
                    <td className="px-4 py-3 font-medium text-slate-200">
                      {order.total.toFixed(2)} {order.currency}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.fulfillmentStatus)}`}>
                        {order.fulfillmentStatus}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.financialStatus)}`}>
                        {order.financialStatus}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => window.open(getOrderAdminUrl(order), '_blank')}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/50 transition-colors"
                        title={`Open order ${order.id} in Shopify`}
                      >
                        Open in Shopify
                      </button>
                    </td>
                  </tr>
                ))}
                {!filteredOrders.length && !isLoading && (
                  <tr>
                    <td colSpan={8} className="px-4 py-6 text-center text-slate-400">
                      No orders found. {searchTerm || statusFilter !== 'all' ? 'Try adjusting your filters.' : 'Orders will appear here once you have data.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Bottom */}
      {!isLoading && totalOrders > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalOrders}
          startIndex={startIndex}
          endIndex={endIndex}
          onPageChange={setCurrentPage}
          itemName="orders"
        />
      )}
    </div>
  );
};

export default Orders;
