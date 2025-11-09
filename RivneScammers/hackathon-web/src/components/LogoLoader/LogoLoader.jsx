import React from 'react';
import logo from '../../assets/logo.svg';
import './LogoLoader.css';

export const LogoLoader = ({ isLoading, message = 'Loading data...' }) => {
  if (!isLoading) return null;

  return (
    <div className="logo-loader-overlay bg-slate-950/90 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <img src={logo} className="logo-pulse" alt="logo" />
        <div className="text-slate-300 text-sm animate-pulse text-center px-4">{message}</div>
        <div className="flex gap-1" aria-hidden="true">
          <div className="loader-dot" style={{ animationDelay: '0ms' }} />
          <div className="loader-dot" style={{ animationDelay: '150ms' }} />
          <div className="loader-dot" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};
