import { useState, useEffect } from 'react';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import LandingPage from '@/pages/LandingPage';
import SignInPage from '@/pages/SignInPage';
import SignUpPage from '@/pages/SignUpPage';
import Dashboard from '@/pages/Dashboard';

type Page = 'home' | 'signin' | 'signup' | 'dashboard';

function AppContent() {
  const [page, setPage] = useState<Page>('home');
  const { isAuthenticated } = useAuth();
  const [dashboardActive, setDashboardActive] = useState<string | undefined>(undefined);

  const navigate = (p: string) => {
    // allow target formats like 'dashboard:My Tickets' to open dashboard on a specific subpage
    if (p.startsWith('dashboard:')) {
      const [, sub] = p.split(':');
      if (!isAuthenticated) {
        // if not authenticated, go to signin and remember desired subpage
        setPage('signin');
        setDashboardActive(sub);
        return;
      }
      setDashboardActive(sub);
      setPage('dashboard');
      return;
    }

    if (p === 'dashboard') {
      if (!isAuthenticated) {
        setPage('signin');
        setDashboardActive(undefined);
        return;
      }
      setPage('dashboard');
      return;
    }

    // navigating to other pages should clear any pending dashboard target
    setDashboardActive(undefined);
    setPage(p as Page);
    window.scrollTo(0, 0);
  };

  useEffect(() => {
    if (page === 'dashboard' && !isAuthenticated) setPage('signin');
  }, [isAuthenticated, page]);

  if (page === 'signin') {
    return <SignInPage onNavigate={navigate} />;
  }
  if (page === 'signup') {
    return <SignUpPage onNavigate={navigate} />;
  }
  if (page === 'dashboard') {
    return <Dashboard onNavigate={navigate} initialPage={dashboardActive as any} />;
  }
  return (
    <>
      <Navbar onNavigate={navigate} />
      <LandingPage onNavigate={navigate} />
    </>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
