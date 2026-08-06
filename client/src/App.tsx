import { useState, useEffect } from 'react';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import LandingPage from '@/pages/LandingPage';
import SignInPage from '@/pages/SignInPage';
import Dashboard from '@/pages/Dashboard';

type Page = 'home' | 'signin' | 'dashboard';

function AppContent() {
  const [page, setPage] = useState<Page>('home');
  const { isAuthenticated } = useAuth();

  const navigate = (p: string) => {
    if (p === 'dashboard' && !isAuthenticated) {
      setPage('signin');
      return;
    }
    setPage(p as Page);
    window.scrollTo(0, 0);
  };

  useEffect(() => {
    if (page === 'dashboard' && !isAuthenticated) setPage('signin');
  }, [isAuthenticated, page]);

  if (page === 'signin') {
    return <SignInPage onNavigate={navigate} />;
  }
  if (page === 'dashboard') {
    return <Dashboard onNavigate={navigate} />;
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
