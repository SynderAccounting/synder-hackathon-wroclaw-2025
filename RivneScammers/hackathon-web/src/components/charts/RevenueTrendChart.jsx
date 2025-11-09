import React from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useSalesTrend } from '../../hooks/api/useAnalytics';
import { features } from '../../config/features';

const RevenueTrendChart = () => {
  const shouldUseBackendAnalytics = features.useBackendAnalytics;
  const { data, isLoading } = useSalesTrend(30, {
    enabled: shouldUseBackendAnalytics,
  });

  if (!shouldUseBackendAnalytics) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
        Enable backend analytics to view live data.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        Loading chart...
      </div>
    );
  }

  const chartData = data?.trend?.map((item) => {
    const dateValue = item?.date ? new Date(item.date) : null;
    const formattedDate = dateValue && !Number.isNaN(dateValue.getTime())
      ? dateValue.toLocaleDateString('en', { month: 'short', day: 'numeric' })
      : 'N/A';

    return {
      date: formattedDate,
      revenue: Number.parseFloat(item?.total_revenue ?? 0) || 0,
    };
  }) ?? [];

  if (chartData.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No revenue trend data.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #6366f1',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
          labelStyle={{ color: '#e2e8f0' }}
        />
        <defs>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="url(#revenueGradient)"
          strokeWidth={2}
          dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default RevenueTrendChart;
