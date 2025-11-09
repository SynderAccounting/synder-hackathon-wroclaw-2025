import { useState, useEffect } from 'react';
import { api } from './services/api';
import ProductsTable from './components/ProductsTable';
import SuggestionsPanel from './components/SuggestionsPanel';
import HistoryPanel from './components/HistoryPanel';
import ConnectionsPanel from './components/ConnectionsPanel';
import Notification from './components/Notification';
import ProductDetailModal from './components/ProductDetailModal';
import { useTranslation } from './i18n/LanguageContext';

function App() {
  const { t, language, toggleLanguage } = useTranslation();
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [modalProduct, setModalProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);
  const [historyRefresh, setHistoryRefresh] = useState(0);
  const [generatingSuggestions, setGeneratingSuggestions] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProducts();
      setProducts(data);

      // Auto-select first product for demo
      if (data.length > 0 && !selectedProduct) {
        setSelectedProduct(data[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
  };

  const handleShowDetails = (product) => {
    setModalProduct(product);
  };

  const handleSuggestionApplied = (notificationData) => {
    setNotification(notificationData);
    // Refresh products to update price and active promotions
    loadProducts();
    // Refresh history when suggestion is applied
    setHistoryRefresh(prev => prev + 1);
  };

  const handleConnectionChange = () => {
    // Reload products when connections change
    loadProducts();
    setHistoryRefresh(prev => prev + 1);
  };

  const handleGenerateSuggestions = async () => {
    setGeneratingSuggestions(true);
    try {
      const result = await api.generateSuggestionsForAll();
      const message = t('notifSuggestionsGeneratedMsg')
        .replace('{analyzed}', result.products_analyzed)
        .replace('{created}', result.total_suggestions_created);
      setNotification({
        type: 'success',
        title: t('notifSuggestionsGenerated'),
        message: message,
      });
      // Refresh to show new suggestions
      if (selectedProduct) {
        setSelectedProduct({ ...selectedProduct });
      }
    } catch (err) {
      setNotification({
        type: 'error',
        title: t('notifError'),
        message: `${t('notifSuggestionsError')}: ${err.message}`,
      });
    } finally {
      setGeneratingSuggestions(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>{t('appTitle')}</h1>
          <p>{t('appSubtitle')}</p>
        </div>
        <button
          onClick={toggleLanguage}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            cursor: 'pointer',
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: 'white'
          }}
        >
          {language === 'pl' ? '🇬🇧 English' : '🇵🇱 Polski'}
        </button>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          {t('tabProducts')}
        </button>
        <button
          className={`tab ${activeTab === 'connections' ? 'active' : ''}`}
          onClick={() => setActiveTab('connections')}
        >
          {t('tabConnections')}
        </button>
      </div>

      {activeTab === 'connections' && (
        <ConnectionsPanel onConnectionChange={handleConnectionChange} />
      )}

      {activeTab === 'products' && (
        <>
          <div className="main-content">
            <div className="products-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 className="section-title" style={{ margin: 0 }}>{t('productsSectionTitle')}</h2>
                {products.length > 0 && (
                  <button
                    className="btn-primary"
                    onClick={handleGenerateSuggestions}
                    disabled={generatingSuggestions}
                    style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                  >
                    {generatingSuggestions ? t('btnGenerating') : t('btnGenerateAI')}
                  </button>
                )}
              </div>

              {loading && <div className="loading">{t('productsLoading')}</div>}

              {error && (
                <div className="error">
                  {t('productsError')}: {error}
                </div>
              )}

              {!loading && !error && products.length === 0 && (
                <div className="empty-state">
                  {t('productsEmpty')}
                </div>
              )}

              {!loading && !error && products.length > 0 && (
                <ProductsTable
                  products={products}
                  selectedProduct={selectedProduct}
                  onSelectProduct={handleProductSelect}
                  onShowDetails={handleShowDetails}
                />
              )}
            </div>

            <div className="sidebar">
              <SuggestionsPanel
                product={selectedProduct}
                onApplied={handleSuggestionApplied}
              />
              <HistoryPanel refreshTrigger={historyRefresh} />
            </div>
          </div>
        </>
      )}

      {notification && (
        <Notification
          type={notification.type}
          title={notification.title}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}

      {modalProduct && (
        <ProductDetailModal
          product={modalProduct}
          onClose={() => setModalProduct(null)}
        />
      )}
    </div>
  );
}

export default App;
