import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTranslation } from '../i18n/LanguageContext';

export default function HistoryPanel({ refreshTrigger }) {
  const { t } = useTranslation();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getEvents(10);
      setEvents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, [refreshTrigger]);

  const formatDate = (dateString) => {
    // SQLite returns dates in format: "2025-11-08 22:26:31" (local time, not UTC)
    // Parse and display exact date and time
    const date = new Date(dateString.replace(' ', 'T'));

    return date.toLocaleString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="history-panel">
      <h3>{t('historyTitle')}</h3>

      {loading && <div className="loading">{t('historyLoading')}</div>}

      {error && <div className="error">{t('historyError')}: {error}</div>}

      {!loading && !error && events.length === 0 && (
        <div className="empty-state">{t('historyEmpty')}</div>
      )}

      {!loading && !error && events.length > 0 && (
        <div>
          {events.map((event) => (
            <div key={event.id} className="event-item">
              <div className="event-time">{formatDate(event.created_at)}</div>
              <div className="event-description">{event.description}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
