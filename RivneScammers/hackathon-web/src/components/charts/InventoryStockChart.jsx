import React from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

// Theme colors: indigo, purple, pink gradients
const COLORS = [
  '#6366f1', // indigo-500
  '#8b5cf6', // purple-500
  '#a855f7', // purple-600
  '#c026d3', // fuchsia-600
  '#ec4899', // pink-500
  '#4f46e5', // indigo-600
  '#7c3aed', // violet-600
  '#d946ef', // fuchsia-500
];

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div style={{ backgroundColor: '#1e293b', opacity: 1, zIndex: 9999 }} className="border-2 border-indigo-500 rounded-lg px-4 py-3 shadow-xl">
        <p className="text-slate-200 font-medium mb-1">{data.payload.fullName}</p>
        <p className="text-indigo-300 text-sm">
          Stock: <span className="font-bold">{data.value}</span> units
        </p>
        <p className="text-slate-400 text-xs mt-1">
          {((data.value / data.payload.total) * 100).toFixed(1)}% of total
        </p>
      </div>
    );
  }
  return null;
};

const InventoryStockChart = ({ inventoryItems = [] }) => {
  // Group inventory by stock levels
  const chartData = React.useMemo(() => {
    if (!inventoryItems || inventoryItems.length === 0) return [];

    // Group products by name and sum their stock
    const stockByProduct = {};

    inventoryItems.forEach(item => {
      const productName = item.title || 'Unknown Product';
      const variantName = item.variant?.title || 'Default';
      const displayName = variantName !== 'Default' ? `${productName} - ${variantName}` : productName;
      const stock = item.totalAvailable || 0;

      if (stockByProduct[displayName]) {
        stockByProduct[displayName] += stock;
      } else {
        stockByProduct[displayName] = stock;
      }
    });

    // Convert to array and sort by stock level (descending)
    const data = Object.entries(stockByProduct)
      .map(([name, stock]) => ({
        name: name.length > 30 ? name.substring(0, 30) + '...' : name,
        fullName: name,
        value: stock,
      }))
      .filter(item => item.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 8); // Show top 8 products

    // Add total for percentage calculation
    const total = data.reduce((sum, item) => sum + item.value, 0);
    return data.map(item => ({ ...item, total }));
  }, [inventoryItems]);

  if (!chartData.length) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400">
        No inventory data available.
      </div>
    );
  }

  const totalStock = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="relative flex items-center justify-center" style={{ zIndex: 1 }}>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            dataKey="value"
            labelLine={false}
            label={false}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={COLORS[index % COLORS.length]}
                className="hover:opacity-80 transition-opacity cursor-pointer"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} wrapperStyle={{ zIndex: 9999 }} />
        </PieChart>
      </ResponsiveContainer>

      {/* Center text */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ zIndex: 2 }}>
        <div className="text-center">
          <div className="text-3xl font-bold text-slate-200">
            {totalStock}
          </div>
          <div className="text-sm text-slate-400 mt-1">Total Stock</div>
        </div>
      </div>
    </div>
  );
};

export default InventoryStockChart;
