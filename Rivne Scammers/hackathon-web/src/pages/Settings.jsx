import React, { useEffect, useState } from 'react';
import { Eye, EyeOff, Save, TestTube } from 'lucide-react';
import shopifySettingsService from '../api/services/shopifySettingsService';

const Settings = () => {
  const [shopifySettings, setShopifySettings] = useState({
    shopUrl: '',
    accessToken: '',
    apiVersion: '2025-01',
    webhooksEnabled: false,
  });
  const [hasStoredToken, setHasStoredToken] = useState(false);
  const [showToken, setShowToken] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [saveStatus, setSaveStatus] = useState('');
  const [saveError, setSaveError] = useState('');
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadConfig = async () => {
      setLoadingConfig(true);
      setLoadError('');
      try {
        const data = await shopifySettingsService.getConfig();
        if (!isMounted) return;
        if (data?.configured) {
          setShopifySettings((prev) => ({
            ...prev,
            shopUrl: data.shop_url ?? '',
            apiVersion: data.api_version ?? '2025-01',
            accessToken: data.access_token ?? '',
            accessTokenMasked: data.access_token_masked ?? '',
          }));
          setHasStoredToken(Boolean(data.has_access_token));
        } else {
          setHasStoredToken(false);
        }
      } catch (error) {
        if (isMounted) {
          const message = error?.response?.data?.detail || error?.message || 'Failed to load Shopify settings';
          setLoadError(message);
        }
      } finally {
        if (isMounted) {
          setLoadingConfig(false);
        }
      }
    };

    loadConfig();

    return () => {
      isMounted = false;
    };
  }, []);

  const updateField = (field, value) => {
    setShopifySettings((prev) => ({ ...prev, [field]: value }));
    setSaveError('');
    setSaveStatus('');
    if (field === 'accessToken' || field === 'shopUrl' || field === 'apiVersion') {
      setTestResult(null);
    }
  };

  const handleSave = async () => {
    setSaveStatus('');
    setSaveError('');

    if (!shopifySettings.shopUrl.trim()) {
      setSaveError('Please enter a valid shop domain.');
      return;
    }

    const payload = {
      shop_url: shopifySettings.shopUrl.trim(),
      api_version: shopifySettings.apiVersion,
      access_token: shopifySettings.accessToken.trim() || undefined,
    };

    const trimmedToken = shopifySettings.accessToken.trim();
    if (trimmedToken) {
      payload.access_token = trimmedToken;
    }

    if (!trimmedToken && !hasStoredToken) {
      setSaveError('Access token is required.');
      return;
    }

    try {
      setSaving(true);
      const response = await shopifySettingsService.saveConfig(payload);
      setSaveStatus(response?.message || 'Settings saved successfully!');
      setHasStoredToken(Boolean(response?.has_access_token));
      setShopifySettings((prev) => ({ ...prev, accessToken: '' }));
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      const message = error?.response?.data?.detail || error?.message || 'Failed to save Shopify settings';
      setSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async () => {
    setTestingConnection(true);
    setTestResult(null);

    if (!shopifySettings.shopUrl.trim()) {
      setTestResult({ success: false, message: 'Enter your shop domain before testing.' });
      setTestingConnection(false);
      return;
    }

    const payload = {
      shop_url: shopifySettings.shopUrl.trim(),
      api_version: shopifySettings.apiVersion,
    };

    const trimmedToken = shopifySettings.accessToken.trim();
    if (trimmedToken) {
      payload.access_token = trimmedToken;
    } else if (!hasStoredToken) {
      setTestResult({ success: false, message: 'Enter an access token to test the connection.' });
      setTestingConnection(false);
      return;
    }

    try {
      const data = await shopifySettingsService.testCredentials(payload);
      const shopName = data?.shop_name || 'Shopify shop';
      setTestResult({ success: true, message: `Connected successfully to ${shopName}.` });
    } catch (error) {
      const message = error?.response?.data?.detail || error?.message || 'Connection failed. Check credentials.';
      setTestResult({ success: false, message });
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">
          Shopify API Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">Configure your Shopify store connection</p>
      </div>

      <section className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">API Configuration</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Shop URL</label>
            <input
              type="text"
              value={shopifySettings.shopUrl}
              onChange={(event) => updateField('shopUrl', event.target.value)}
              disabled={loadingConfig || saving}
              placeholder="your-store.myshopify.com"
              className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
            />
            <p className="mt-1 text-xs text-slate-400">Your Shopify store domain</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Access Token</label>
            <div className="relative">
              <input
                type={showToken ? 'text' : 'password'}
                value={shopifySettings.accessToken}
                onChange={(event) => updateField('accessToken', event.target.value)}
                disabled={loadingConfig || saving}
                placeholder="shpat_xxxxx"
                className="w-full px-4 py-2 pr-12 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
              />
              <button
                type="button"
                onClick={() => setShowToken((value) => !value)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition"
                aria-label={showToken ? 'Hide access token' : 'Show access token'}
              >
                {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Your private Shopify Admin API access token
              {hasStoredToken ? ' (leave blank to keep the stored token)' : ''}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">API Version</label>
            <select
              value={shopifySettings.apiVersion}
              onChange={(event) => updateField('apiVersion', event.target.value)}
              disabled={loadingConfig || saving}
              className="w-full px-4 py-2 rounded-xl bg-white/5 border border-indigo-500/20 text-slate-200 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/10 transition"
            >
              <option value="2025-01">2025-01 (Latest)</option>
              <option value="2024-10">2024-10</option>
              <option value="2024-07">2024-07</option>
              <option value="2024-04">2024-04</option>
            </select>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <div className="text-sm font-medium text-slate-300">Enable Webhooks</div>
              <div className="text-xs text-slate-400 mt-1">Receive real-time updates (Coming Soon)</div>
            </div>
            <label className="relative inline-flex items-center cursor-not-allowed opacity-50">
              <input
                type="checkbox"
                checked={shopifySettings.webhooksEnabled}
                onChange={(event) => updateField('webhooksEnabled', event.target.checked)}
                className="sr-only peer"
                disabled
              />
              <div className="w-11 h-6 bg-white/10 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-indigo-500 peer-checked:to-purple-500" />
            </label>
          </div>
        </div>

        {loadingConfig && (
          <div className="mt-4 p-3 rounded-xl text-sm bg-slate-500/10 border border-slate-500/30 text-slate-300">
            Loading existing settings...
          </div>
        )}

        {loadError && (
          <div className="mt-4 p-3 rounded-xl text-sm bg-rose-500/10 border border-rose-500/30 text-rose-300">
            {loadError}
          </div>
        )}

        {testResult && (
          <div
            className={`mt-4 p-3 rounded-xl text-sm ${
              testResult.success
                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
            }`}
          >
            {testResult.message}
          </div>
        )}

        {saveError && (
          <div className="mt-4 p-3 rounded-xl text-sm bg-rose-500/10 border border-rose-500/30 text-rose-300">
            {saveError}
          </div>
        )}

        {saveStatus && (
          <div className="mt-4 p-3 rounded-xl text-sm bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
            {saveStatus}
          </div>
        )}

        <div className="flex gap-3 mt-6">
          <button
            type="button"
            onClick={testConnection}
            disabled={testingConnection || loadingConfig}
            className="px-5 py-2.5 rounded-xl border border-indigo-500/30 bg-white/5 text-indigo-200 hover:text-white hover:border-indigo-400 backdrop-blur-xl transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <TestTube className={`h-4 w-4 ${testingConnection ? 'animate-pulse' : ''}`} />
            {testingConnection ? 'Testing...' : 'Test Connection'}
          </button>

          <button
            type="button"
            onClick={handleSave}
            disabled={loadingConfig || saving}
            className="group relative overflow-hidden px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold shadow-lg shadow-indigo-900/40 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4" />
            Save Settings
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
          </button>
        </div>
      </section>

      <section className="border border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl p-6 rounded-xl shadow-lg shadow-indigo-900/10">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Quick Setup Guide</h2>
        <ol className="space-y-3 text-sm text-slate-300">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center text-xs font-semibold">1</span>
            <div>
              <div className="font-medium">Create a Private App in Shopify</div>
              <div className="text-xs text-slate-400 mt-1">Go to Settings → Apps → Develop apps → Create an app</div>
            </div>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center text-xs font-semibold">2</span>
            <div>
              <div className="font-medium">Configure API Scopes</div>
              <div className="text-xs text-slate-400 mt-1">Enable read_products, read_orders, read_inventory permissions</div>
            </div>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center text-xs font-semibold">3</span>
            <div>
              <div className="font-medium">Install the App</div>
              <div className="text-xs text-slate-400 mt-1">Install the app and copy the Admin API access token</div>
            </div>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center text-xs font-semibold">4</span>
            <div>
              <div className="font-medium">Enter Credentials Here</div>
              <div className="text-xs text-slate-400 mt-1">Paste your shop URL and access token above</div>
            </div>
          </li>
        </ol>
      </section>
    </div>
  );
};

export default Settings;
