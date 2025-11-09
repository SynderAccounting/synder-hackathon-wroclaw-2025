import { useEffect, useState } from 'react';

export const UpdateIndicator = ({ isUpdating }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!isUpdating) {
      return;
    }

    setVisible(true);
    const timer = setTimeout(() => setVisible(false), 2000);
    return () => clearTimeout(timer);
  }, [isUpdating]);

  if (!visible) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in">
      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
      <span>Updating...</span>
    </div>
  );
};
