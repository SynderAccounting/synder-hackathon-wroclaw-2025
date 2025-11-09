import { useState, useEffect } from 'react'
import { ThemeProvider, AuthProvider, useAuth } from './contexts'
import { Navbar } from './components/navbar'
import { SimpleRouter } from './components/SimpleRouter'
import { Login } from './features/user'
import { HomePage, LoginPage, RegisterPage, DashboardPage, OrdersPage, StatisticsPage, RefundsPage } from './pages'
import './App.css'

function AppContent() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname)
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // Redirect authenticated users from home to dashboard
  useEffect(() => {
    if (isAuthenticated && currentPath === '/') {
      window.history.pushState({}, '', '/dashboard')
      setCurrentPath('/dashboard')
    }
  }, [isAuthenticated, currentPath])

  const isLoginPage = currentPath === '/login'
  const isRegisterPage = currentPath === '/register'

  return (
    <>
      <Navbar
        userComponent={!isLoginPage && !isRegisterPage ? <Login /> : undefined}
        isLoggedIn={isAuthenticated}
      />
      <SimpleRouter
        routes={[
          { path: '/', component: HomePage },
          { path: '/login', component: LoginPage },
          { path: '/register', component: RegisterPage },
          { path: '/dashboard', component: DashboardPage },
          { path: '/orders', component: OrdersPage },
          { path: '/statistics', component: StatisticsPage },
          { path: '/refunds', component: RefundsPage },
        ]}
      />
    </>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  )
}