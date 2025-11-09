import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { AlertTriangle, Calendar, Package, TrendingUp, ExternalLink } from 'lucide-react';
import {
  useActionRecommendation,
  useGenerateRecommendations,
  useRecommendations,
} from '../hooks/api/useRecommendations';
import { useProducts } from '../hooks/api/useProducts';
import { useLoading } from '../context/LoadingContext';
import { STATUS_COLORS } from '../constants';
import { extractShopifyId, getProductAdminUrl, openShopifyProduct } from '../utils/shopify';
import RefreshButton from '../components/RefreshButton';

const iconByType = {
  urgent_restock: <AlertTriangle className="h-5 w-5" />,
  trending: <TrendingUp className="h-5 w-5" />,
  slow_mover: <Package className="h-5 w-5" />,
  seasonal: <Calendar className="h-5 w-5" />,
};

const getIcon = (type) => iconByType[type] ?? <Package className="h-5 w-5" />;

const MLSuggestions = () => {
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('pending');
  const [generationStatus, setGenerationStatus] = useState(null);
  const [statusPollingInterval, setStatusPollingInterval] = useState(null);
  const { setIsGlobalLoading, setLoadingMessage } = useLoading();

  const recommendationFilters = useMemo(
    () => ({
      priority: selectedPriority === 'all' ? undefined : selectedPriority,
      status: selectedStatus,
    }),
    [selectedPriority, selectedStatus]
  );

  const {
    data: recommendationsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useRecommendations(recommendationFilters);

  const { data: productsData } = useProducts({ limit: 250 }, { staleTime: 5 * 60 * 1000 });

  const generateMutation = useGenerateRecommendations();
  const actionMutation = useActionRecommendation();

  const isGenerating = generateMutation.status === 'pending' || generationStatus?.is_running;
  const isActing = actionMutation.status === 'pending';

  // Check generation status from API
  const checkStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/recommendations/status');
      if (!response.ok) return;
      const status = await response.json();
      setGenerationStatus(status);

      // If generation completed, stop polling and refresh recommendations
      if (!status.is_running && statusPollingInterval) {
        clearInterval(statusPollingInterval);
        setStatusPollingInterval(null);
        if (status.last_run) {
          await refetch();
        }
      }
    } catch (err) {
      console.error('Failed to fetch generation status:', err);
    }
  }, [statusPollingInterval, refetch]);

  useEffect(() => {
    const loading = (isLoading || isGenerating || isActing) && !isError;
    setIsGlobalLoading(loading);
    if (loading) {
      if (isGenerating) {
        setLoadingMessage('AI is analyzing your inventory, forecasting demand, and detecting trends...');
      } else {
        setLoadingMessage('Preparing AI-powered recommendations...');
      }
    } else {
      setLoadingMessage('');
    }
  }, [isLoading, isGenerating, isActing, isError, setIsGlobalLoading, setLoadingMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      setIsGlobalLoading(false);
      if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
      }
    };
  }, [setIsGlobalLoading, statusPollingInterval]);

  // Check status on mount
  useEffect(() => {
    checkStatus();
  }, []);

  const recommendations = useMemo(() => {
    if (!recommendationsData) return [];
    if (Array.isArray(recommendationsData)) {
      return recommendationsData;
    }
    if (Array.isArray(recommendationsData?.recommendations)) {
      return recommendationsData.recommendations;
    }
    return [];
  }, [recommendationsData]);

  const recommendationsErrorMessage = useMemo(() => {
    if (!isError) return '';
    if (error?.response?.data?.detail) return error.response.data.detail;
    if (error?.message) return error.message;
    return 'Unable to load recommendations.';
  }, [isError, error]);

  const handleGenerateRecommendations = async () => {
    try {
      await generateMutation.mutateAsync();

      // Start polling for status every 2 seconds
      const interval = setInterval(checkStatus, 2000);
      setStatusPollingInterval(interval);

      // Also do an immediate status check
      await checkStatus();
    } catch (err) {
      console.error('Failed to generate recommendations:', err);
      // errors handled via toast layer elsewhere
    }
  };

  const handleAction = async (recommendationId, action) => {
    try {
      await actionMutation.mutateAsync({
        recommendationId,
        actionData: { action },
      });
      await refetch();
    } catch (err) {
      console.error('Failed to update recommendation status:', err);
    }
  };

  const priorities = ['all', 'critical', 'high', 'medium', 'low'];
  const isPendingView = selectedStatus === 'pending';

  const toggleStatusView = () => {
    setSelectedStatus((prev) => (prev === 'pending' ? 'dismissed' : 'pending'));
  };

  const productsIndex = useMemo(() => {
    const bySku = new Map();
    const byGid = new Map();
    const byNumericId = new Map();
    const list = productsData?.products;
    if (!Array.isArray(list)) {
      return { bySku, byGid, byNumericId };
    }

    list.forEach((product) => {
      if (!product) return;
      const basePayload = {
        id: product.id ?? null,
        gid: product.gid ?? null,
        sku: product.sku ?? null,
        shopDomain: product.shopDomain ?? null,
        name: product.name ?? null,
        rawId: product.raw?.id ?? null,
      };

      if (basePayload.sku) {
        bySku.set(String(basePayload.sku).toLowerCase(), basePayload);
      }
      const normalizedNumericId = extractShopifyId(basePayload.gid ?? basePayload.id ?? basePayload.rawId);
      if (normalizedNumericId) {
        byNumericId.set(String(normalizedNumericId), basePayload);
      }
      if (basePayload.gid ?? basePayload.rawId) {
        const gidKey = String(basePayload.gid ?? basePayload.rawId);
        byGid.set(gidKey, basePayload);
      }

      const variantSources = [];
      if (Array.isArray(product.raw?.variants)) {
        variantSources.push(...product.raw.variants);
      } else if (Array.isArray(product.raw?.variants?.edges)) {
        variantSources.push(
          ...product.raw.variants.edges
            .map((edge) => edge?.node ?? edge)
            .filter(Boolean)
        );
      } else if (Array.isArray(product.raw?.variants?.nodes)) {
        variantSources.push(...product.raw.variants.nodes);
      }

      variantSources.forEach((variant) => {
        const variantSku = variant?.sku;
        if (!variantSku) return;
        bySku.set(String(variantSku).toLowerCase(), {
          ...basePayload,
          sku: variantSku,
        });
        const variantGid = variant?.id;
        if (variantGid) {
          byGid.set(String(variantGid), {
            ...basePayload,
            gid: variantGid,
          });
          const variantNumeric = extractShopifyId(variantGid);
          if (variantNumeric) {
            byNumericId.set(String(variantNumeric), {
              ...basePayload,
              id: variantNumeric,
              gid: variantGid,
            });
          }
        }
      });
    });

    return { bySku, byGid, byNumericId };
  }, [productsData]);

  const resolveProductPayload = useCallback(
    (rec) => {
      if (!rec) return null;
      const { bySku, byGid, byNumericId } = productsIndex;
      const skuCandidates = [rec.sku, rec.product_sku, rec.raw?.sku]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());
      for (const candidate of skuCandidates) {
        if (bySku.has(candidate)) {
          return bySku.get(candidate);
        }
      }

      const gidCandidates = [rec.product_gid, rec.raw?.product?.gid, rec.gid, rec.raw?.gid]
        .filter(Boolean)
        .map((value) => String(value));
      for (const candidate of gidCandidates) {
        if (byGid.has(candidate)) {
          return byGid.get(candidate);
        }
      }

      const idCandidates = [
        rec.product_id,
        rec.productId,
        rec.raw?.product_id,
        rec.raw?.productId,
        rec.raw?.product?.id,
        rec.raw?.id,
      ]
        .filter(Boolean)
        .map((value) => String(value));
      for (const candidate of idCandidates) {
        if (byNumericId.has(candidate)) {
          return byNumericId.get(candidate);
        }
      }

      return null;
    },
    [productsIndex]
  );

  const buildShopifyPayload = useCallback(
    (rec) => {
      if (!rec) {
        return null;
      }

      const matched = resolveProductPayload(rec);
      if (matched) {
        const numericId = extractShopifyId(matched.gid ?? matched.rawId ?? matched.id);
        return {
          id: numericId || undefined,
          gid: matched.gid ?? matched.rawId ?? matched.id ?? undefined,
          sku: matched.sku ?? rec.sku ?? undefined,
          shopDomain: matched.shopDomain ?? rec.shopDomain,
          name: matched.name ?? rec.product_name ?? rec.productName,
        };
      }

      const fallbackNumericId = extractShopifyId(
        rec.product_gid ??
        rec.product_id ??
        rec.productId ??
        rec.raw?.product?.gid ??
        rec.raw?.product?.id ??
        rec.raw?.product_id ??
        rec.raw?.productId ??
        rec.raw?.gid ??
        rec.raw?.id ??
        rec.shopify_product_id ??
        rec.shopifyProductId
      );
      const fallbackGid =
        rec.product_gid ??
        rec.raw?.product?.gid ??
        rec.raw?.gid ??
        rec.shopify_product_gid ??
        rec.shopifyProductGid ??
        undefined;

      if (!fallbackNumericId && !rec.sku) {
        return null;
      }

      return {
        id: fallbackNumericId || undefined,
        gid: fallbackGid || undefined,
        sku: rec.sku ?? rec.product_sku ?? undefined,
        shopDomain:
          rec.shopDomain ??
          rec.store_domain ??
          rec.storeDomain ??
          rec.shop?.storeDomain ??
          rec.shop?.myshopifyDomain ??
          rec.shop?.domain ??
          rec.raw?.shopDomain ??
          rec.raw?.storeDomain ??
          undefined,
        name: rec.product_name ?? rec.productName ?? null,
      };
    },
    [resolveProductPayload]
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">
            ML Suggestions
          </h1>
          <p className="text-sm text-slate-400 mt-1">AI-powered inventory recommendations</p>
          {generationStatus && generationStatus.last_run && (
            <p className="text-xs text-slate-500 mt-1">
              Last generated: {new Date(generationStatus.last_run * 1000).toLocaleString()}
              {' '}({generationStatus.last_run_count} recommendations in {generationStatus.last_run_duration?.toFixed(2)}s)
            </p>
          )}
        </div>
        <RefreshButton
          onRefresh={handleGenerateRecommendations}
          isRefreshing={isGenerating}
          label="Generate New"
          disabled={isGenerating}
        />
      </div>

       <div className="flex flex-col gap-3">
         <div className="flex flex-col gap-2">
           <div className="flex flex-col leading-tight">
             <span className="text-xs uppercase tracking-wide text-slate-400">Status</span>
             <span className="text-sm font-semibold text-slate-200">
               {isPendingView ? 'Active' : 'Dismissed'}
             </span>
           </div>
           <button
             type="button"
             role="switch"
             aria-checked={isPendingView}
             aria-label="Toggle between Active and Dismissed recommendations"
             onClick={toggleStatusView}
             className={`relative inline-flex h-8 w-24 items-center rounded-full transition ${
               isPendingView ? 'bg-indigo-500/30' : 'bg-rose-500/30'
             }`}
           >
             <span className="sr-only">Toggle suggestion status view</span>
             <span
               className={`pointer-events-none absolute top-0.5 h-7 w-7 rounded-full bg-white shadow transition-all ${
                 isPendingView ? 'left-1' : 'right-1'
               }`}
             />
           </button>
         </div>
         <div className="flex flex-wrap gap-2">
           {priorities.map((priority) => (
             <button
               key={priority}
               type="button"
               onClick={() => setSelectedPriority(priority)}
               className={`px-4 py-2 rounded-xl font-medium transition ${
                 selectedPriority === priority
                   ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white'
                   : 'bg-white/5 border border-indigo-500/20 text-slate-300 hover:bg-white/10'
               }`}
             >
               {priority.charAt(0).toUpperCase() + priority.slice(1)}
             </button>
           ))}
         </div>
       </div>

       <div className="grid gap-4">
         {isError ? (
           <div className="text-center py-12 space-y-4 text-rose-300">
             <div>{recommendationsErrorMessage}</div>
             <button
               type="button"
               onClick={() => refetch()}
               className="text-indigo-300 hover:text-indigo-200 underline"
             >
               Try again
             </button>
           </div>
         ) : isLoading ? (
           <div className="text-center py-12 text-slate-400">Loading recommendations...</div>
         ) : recommendations.length > 0 ? (
           recommendations.map((rec) => {
             const priorityKey = rec.priority ? rec.priority.toUpperCase() : 'MEDIUM';
             const priorityBubbleColor =
               rec.priority === 'critical'
                 ? 'bg-rose-500/20'
                 : rec.priority === 'high'
                 ? 'bg-amber-500/20'
                 : rec.priority === 'medium'
                 ? 'bg-indigo-500/20'
                 : 'bg-slate-500/20';
             const shopifyPayload = buildShopifyPayload(rec);
             const productAdminUrl = shopifyPayload ? getProductAdminUrl(shopifyPayload) : null;

            return (
              <div
                key={rec.id}
                className={`border rounded-xl p-6 backdrop-blur-xl ${STATUS_COLORS[priorityKey] || STATUS_COLORS.MEDIUM}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-4">
                    <div className="flex items-center gap-3">
                      {getIcon(rec.type)}
                      <h3 className="text-lg font-semibold">{rec.product_name ?? rec.productName ?? 'Product'}</h3>
                      <span className={`px-2 py-1 rounded-lg text-xs font-medium ${priorityBubbleColor}`}>
                        {(rec.priority || 'medium').toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm">{rec.message || rec.summary || 'No message provided.'}</p>
                    {productAdminUrl && (
                      <div className="text-xs text-indigo-200">
                        <a
                          href={productAdminUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline decoration-indigo-400 hover:text-indigo-100"
                        >
                          View related Shopify product
                        </a>
                      </div>
                    )}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-xs text-slate-400">Current Stock</div>
                        <div className="font-semibold">{rec.current_stock ?? rec.currentStock ?? 0} units</div>
                      </div>
                      {rec.suggested_quantity ?? rec.suggestedQuantity ? (
                        <div>
                          <div className="text-xs text-slate-400">Suggested Order</div>
                          <div className="font-semibold">{rec.suggested_quantity ?? rec.suggestedQuantity} units</div>
                        </div>
                      ) : null}
                      {rec.days_until_stockout ?? rec.daysUntilStockout ? (
                        <div>
                          <div className="text-xs text-slate-400">Days Until Stockout</div>
                          <div className="font-semibold">{Math.round(rec.days_until_stockout ?? rec.daysUntilStockout)}</div>
                        </div>
                      ) : null}
                      <div>
                        <div className="text-xs text-slate-400">Confidence</div>
                        <div className="font-semibold">{Math.round((rec.confidence ?? 0) * 100)}%</div>
                      </div>
                    </div>
                    {rec.reasoning && (
                      <details className="text-sm">
                        <summary className="text-xs text-slate-400 cursor-pointer hover:text-slate-300">
                          View Analysis Details
                        </summary>
                        <p className="mt-2 text-xs text-slate-300 bg-black/20 p-2 rounded">{rec.reasoning}</p>
                      </details>
                    )}
                  </div>
                  <div className="flex flex-wrap sm:flex-row gap-2">
                    <button
                      type="button"
                      onClick={() => shopifyPayload && openShopifyProduct(shopifyPayload)}
                      disabled={!shopifyPayload}
                      className="px-3 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 text-sm font-medium transition flex items-center gap-1.5 justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                      title="View product in Shopify admin"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      <span>View in Shopify</span>
                    </button>
                    {isPendingView ? (
                      <button
                        type="button"
                        onClick={() => handleAction(rec.id, 'dismissed')}
                        disabled={isActing}
                        className="px-3 py-1.5 rounded-lg bg-slate-500/20 text-slate-200 hover:bg-slate-500/30 text-sm font-medium transition disabled:opacity-50"
                      >
                        Dismiss
                      </button>
                    ) : null}
                    <div className="px-3 py-1.5 rounded-lg bg-white/5 border border-indigo-500/20 text-xs text-slate-300">
                      Status: {rec.status?.toUpperCase() ?? selectedStatus.toUpperCase()}
                    </div>
                  </div>
                </div>
              </div>
            );
           })
         ) : (
           <div className="text-center py-12 space-y-4">
             <div className="text-slate-400">No recommendations available</div>
             <div className="text-sm text-slate-500">Click the "Generate New" button above to create AI-powered recommendations</div>
           </div>
         )}
       </div>
     </div>
   );
 };

 export default MLSuggestions;
