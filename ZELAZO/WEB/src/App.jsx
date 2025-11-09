// Marketplace Listings Dashboard — single-file React app
// ------------------------------------------------------------
// Features:
// - Clean dashboard for managing product listings across marketplaces
// - Header with marketplace switcher (Amazon, Allegro, Temu)
// - Create new listings with product ID, marketplace, amount, and listing date
// - Listings table with search by product/listing ID & refresh
// - Liquid‑glass UI (blur, translucency, soft gradients)
// - Adaptive layout: table on desktop, cards on mobile
// - Network layer with ENV-driven baseURL, central endpoints map
//
// API Backend:
//   - GET  /api/listed-products/v1/listings - Get all product listings
//   - POST /api/listed-products/v1/listings - Create new listing
//
// ENV configuration:
//   Set VITE_API_BASE_URL in .env file (e.g., https://susceptible-liv-issuably.ngrok-free.dev)
// ------------------------------------------------------------

import React, { useEffect, useMemo, useState } from "react";

// ===== ENV =====
const ENV = {
  API_BASE_URL: "", // Empty - requests go through Vite proxy configured in vite.config.js
};

// ===== Endpoints registry (single source of truth) =====
const ENDPOINTS = {
  listings: {
    list: "/api/listed-products/v1/listings", // GET /api/listed-products/v1/listings
    create: "/api/listed-products/v1/listings", // POST /api/listed-products/v1/listings
    bulkImport: "/api/listed-products/v1/import-bulk", // POST bulk import with auto-matching
  },
  products: {
    list: "/api/products/v1/products", // GET /api/products/v1/products
  },
};

// ===== DTOs =====
/** @typedef {Object} ListedProduct
 * @property {string} id // UUID
 * @property {string} product_id // UUID
 * @property {"amazon"|"allegro"|"temu"|string} marketplace
 * @property {number} amount
 * @property {string} date_of_listing // ISO string
 * @property {string} created_at // ISO string
 * @property {string} updated_at // ISO string
 */

// ===== Network Manager =====
class NetworkError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "NetworkError";
    this.status = status;
    this.payload = payload;
  }
}

class NetworkManager {
  /** @param {string} baseURL */
  constructor(baseURL) {
    this.baseURL = baseURL?.replace(/\/$/, "") || "";
  }
  url(path) { return `${this.baseURL}${path}`; }
  /** @param {Record<string, any>=} query */
  toQuery(query) {
    if (!query || Object.keys(query).length === 0) return "";
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null || v === "") continue;
      q.append(k, String(v));
    }
    const s = q.toString();
    return s ? `?${s}` : "";
  }
  async get(path, { query } = {}) {
    const res = await fetch(this.url(path) + this.toQuery(query), {
      method: "GET",
      headers: {
        "ngrok-skip-browser-warning": "true",
      },
    });
    if (!res.ok) throw new NetworkError(`GET ${path} failed`, res.status, await safeJson(res));
    return safeJson(res);
  }
  async post(path, body) {
    const res = await fetch(this.url(path), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new NetworkError(`POST ${path} failed`, res.status, await safeJson(res));
    return safeJson(res);
  }
}

async function safeJson(res) { try { return await res.json(); } catch { return null; } }

const api = new NetworkManager(ENV.API_BASE_URL || "");

// ===== Helpers =====
const PLATFORMS = [
  { value: "amazon", label: "Amazon" },
  { value: "allegro", label: "Allegro" },
  { value: "temu", label: "Temu" }
];
function formatDate(iso){ return new Date(iso).toLocaleString(); }

// ================= UI =================
export default function App(){
  const [marketplace,setMarketplace]=useState(PLATFORMS[0].value);
  const [listings,setListings]=useState(/** @type {ListedProduct[]} */([]));
  const [loading,setLoading]=useState(false);
  const [generating,setGenerating]=useState(false);
  const [q,setQ]=useState("");
  const [showForm,setShowForm]=useState(false);
  const [toast,setToast]=useState(null);

  const filtered=useMemo(()=>{
    let list=listings.filter(l=>l.marketplace===marketplace);
    if (!q) return list;
    const needle=q.toLowerCase();
    return list.filter(l=>l.product_id.toLowerCase().includes(needle)||l.id.toLowerCase().includes(needle));
  },[listings,q,marketplace]);

  async function load(){
    setLoading(true);
    try{
      const data=await api.get(ENDPOINTS.listings.list);
      setListings(data?.listed_products || []);
    }
    catch(e){ console.error(e); showToast(`Failed to load (${e.status||"net"})`); }
    finally{ setLoading(false); }
  }
  useEffect(()=>{ load(); /* eslint-disable-next-line */ },[]);

  function showToast(text){ setToast(text); setTimeout(()=>setToast(null),2200); }

  function onAddListing(){
    setShowForm(true);
  }

  // Generate random date with weighted distribution
  // isEarlyWeighted: true = more dates early in period, false = more dates late in period
  function randomDateWeighted(start, end, isEarlyWeighted) {
    const totalMs = end.getTime() - start.getTime();
    const midPoint = start.getTime() + totalMs / 2;

    // 60% in preferred period, 40% in other period
    const preferEarly = Math.random() < 0.6 === isEarlyWeighted;

    let timestamp;
    if (preferEarly) {
      // Generate date in first half
      timestamp = start.getTime() + Math.random() * (midPoint - start.getTime());
    } else {
      // Generate date in second half
      timestamp = midPoint + Math.random() * (end.getTime() - midPoint);
    }

    return new Date(timestamp);
  }

  async function generateBigData(){
    setGenerating(true);
    try{
      // Get all products
      const data = await api.get(ENDPOINTS.products.list);
      const products = data?.products || [];

      if (products.length === 0) {
        showToast("No products found to generate listings");
        return;
      }

      // Calculate date range: start of last month to today
      const today = new Date();
      const startOfLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);

      // Build array of all listings to import
      const allListings = [];

      // For each product, create 1-2 listings per marketplace (20 products × ~1.5 × 3 platforms = ~90 listings)
      products.forEach((product, productIndex) => {
        // Alternate pattern: even index = declining trend (early weighted), odd = growing trend (late weighted)
        const isEarlyWeighted = productIndex % 2 === 0;

        PLATFORMS.forEach((platform) => {
          // Randomly create 1 or 2 listings per product per platform (avg 1.5)
          const listingsCount = Math.random() < 0.5 ? 1 : 2;
          for (let i = 0; i < listingsCount; i++) {
            const randomAmount = Math.floor(Math.random() * 100) + 1; // Random amount 1-100
            const randomListingDate = randomDateWeighted(startOfLastMonth, today, isEarlyWeighted);

            // SKU distribution: 50% correct, 40% missing, 10% incorrect
            const skuRandom = Math.random();
            let skuType;
            if (skuRandom < 0.5) {
              skuType = 'correct'; // 50% - correct product ID
            } else if (skuRandom < 0.9) {
              skuType = 'missing'; // 40% - no SKU (test AI fuzzy matching)
            } else {
              skuType = 'incorrect'; // 10% - wrong SKU (test mismatch handling)
            }

            // Add 2-15% markup to the base product price
            const markupPercent = 2 + Math.random() * 13; // Random between 2% and 15%
            const markedUpPrice = product.price * (1 + markupPercent / 100);
            const listingPrice = Math.round(markedUpPrice * 100) / 100; // Round to 2 decimal places

            const listing = {
              name: product.name,
              price: listingPrice,
              marketplace: platform.value,
              amount: randomAmount,
              date_of_listing: randomListingDate.toISOString()
            };

            // Apply SKU based on type
            if (skuType === 'correct') {
              listing.sku = product.id;
            } else if (skuType === 'incorrect') {
              // Generate a fake SKU that won't match any product
              listing.sku = `FAKE-SKU-${Math.random().toString(36).substring(2, 15)}`;
            }
            // If skuType === 'missing', don't add SKU field at all

            allListings.push(listing);
          }
        });
      });

      // Send all listings in one bulk request
      const response = await api.post(ENDPOINTS.listings.bulkImport, {
        listings: allListings
      });

      const totalCreated = allListings.length;
      showToast(`Generated ${totalCreated} listings for ${products.length} products`);
      load(); // Reload listings
    }
    catch(e){
      console.error(e);
      showToast(`Failed to generate data: ${e.message || e.status || "network error"}`);
    }
    finally{
      setGenerating(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-slate-100">
      {/* Decorative gradient blur blobs */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl"></div>
        <div className="absolute top-1/3 -right-24 h-80 w-80 rounded-full bg-indigo-400/20 blur-3xl"></div>
        <div className="absolute bottom-0 left-1/4 h-60 w-60 rounded-full bg-emerald-400/10 blur-3xl"></div>
      </div>

      <Header
        marketplace={marketplace}
        setMarketplace={setMarketplace}
        apiBase={ENV.API_BASE_URL}
      />

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl px-2 py-2 shadow-2xl">
          {/* Action bar */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between px-4 py-4">
            <div className="flex gap-2 flex-wrap">
              <Primary onClick={onAddListing}>Add listing</Primary>
              <button
                onClick={generateBigData}
                disabled={generating}
                className="px-4 py-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium shadow hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? "Generating..." : "Generate data"}
              </button>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden sm:block text-xs text-slate-400">
                API: <span className="font-medium text-emerald-400">Vite Proxy → ngrok</span>
              </div>
              <div className="flex items-center gap-2 rounded-2xl bg-white/5 border border-white/10 px-3 py-2">
                <svg width="16" height="16" viewBox="0 0 24 24" className="opacity-70"><path d="M11 4a7 7 0 0 1 4.95 11.95l4.4 4.4-1.4 1.4-4.4-4.4A7 7 0 1 1 11 4Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z" fill="currentColor"/></svg>
                <input
                  value={q}
                  onChange={(e)=>setQ(e.target.value)}
                  placeholder="Search product/listing ID"
                  className="bg-transparent outline-none text-sm placeholder-slate-400"
                />
                <button onClick={load} className="text-xs px-3 py-1 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10">Refresh</button>
              </div>
            </div>
          </div>

          {/* Content panel */}
          <div className="p-2 sm:p-3">
            <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl">
              <TableOrCards loading={loading} listings={filtered} />
            </div>
          </div>
        </div>
      </main>

      {showForm && (
        <ListingForm
          marketplace={marketplace}
          onClose={()=>setShowForm(false)}
          onSubmit={async (payload)=>{
            try{
              await api.post(ENDPOINTS.listings.create,payload);
              showToast("Listing added");
              setShowForm(false);
              load();
            }
            catch(e){ console.error(e); showToast(`Error (${e.status||"net"})`); }
          }}
        />
      )}

      {toast && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 text-white px-4 py-2 shadow-xl">
          {toast}
        </div>
      )}
    </div>
  );
}

function Header({ marketplace, setMarketplace, apiBase }){
  return (
    <header className="sticky top-0 z-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-4">
        <div className="relative overflow-hidden rounded-3xl border border-white/15 bg-white/10 backdrop-blur-xl shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-white/30 via-white/0 to-white/10" />
          <div className="relative px-4 py-4 sm:px-6 sm:py-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="text-lg sm:text-xl font-semibold tracking-tight">Marketplace Listings Dashboard</div>
              <span className="hidden sm:inline text-slate-300">•</span>
              <span className="text-xs rounded-xl px-2 py-1 bg-white/10 border border-white/15">REST API</span>
            </div>
            <MarketplaceSegment value={marketplace} onChange={setMarketplace} />
          </div>
        </div>
      </div>
    </header>
  );
}

function MarketplaceSegment({ value, onChange }){
  return (
    <div className="inline-flex rounded-2xl bg-white/10 border border-white/15 p-1 backdrop-blur-xl">
      {PLATFORMS.map((p)=>{
        const active = p.value===value;
        return (
          <button
            key={p.value}
            onClick={()=>onChange(p.value)}
            className={`px-3 sm:px-4 py-1.5 rounded-xl text-sm transition ${active ? "bg-white/30 shadow-inner text-slate-900" : "text-slate-200 hover:bg-white/15"}`}
          >
            {marketplaceIcon(p.value)} <span className="ml-1 hidden sm:inline">{p.label}</span>
          </button>
        );
      })}
    </div>
  );
}

function marketplaceIcon(m){
  const common = "inline-block align-[-2px]";
  if (m==="amazon") return <span className={common}>🅰️</span>;
  if (m==="allegro") return <span className={common}>🅰︎</span>;
  if (m==="temu") return <span className={common}>🛍️</span>;
  return <span className={common}>🛒</span>;
}


function Primary({ children, onClick }){
  return (
    <button onClick={onClick} className="px-4 py-2 rounded-2xl bg-white text-slate-900 font-medium shadow hover:opacity-90 transition">
      {children}
    </button>
  );
}

function TableOrCards({ listings, loading }){
  return (
    <div className="p-3">
      {/* Desktop table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full">
          <thead className="text-left text-slate-300 text-sm">
            <tr>
              {['Listing ID','Product ID','Marketplace','Amount','Listing Date','Created At'].map((h)=>(
                <th key={h} className="px-4 py-3 border-b border-white/10">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">Loading…</td></tr>
            ) : listings.length===0 ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">No listings</td></tr>
            ) : (
              listings.map((l)=> (
                <tr key={l.id} className="hover:bg-white/5">
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{l.id}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-300">{l.product_id}</td>
                  <td className="px-4 py-3"><span className="text-xs px-2 py-1 rounded-lg bg-white/10 border border-white/10">{l.marketplace}</span></td>
                  <td className="px-4 py-3 font-semibold">{l.amount}</td>
                  <td className="px-4 py-3 text-slate-300">{formatDate(l.date_of_listing)}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{formatDate(l.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden grid grid-cols-1 gap-3">
        {loading ? (
          <div className="text-center text-slate-400 py-10">Loading…</div>
        ) : listings.length===0 ? (
          <div className="text-center text-slate-400 py-10">No listings</div>
        ) : (
          listings.map((l)=> (
            <div key={l.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <div className="font-medium text-sm">Listing</div>
                <span className="text-xs px-2 py-1 rounded-lg bg-white/10 border border-white/10">{l.marketplace}</span>
              </div>
              <div className="mt-2 text-xs font-mono text-slate-400">ID: {l.id}</div>
              <div className="mt-3 grid grid-cols-1 gap-2 text-sm">
                <div className="opacity-80">Product ID: <span className="text-white font-mono text-xs">{l.product_id}</span></div>
                <div className="opacity-80">Amount: <span className="text-white font-semibold">{l.amount}</span></div>
                <div className="opacity-80">Listed: <span className="text-white">{formatDate(l.date_of_listing)}</span></div>
                <div className="opacity-80 text-xs">Created: <span className="text-slate-300">{formatDate(l.created_at)}</span></div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function ListingForm({ marketplace, onClose, onSubmit }){
  const [productId,setProductId]=useState("");
  const [amount,setAmount]=useState(1);
  const [date,setDate]=useState(new Date().toISOString().slice(0,16));
  const [selectedMarketplace,setSelectedMarketplace]=useState(marketplace);
  const [busy,setBusy]=useState(false);

  return (
    <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-4 z-30">
      <div className="w-full max-w-lg rounded-3xl border border-white/15 bg-white/10 backdrop-blur-xl shadow-2xl">
        <div className="px-5 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="font-semibold">Create new listing</div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-white/10" aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
          </button>
        </div>
        <div className="px-5 py-4 grid grid-cols-1 gap-4">
          <label className="grid gap-1">
            <span className="text-sm text-slate-300">Product ID (UUID) *</span>
            <input value={productId} onChange={(e)=>setProductId(e.target.value)} className="px-3 py-2 rounded-xl bg-white/10 border border-white/15 outline-none focus:ring w-full font-mono text-sm" placeholder="550e8400-e29b-41d4-a716-446655440000" />
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-slate-300">Marketplace *</span>
            <select value={selectedMarketplace} onChange={(e)=>setSelectedMarketplace(e.target.value)} className="px-3 py-2 rounded-xl bg-white/10 border border-white/15 outline-none focus:ring w-full">
              {PLATFORMS.map((p)=><option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-slate-300">Amount *</span>
            <input type="number" min={1} value={amount} onChange={(e)=>setAmount(Number(e.target.value))} className="px-3 py-2 rounded-xl bg-white/10 border border-white/15 outline-none focus:ring w-full" />
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-slate-300">Listing Date *</span>
            <input type="datetime-local" value={date} onChange={(e)=>setDate(e.target.value)} className="px-3 py-2 rounded-xl bg-white/10 border border-white/15 outline-none focus:ring w-full" />
          </label>
          <p className="text-xs text-slate-400">The listing will be created on the selected marketplace with the specified product ID and amount.</p>
        </div>
        <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15">Cancel</button>
          <button disabled={busy||!productId||amount<1}
            onClick={async()=>{
              setBusy(true);
              await onSubmit({
                product_id: productId,
                marketplace: selectedMarketplace,
                amount: Number(amount),
                date_of_listing: new Date(date).toISOString()
              });
              setBusy(false);
            }}
            className="px-4 py-2 rounded-xl bg-white text-slate-900 disabled:opacity-50">Create Listing</button>
        </div>
      </div>
    </div>
  );
}


// -------------------------
// REST API Contract:
//   GET  /api/listed-products/v1/listings → { listed_products: ListedProduct[], total: number }
//   POST /api/listed-products/v1/listings → ListedProduct
//        Body: { product_id: string (UUID), marketplace: "amazon"|"allegro"|"temu", amount: number, date_of_listing: string (ISO) }
//
// ListedProduct:
//   {
//     id: string (UUID),
//     product_id: string (UUID),
//     marketplace: "amazon"|"allegro"|"temu",
//     amount: number,
//     date_of_listing: string (ISO),
//     created_at: string (ISO),
//     updated_at: string (ISO)
//   }
// -------------------------
