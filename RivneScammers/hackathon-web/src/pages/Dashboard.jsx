import React, { useEffect, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import RefreshButton from '../components/RefreshButton';
import RevenueTrendChart from '../components/charts/RevenueTrendChart';
import InventoryStockChart from '../components/charts/InventoryStockChart';
import { useDashboardStats } from '../hooks/api/useDashboard';
import { useLoading } from '../context/LoadingContext';
import { QUERY_KEYS, ROUTES } from '../constants';
import { formatCurrency, formatDate, formatDateTime } from '../utils/formatters';

const DEFAULT_STATS = {
    revenue: 0,
    orders: 0,
    products: 0,
    customers: 0,
};

const Dashboard = () => {
    const queryClient = useQueryClient();
    const { setIsGlobalLoading, setLoadingMessage } = useLoading();
    const [isRefreshing, setIsRefreshing] = useState(false);

    const {
        data: dashboardData,
        isLoading,
        isError,
        error: errorDetail,
    } = useDashboardStats();

    const stats = dashboardData || DEFAULT_STATS;
    const recentOrders = dashboardData?.recentOrders || [];
    const inventoryItems = dashboardData?.inventoryItems || [];

    const errorMessage = useMemo(() => {
        if (!isError) return null;
        return (
            errorDetail?.message ||
            errorDetail?.response?.data?.detail ||
            'Failed to load dashboard data from Shopify'
        );
    }, [isError, errorDetail]);

    useEffect(() => {
        setIsGlobalLoading(isLoading);
        if (isLoading) {
            setLoadingMessage(isRefreshing ? 'Refreshing dashboard data...' : 'Loading dashboard data...');
        }
    }, [isLoading, isRefreshing, setIsGlobalLoading, setLoadingMessage]);

    useEffect(() => () => setIsGlobalLoading(false), [setIsGlobalLoading]);

    // Auto-refresh on mount
    useEffect(() => {
        handleRefresh();
    }, []);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        setLoadingMessage('Refreshing dashboard data...');
        setIsGlobalLoading(true);
        try {
            await queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ANALYTICS, 'dashboard'] });
        } finally {
            setTimeout(() => {
                setIsRefreshing(false);
                setIsGlobalLoading(false);
            }, 500);
        }
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

    const formatOrderDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        }).format(date);
    };

    return (
        <div className="h-full overflow-hidden flex flex-col p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">Dashboard</h1>
                    <p className="text-sm text-slate-400 mt-1">Monitor your Shopify store performance</p>
                </div>
                <RefreshButton
                    onRefresh={handleRefresh}
                    isRefreshing={isRefreshing || isLoading}
                    disabled={false}
                />
            </div>

            <div className="flex-1 overflow-y-auto space-y-6">
                {isLoading && (
                    <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 p-4 text-sm text-slate-300">
                        Loading latest data from Shopify...
                    </div>
                )}

                {errorMessage && (
                    <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
                        {errorMessage}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <div className="text-sm text-slate-400">Total Revenue</div>
                    <div className="text-2xl font-bold text-slate-200 mt-2">{formatCurrency(stats.revenue)}</div>
                </div>
                <div
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <div className="text-sm text-slate-400">Orders</div>
                    <div className="text-2xl font-bold text-slate-200 mt-2">{stats.orders.toLocaleString()}</div>
                </div>
                <div
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <div className="text-sm text-slate-400">Products</div>
                    <div className="text-2xl font-bold text-slate-200 mt-2">{stats.products.toLocaleString()}</div>
                </div>
                <div
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <div className="text-sm text-slate-400">Customers</div>
                    <div className="text-2xl font-bold text-slate-200 mt-2">{stats.customers.toLocaleString()}</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <section
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <h2 className="text-lg font-semibold text-slate-200 mb-4">Revenue Trend</h2>
                    <RevenueTrendChart />
                </section>

                <section
                    className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                    <h2 className="text-lg font-semibold text-slate-200 mb-4">Products in Stock</h2>
                    <InventoryStockChart inventoryItems={inventoryItems} />
                </section>
            </div>

            <section
                className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-200">Recent Orders</h2>
                    <Link
                        to={ROUTES.ORDERS}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/50 transition-colors"
                    >
                        Go to Orders
                        <ArrowRight className="h-4 w-4" />
                    </Link>
                </div>
                <div className="mt-6 overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-indigo-500/20">
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Order ID</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Order Number</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Customer</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Date</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Amount</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Fulfillment</th>
                                <th className="px-4 py-3 text-sm font-medium text-slate-400">Payment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentOrders.map((order) => (
                                <tr key={order.id ?? order.orderNumber} className="border-b border-indigo-500/20">
                                    <td className="px-4 py-3 font-mono text-indigo-300">{order.id || '—'}</td>
                                    <td className="px-4 py-3 font-medium text-slate-200">{order.orderNumber || order.name || '—'}</td>
                                    <td className="px-4 py-3 text-slate-200">{order.customerName || 'Guest'}</td>
                                    <td className="px-4 py-3 text-slate-400">{formatOrderDate(order.createdAt)}</td>
                                    <td className="px-4 py-3 font-medium text-slate-200">
                                        {formatCurrency(order.total)} {order.currency || ''}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.fulfillmentStatus)}`}>
                                            {order.fulfillmentStatus || 'UNKNOWN'}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.financialStatus)}`}>
                                            {order.financialStatus || 'UNKNOWN'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {!recentOrders.length && !isLoading && (
                                <tr>
                                    <td colSpan={7} className="px-4 py-6 text-center text-slate-400">
                                        No recent orders found. Orders will appear here once you have data from Shopify.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </section>
            </div>
        </div>
    );
};

export default Dashboard;
