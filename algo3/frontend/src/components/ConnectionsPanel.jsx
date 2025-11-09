import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTranslation } from '../i18n/LanguageContext';

export default function ConnectionsPanel({ onConnectionChange }) {
  const { t } = useTranslation();
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    platform: 'woocommerce',
    store_url: '',
    api_key: '',
    api_secret: ''
  });
  const [formError, setFormError] = useState(null);
  const [syncing, setSyncing] = useState(null);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    setLoading(true);
    try {
      const data = await api.getConnections();
      setConnections(data);
    } catch (err) {
      console.error('Failed to load connections:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);

    try {
      await api.createConnection(formData);
      setShowForm(false);
      setFormData({
        name: '',
        platform: 'woocommerce',
        store_url: '',
        api_key: '',
        api_secret: ''
      });
      await loadConnections();
      if (onConnectionChange) onConnectionChange();
    } catch (err) {
      setFormError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm(t('connectionDeleteConfirm'))) return;

    try {
      await api.deleteConnection(id);
      await loadConnections();
      if (onConnectionChange) onConnectionChange();
    } catch (err) {
      alert(t('connectionDeleteError') + ': ' + err.message);
    }
  };

  const handleSync = async (id) => {
    setSyncing(id);
    try {
      const result = await api.syncConnection(id);
      alert(result.message);
      await loadConnections();
      if (onConnectionChange) onConnectionChange();
    } catch (err) {
      alert(t('connectionSyncError') + ': ' + err.message);
    } finally {
      setSyncing(null);
    }
  };


  return (
    <div className="connections-panel">
      <div className="panel-header">
        <h2>{t('connectionsTitle')}</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? t('btnCancel') : t('btnAddConnection')}
        </button>
      </div>

      {showForm && (
        <form className="connection-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{t('connectionName')}</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="e.g., My WooCommerce Store"
              required
            />
          </div>

          <div className="form-group">
            <label>{t('connectionPlatform')}</label>
            <select
              value={formData.platform}
              onChange={(e) => setFormData({...formData, platform: e.target.value})}
            >
              <option value="woocommerce">{t('connectionPlatformWoo')}</option>
              <option value="shopify">{t('connectionPlatformShopify')}</option>
            </select>
          </div>

          <div className="form-group">
            <label>{t('connectionUrl')}</label>
            <input
              type={formData.platform === 'shopify' ? 'text' : 'url'}
              value={formData.store_url}
              onChange={(e) => setFormData({...formData, store_url: e.target.value})}
              placeholder={formData.platform === 'shopify' ? 'myshop.myshopify.com' : 'https://myshop.com'}
              required
            />
            <small>
              {formData.platform === 'shopify'
                ? t('connectionUrlHintShopify')
                : t('connectionUrlHintWoo')
              }
            </small>
          </div>

          <div className="form-group">
            <label>
              {formData.platform === 'shopify' ? t('connectionApiKey') : t('connectionConsumerKey')}
            </label>
            <input
              type="text"
              value={formData.api_key}
              onChange={(e) => setFormData({...formData, api_key: e.target.value})}
              placeholder="API Key"
              required
            />
          </div>

          {formData.platform === 'woocommerce' && (
            <div className="form-group">
              <label>{t('connectionConsumerSecret')}</label>
              <input
                type="password"
                value={formData.api_secret}
                onChange={(e) => setFormData({...formData, api_secret: e.target.value})}
                placeholder="API Secret"
                required
              />
            </div>
          )}

          {formError && <div className="error">{formError}</div>}

          <button type="submit" className="btn-primary">{t('connectionBtnSubmit')}</button>
        </form>
      )}

      {loading ? (
        <div className="loading">{t('connectionsLoading')}</div>
      ) : connections.length === 0 ? (
        <div className="empty-state">{t('connectionsEmpty')}</div>
      ) : (
        <div className="connections-list">
          {connections.map((conn) => (
            <div key={conn.id} className="connection-card">
              <div className="connection-header">
                <div>
                  <h3>{conn.name}</h3>
                  <span className={`platform-badge ${conn.platform}`}>
                    {conn.platform}
                  </span>
                </div>
                <span className={`status-indicator ${conn.is_active ? 'active' : 'inactive'}`}>
                  {conn.is_active ? t('connectionActive') : t('connectionInactive')}
                </span>
              </div>

              <div className="connection-info">
                <div><strong>URL:</strong> {conn.store_url}</div>
                {conn.last_sync && (
                  <div><strong>{t('connectionLastSync')}:</strong> {new Date(conn.last_sync).toLocaleString('pl-PL')}</div>
                )}
              </div>

              <div className="connection-actions">
                <button
                  className="btn-secondary"
                  onClick={() => handleSync(conn.id)}
                  disabled={!conn.is_active || syncing === conn.id}
                >
                  {syncing === conn.id ? t('btnSyncing') : t('btnSync')}
                </button>
                <button
                  className="btn-danger"
                  onClick={() => handleDelete(conn.id)}
                >
                  {t('btnDelete')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
