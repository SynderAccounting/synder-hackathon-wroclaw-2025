import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const Pagination = ({
  currentPage,
  totalPages,
  totalItems,
  startIndex,
  endIndex,
  onPageChange,
  itemName = 'items'
}) => {
  const hasNextPage = currentPage < totalPages;
  const hasPrevPage = currentPage > 1;

  const handleNextPage = () => {
    if (hasNextPage) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (hasPrevPage) {
      onPageChange(currentPage - 1);
    }
  };

  return (
    <div className="flex items-center justify-between">
      <div className="text-sm text-slate-400">
        Showing <span className="font-medium text-slate-300">{startIndex + 1}</span> to{' '}
        <span className="font-medium text-slate-300">{Math.min(endIndex, totalItems)}</span> of{' '}
        <span className="font-medium text-slate-300">{totalItems}</span> {itemName}
        <span className="ml-2">
          (Page {currentPage} of {totalPages})
        </span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handlePrevPage}
          disabled={!hasPrevPage}
          className="flex items-center gap-1 px-4 py-2 rounded-lg bg-slate-900/50 border border-indigo-500/20 text-slate-200 hover:bg-slate-800/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>

        <div className="flex items-center gap-1">
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }

            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                className={`px-3 py-2 rounded-lg transition ${
                  currentPage === pageNum
                    ? 'bg-indigo-500 text-white'
                    : 'bg-slate-900/50 border border-indigo-500/20 text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        <button
          onClick={handleNextPage}
          disabled={!hasNextPage}
          className="flex items-center gap-1 px-4 py-2 rounded-lg bg-slate-900/50 border border-indigo-500/20 text-slate-200 hover:bg-slate-800/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default Pagination;
