import React, { useState, useEffect } from 'react';

const PERIOD_OPTIONS = [
  { label: 'Every hour', value: 'hourly' },
  { label: 'Every day', value: 'daily' },
  { label: 'Every week', value: 'weekly' },
];

const Notifications = () => {
  const [message, setMessage] = useState('');
  const [period, setPeriod] = useState('hourly');
  const [sessionId, setSessionId] = useState('');
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    // Here, session_id is populated automatically; you can customize this as needed
    // For demo, using a random sessionId
    const sid = localStorage.getItem('session_id') || Math.random().toString(36).slice(2);
    setSessionId(sid);
    localStorage.setItem('session_id', sid);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback('Sending...');
    try {
      const res = await fetch('http://localhost:8000/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: message,
          message,
          session_id: sessionId,
          period,
        }),
      });
      if (res.ok) {
        setFeedback('Notification scheduled!');
      } else {
        setFeedback('Failed to schedule notification.');
      }
    } catch (error) {
      setFeedback('Error sending notification.');
    }
  };

  return (
    <div className="notification-page">
      <h1>Schedule Notification</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: 500 }}>
        <label>
          Notification Message:
          <textarea
            value={message}
            onChange={e => setMessage(e.target.value)}
            required
            rows={4}
            style={{ width: '100%' }}
          />
        </label>
        <br /><br />
        <label>
          Notification Period:
          <select value={period} onChange={e => setPeriod(e.target.value)}>
            {PERIOD_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </label>
        <br /><br />
        <button type="submit">Send Notification</button>
        <div style={{ marginTop: 16 }}>{feedback}</div>
      </form>
    </div>
  );
};

export default Notifications;
