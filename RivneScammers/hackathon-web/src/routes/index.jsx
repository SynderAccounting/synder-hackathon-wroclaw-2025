import { createBrowserRouter } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import Dashboard from '../pages/Dashboard';
import Management from '../pages/Management';
import Products from '../pages/Products';
import Export from '../pages/Export';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Settings from '../pages/Settings';
import NotFound from '../pages/NotFound';
import Home from '../pages/Home';
import MLSuggestions from '../pages/MLSuggestions';

export const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/dashboard', element: <DashboardLayout><Dashboard /></DashboardLayout> },
  { path: '/management', element: <DashboardLayout><Management /></DashboardLayout> },
  { path: '/products', element: <DashboardLayout><Products /></DashboardLayout> },
  { path: '/ml-suggestions', element: <DashboardLayout><MLSuggestions /></DashboardLayout> },
  { path: '/export', element: <DashboardLayout><Export /></DashboardLayout> },
  { path: '/settings', element: <DashboardLayout><Settings /></DashboardLayout> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '*', element: <NotFound /> },
]);
