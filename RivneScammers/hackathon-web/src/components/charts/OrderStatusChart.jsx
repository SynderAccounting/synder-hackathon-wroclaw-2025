import React, { useMemo } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { useOrders } from '../../hooks/api/useOrders';
import { features } from '../../config/features';
import { formatStatus } from '../../utils/formatters';

const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f97316'];

const OrderStatusChart = () => {
  const shouldUseBackendOrders = features.useBackendOrders;
  const { data, isLoading } = useOrders(
    { limit: 100 },
    { enabled: shouldUseBackendOrders },
  );

  const chartData = useMemo(() => {
    if (!data?.orders?.length) return [];
    const statusCounts = data.orders.reduce((acc, order) => {
      const status = formatStatus(order.fulfillmentStatus || order.status || 'unknown');
      acc[status] = (acc[status] ?? 0) + 1;
      return acc;
    }, {});

    return Object.entries(statusCounts).map(([status, count]) => ({
      name: status.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()),
      value: count,
    }));
  }, [data]);

  if (!shouldUseBackendOrders) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
        Enable backend orders to view live data.
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

  if (!chartData.length) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No order status data.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          outerRadius={80}
          dataKey="value"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
        >
          {chartData.map((entry, index) => (
            <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #6366f1',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default OrderStatusChart;
