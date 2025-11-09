import React from 'react';
import { RefreshCw } from 'lucide-react';

const RefreshButton = ({ onRefresh, isRefreshing, label = 'Refresh', disabled = false }) => {
  const isDisabled = isRefreshing || disabled;
  return (
    <button
      onClick={onRefresh}
      disabled={isDisabled}
      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium hover:shadow-lg hover:shadow-indigo-900/40 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none transition-all active:scale-95"
      title="Click to refresh data"
    >
      <RefreshCw className={`h-4 w-4 transition-transform ${isRefreshing ? 'animate-spin' : ''}`} />
      <span className="text-sm">{isRefreshing ? 'Refreshing...' : label}</span>
    </button>
  );
};

export default RefreshButton;
