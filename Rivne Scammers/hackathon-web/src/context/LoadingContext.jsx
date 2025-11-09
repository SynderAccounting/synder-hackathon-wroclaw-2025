import React, { createContext, useContext, useMemo, useState } from 'react';

const LoadingContext = createContext({
  isGlobalLoading: false,
  setIsGlobalLoading: () => {},
  loadingMessage: 'Loading...',
  setLoadingMessage: () => {},
});

export const LoadingProvider = ({ children }) => {
  const [isGlobalLoading, setIsGlobalLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Loading...');

  const value = useMemo(
    () => ({
      isGlobalLoading,
      setIsGlobalLoading,
      loadingMessage,
      setLoadingMessage,
    }),
    [isGlobalLoading, loadingMessage],
  );

  return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
};

export const useLoading = () => useContext(LoadingContext);
