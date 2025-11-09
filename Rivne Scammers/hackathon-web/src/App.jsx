import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout';
import RequireAuth from './routes/RequireAuth.jsx';
import ErrorBoundary from './components/ErrorBoundary';
import { LoadingProvider, useLoading } from './context/LoadingContext';
import { LogoLoader } from './components/LogoLoader/LogoLoader';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Management = lazy(() => import('./pages/Management'));
const Products = lazy(() => import('./pages/Products'));
const Orders = lazy(() => import('./pages/Orders'));
const Export = lazy(() => import('./pages/Export'));
const Settings = lazy(() => import('./pages/Settings'));
const MLSuggestions = lazy(() => import('./pages/MLSuggestions'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Home = lazy(() => import('./pages/Home'));
const NotFound = lazy(() => import('./pages/NotFound'));

const AppRoutes = () => {
  const { isGlobalLoading, loadingMessage } = useLoading();

  return (
    <>
      <LogoLoader isLoading={isGlobalLoading} message={loadingMessage} />
      <Suspense fallback={<LogoLoader isLoading message="Loading application..." />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route element={<RequireAuth><DashboardLayout /></RequireAuth>}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/management" element={<Management />} />
            <Route path="/products" element={<Products />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/ml-suggestions" element={<MLSuggestions />} />
            <Route path="/export" element={<Export />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </>
  );
};

const App = () => {
  return (
    <ErrorBoundary>
      <LoadingProvider>
        <AppRoutes />
      </LoadingProvider>
    </ErrorBoundary>
  );
};

export default App;
