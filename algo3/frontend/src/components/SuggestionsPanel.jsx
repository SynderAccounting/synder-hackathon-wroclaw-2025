import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTranslation } from '../i18n/LanguageContext';

export default function SuggestionsPanel({ product, onApplied }) {
  const { t } = useTranslation();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [applying, setApplying] = useState(null);

  useEffect(() => {
    if (!product) {
      setSuggestions([]);
      return;
    }

    const loadSuggestions = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getSuggestions(product.id);
        setSuggestions(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadSuggestions();
  }, [product]);

  const handleApply = async (suggestion) => {
    setApplying(suggestion.id);
    try {
      const result = await api.applySuggestion(suggestion.id);

      // Update local state
      setSuggestions(suggestions.map(s =>
        s.id === suggestion.id
          ? { ...s, status: 'applied', applied_at: result.applied_at }
          : s
      ));

      onApplied({
        type: 'success',
        title: t('notifSuccess'),
        message: result.message,
      });
    } catch (err) {
      onApplied({
        type: 'error',
        title: t('notifError'),
        message: err.message,
      });
    } finally {
      setApplying(null);
    }
  };

  const getSuggestionTypeLabel = (type) => {
    const labels = {
      price: t('suggestionTypePrice'),
      promo: t('suggestionTypePromo'),
      bundle: t('suggestionTypeBundle'),
      restock: t('suggestionTypeRestock'),
    };
    return labels[type] || type;
  };

  if (!product) {
    return (
      <div className="suggestions-panel">
        <h3>{t('suggestionsTitle')}</h3>
        <div className="empty-state">
          {t('suggestionsSelectProduct')}
        </div>
      </div>
    );
  }

  return (
    <div className="suggestions-panel">
      <h3>{t('suggestionsForProduct')}: {product.name}</h3>

      {loading && <div className="loading">{t('suggestionsLoading')}</div>}

      {error && <div className="error">{t('suggestionsError')}: {error}</div>}

      {!loading && !error && suggestions.length === 0 && (
        <div className="empty-state">{t('suggestionsEmpty')}</div>
      )}

      {!loading && !error && suggestions.length > 0 && (
        <div>
          {suggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className={`suggestion-card ${suggestion.status}`}
            >
              <div className="suggestion-header">
                <span className={`suggestion-badge ${suggestion.type}`}>
                  {getSuggestionTypeLabel(suggestion.type)}
                </span>
                <span className={`suggestion-status ${suggestion.status}`}>
                  {suggestion.status === 'new' ? t('suggestionStatusNew') : t('suggestionStatusApplied')}
                </span>
              </div>

              <div className="suggestion-description">
                {suggestion.description}
              </div>

              {suggestion.status === 'new' && (
                <button
                  className="apply-button"
                  onClick={() => handleApply(suggestion)}
                  disabled={applying === suggestion.id}
                >
                  {applying === suggestion.id ? t('btnApplying') : t('btnApply')}
                </button>
              )}

              {suggestion.status === 'applied' && suggestion.applied_at && (
                <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '8px' }}>
                  {t('suggestionAppliedAt')}: {new Date(suggestion.applied_at).toLocaleString('pl-PL')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
