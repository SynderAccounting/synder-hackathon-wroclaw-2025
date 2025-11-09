import { useEffect } from 'react';

export default function Notification({ type, title, message, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`notification ${type}`}>
      <div className="notification-title">{title}</div>
      <div className="notification-message">{message}</div>
    </div>
  );
}
