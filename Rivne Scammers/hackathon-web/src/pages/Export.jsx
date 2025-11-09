import { useState } from 'react';
import { getToken } from '../api/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Export = () => {
  const [format, setFormat] = useState('csv');
  const [days, setDays] = useState(30);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleExport = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = getToken();
      if (!token) {
        throw new Error('Please login to export data');
      }

      // Build query parameters
      const params = new URLSearchParams({
        format: format,
        days: days.toString(),
      });

      if (startDate) {
        params.append('start_date', startDate);
      }
      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v1/shopify/export/sales?${params.toString()}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Export failed' }));
        throw new Error(errorData.detail || 'Failed to export data');
      }

      // Get the filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `sales_export_${new Date().toISOString().split('T')[0]}.${format}`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Successfully exported data as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Export error:', err);
      setError(err.message || 'Failed to export data');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">
          Export
        </h1>
        <p className="text-sm text-slate-400 mt-1">Export your sales data in multiple formats</p>
      </div>

      {error && (
        <div className="border border-red-500/20 bg-red-500/10 backdrop-blur-xl p-4 rounded-xl">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="border border-green-500/20 bg-green-500/10 backdrop-blur-xl p-4 rounded-xl">
          <p className="text-green-300 text-sm">{success}</p>
        </div>
      )}

      <section className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Export Sales Data</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Select format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
            >
              <option value="csv">CSV (Comma Separated Values)</option>
              <option value="excel">Excel (XLSX)</option>
              <option value="json">JSON (JavaScript Object Notation)</option>
            </select>
            <p className="text-xs text-slate-400 mt-1">
              {format === 'csv' && 'Best for importing into spreadsheet applications'}
              {format === 'excel' && 'Native Excel format with formatting'}
              {format === 'json' && 'For developers and API integrations'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Time Period (last N days)
            </label>
            <input
              type="number"
              min="1"
              max="365"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value) || 30)}
              className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
              placeholder="30"
            />
            <p className="text-xs text-slate-400 mt-1">Export data from the last {days} days (max 365)</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Custom Date Range (optional)
            </label>
            <div className="flex gap-3">
              <div className="flex-1">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
                  placeholder="Start date"
                />
              </div>
              <div className="flex-1">
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
                  placeholder="End date"
                />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-1">Leave empty to use the time period above</p>
          </div>

          <button
            onClick={handleExport}
            disabled={isLoading}
            className="relative group overflow-hidden px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold shadow-lg shadow-indigo-900/40 transition hover:shadow-indigo-900/50 active:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10">
              {isLoading ? 'Exporting...' : `Export as ${format.toUpperCase()}`}
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
          </button>
        </div>
      </section>

      <section className="border border-slate-500/20 bg-slate-500/10 backdrop-blur-xl p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-slate-200 mb-3">What's included in the export?</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start gap-2">
            <span className="text-indigo-400 mt-0.5">•</span>
            <span><strong>Sales Summary:</strong> Total revenue, order count, and average order value</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400 mt-0.5">•</span>
            <span><strong>Daily Sales Trend:</strong> Revenue breakdown by day</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400 mt-0.5">•</span>
            <span><strong>Top Products:</strong> Best-selling products with revenue and quantity</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400 mt-0.5">•</span>
            <span><strong>Export Metadata:</strong> Export date and period for record-keeping</span>
          </li>
        </ul>
      </section>
    </div>
  );
};

export default Export;
