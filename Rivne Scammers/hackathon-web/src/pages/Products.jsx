import React, { useEffect, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import RefreshButton from '../components/RefreshButton';
import Pagination from '../components/Pagination';
import { useProducts } from '../hooks/api/useProducts';
import { features } from '../config/features';
import { useLoading } from '../context/LoadingContext';
import { QUERY_KEYS } from '../constants';
import { formatCurrency } from '../utils/formatters';
import { openShopifyProduct } from '../utils/shopify';

const ITEMS_PER_PAGE = 15;

const Products = () => {
  const queryClient = useQueryClient();
  const { setIsGlobalLoading, setLoadingMessage } = useLoading();
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [stockFilter, setStockFilter] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const shouldUseBackendProducts = features.useBackendProducts;

  const {
    data: backendProducts,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useProducts({}, { enabled: shouldUseBackendProducts });

  useEffect(() => {
    if (!shouldUseBackendProducts) {
      setProducts([]);
      return;
    }
    if (backendProducts) {
      setProducts(backendProducts.products ?? []);
    }
  }, [backendProducts, shouldUseBackendProducts]);

  useEffect(() => {
    const busy = (isLoading || isFetching) && shouldUseBackendProducts;
    if (busy) {
      setLoadingMessage(isRefreshing ? 'Refreshing product catalog...' : 'Loading product catalog...');
    } else {
      setLoadingMessage('');
    }
    setIsGlobalLoading(busy);
  }, [isLoading, isFetching, isRefreshing, shouldUseBackendProducts, setIsGlobalLoading, setLoadingMessage]);

  useEffect(() => () => setIsGlobalLoading(false), [setIsGlobalLoading]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PRODUCTS] });
      await refetch();
    } catch (syncError) {
      // eslint-disable-next-line no-console
      console.error('Failed to sync products', syncError);
    } finally {
      setTimeout(() => {
        setIsRefreshing(false);
      }, 500);
    }
  };

  const filteredProducts = useMemo(() => {
    if (!products.length) return [];
    
    return products.filter((product) => {
      // Search filter
      const term = searchTerm.trim().toLowerCase();
      const matchesSearch = !term || 
        product.name?.toLowerCase().includes(term) || 
        product.sku?.toLowerCase().includes(term) || 
        product.category?.toLowerCase().includes(term);
      
      // Category filter
      const matchesCategory = categoryFilter === 'all' || 
        product.category?.toLowerCase() === categoryFilter.toLowerCase();
      
      // Stock filter
      let matchesStock = true;
      if (stockFilter === 'in-stock') {
        matchesStock = (product.stock || 0) > 0;
      } else if (stockFilter === 'low-stock') {
        matchesStock = (product.stock || 0) > 0 && (product.stock || 0) <= 10;
      } else if (stockFilter === 'out-of-stock') {
        matchesStock = (product.stock || 0) === 0;
      }
      
      return matchesSearch && matchesCategory && matchesStock;
    });
  }, [products, searchTerm, categoryFilter, stockFilter]);

  // Pagination logic
  const totalProducts = filteredProducts.length;
  const totalPages = Math.ceil(totalProducts / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, categoryFilter, stockFilter]);

  // Get unique categories for filter
  const categories = useMemo(() => {
    const uniqueCategories = [...new Set(products.map(p => p.category).filter(Boolean))];
    return uniqueCategories.sort();
  }, [products]);

  const errorMessage = isError
    ? error?.message || error?.response?.data?.detail || 'Failed to load products from the backend'
    : null;

  const canRefresh = shouldUseBackendProducts;

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">Products</h1>
          <p className="text-sm text-slate-400 mt-1">Manage your product catalog</p>
        </div>
        <RefreshButton
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing || isLoading}
          disabled={!canRefresh}
        />
      </div>

      {(isLoading || isFetching) && (
        <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 p-4 text-sm text-slate-300">
          Loading latest products...
        </div>
      )}

      {errorMessage && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
          {errorMessage}
        </div>
      )}

      {/* Filters and Search */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              type="search"
              placeholder="Search by product name, SKU, or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
            />
          </div>
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-4 py-2 rounded-xl bg-slate-800 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition cursor-pointer hover:border-indigo-500/40"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" className="bg-slate-800 text-slate-200">All Categories</option>
          {categories.map(category => (
            <option key={category} value={category} className="bg-slate-800 text-slate-200">
              {category}
            </option>
          ))}
        </select>

        <select
          value={stockFilter}
          onChange={(e) => setStockFilter(e.target.value)}
          className="px-4 py-2 rounded-xl bg-slate-800 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition cursor-pointer hover:border-indigo-500/40"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" className="bg-slate-800 text-slate-200">All Stock</option>
          <option value="in-stock" className="bg-slate-800 text-slate-200">In Stock</option>
          <option value="low-stock" className="bg-slate-800 text-slate-200">Low Stock (≤10)</option>
          <option value="out-of-stock" className="bg-slate-800 text-slate-200">Out of Stock</option>
        </select>
      </div>

      {/* Products Table */}
      <div className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-indigo-500/20">
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Product ID</th>
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Name</th>
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Category</th>
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Stock</th>
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Price</th>
                <th className="px-4 py-3 text-sm font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedProducts.map((product) => (
                <tr key={product.id ?? product.sku} className="border-b border-indigo-500/20">
                  <td className="px-4 py-3 font-mono text-indigo-300">{product.id || '—'}</td>
                  <td className="px-4 py-3 text-slate-200">{product.name}</td>
                  <td className="px-4 py-3 text-slate-400">{product.category}</td>
                  <td className="px-4 py-3 text-slate-200">{product.stock}</td>
                  <td className="px-4 py-3 font-medium text-slate-200">{formatCurrency(product.price)}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => openShopifyProduct(product)}
                      className="px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/50 transition-colors"
                      title={`Open product ${product.id} in Shopify`}
                    >
                      Open in Shopify
                    </button>
                  </td>
                </tr>
              ))}
              {!paginatedProducts.length && !isLoading && (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                    {searchTerm ? 'No products found matching your search.' : 'No products found. Trigger a sync to pull your Shopify catalog.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Bottom */}
      {!isLoading && totalProducts > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalProducts}
          startIndex={startIndex}
          endIndex={endIndex}
          onPageChange={setCurrentPage}
          itemName="products"
        />
      )}
    </div>
  );
};

export default Products;
