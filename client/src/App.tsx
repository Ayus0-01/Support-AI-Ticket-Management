import { useState, useEffect, useRef } from 'react';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import LandingPage from '@/pages/LandingPage';
import SignInPage from '@/pages/SignInPage';
import SignUpPage from '@/pages/SignUpPage';
import UserDashboard from '@/pages/UserDashboard';
import AgentDashboard from '@/pages/AgentDashboard';
import AdminDashboard from '@/pages/AdminDashboard';
import SupportManagerDashboard from '@/pages/SupportManagerDashboard';
import type { NavPage } from '@/pages/Dashboard';
import api from '@/api';

type Page = 'home' | 'signin' | 'signup' | 'dashboard' | 'verify' | 'verify-pending';

function VerificationPendingPage({ email, onNavigate }: { email: string; onNavigate: (page: string, email?: string) => void }) {
  const [resending, setResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');

  const resend = async () => {
    if (!email) {
      setResendMessage('Return to registration and enter your email address to request a link.');
      return;
    }
    setResending(true);
    setResendMessage('');
    try {
      const response = await api.post('/api/auth/resend-verification/', { email });
      setResendMessage(response.data?.message || 'If the account needs verification, a fresh link has been sent.');
    } catch (error: any) {
      setResendMessage(error?.response?.data?.message || 'Unable to request a verification email. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <section className="max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-lg dark:border-slate-800 dark:bg-slate-900">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Check your email</h1>
        <p className="mt-4 text-slate-600 dark:text-slate-300" role="status">
          A verification link was sent to <strong>{email}</strong>. Open that link to verify the address, then sign in.
        </p>
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">If you don’t see it, check your spam folder.</p>
        <button className="mt-4 font-semibold text-blue-600 underline disabled:opacity-60" disabled={resending} onClick={resend}>
          {resending ? 'Sending…' : 'Resend verification email'}
        </button>
        {resendMessage && <p className="mt-3 text-sm text-slate-600 dark:text-slate-300" role="status">{resendMessage}</p>}
        <button className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white" onClick={() => onNavigate('signin')}>
          Continue to sign in
        </button>
      </section>
    </main>
  );
}

function VerifyEmailPage({ onNavigate }: { onNavigate: (page: string) => void }) {
  const [message, setMessage] = useState('Verifying your email address...');
  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('verify_email');
    if (!token) {
      setMessage('This verification link is missing its token.');
      return;
    }
    window.history.replaceState({}, '', window.location.pathname);
    api.post('/api/auth/verify-email/', { token })
      .then((response) => setMessage(response.data?.message || 'Email verified. You can sign in.'))
      .catch((error) => setMessage(error?.response?.data?.message || 'Email verification failed.'));
  }, []);
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <section className="max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-lg dark:border-slate-800 dark:bg-slate-900">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Email verification</h1>
        <p className="mt-4 text-slate-600 dark:text-slate-300" role="status">{message}</p>
        <button className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white" onClick={() => onNavigate('signin')}>Continue to sign in</button>
      </section>
    </main>
  );
}

const NAV_PAGES: NavPage[] = [
  'Dashboard',
  'My queue',
  'My Tickets',
  'Create Ticket',
  'Reports',
  'Knowledge Base',
  'Users',
  'Settings',
  'Taxonomy',
  'SLA policies',
  'Agent Assignment',
  'Escalations',
  'SLA Management',
  'Agent Performance',
  'AI Performance',
  'Notifications',
  'Profile',
];

function isNavPage(page: string | null): page is NavPage {
  return page !== null && NAV_PAGES.includes(page as NavPage);
}

function AppContent() {
  const [page, setPage] = useState<Page>(() => {
    if (new URLSearchParams(window.location.search).has('verify_email')) return 'verify';
    const browserPage = window.history.state?.appPage;
    if (['home', 'signin', 'signup', 'dashboard', 'verify', 'verify-pending'].includes(browserPage)) return browserPage as Page;
    return (sessionStorage.getItem("page") as Page) || "home";
  });
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState('');

  const {
    isAuthenticated,
    user,
    authLoading
  } = useAuth();

  const [dashboardActive, setDashboardActive] = useState<NavPage | undefined>(
    () => {
      const browserPage = window.history.state?.dashboardNavigation?.page || window.history.state?.dashboardActive;
      if (isNavPage(browserPage)) return browserPage;
      const savedPage = sessionStorage.getItem("dashboardActive");

      return isNavPage(savedPage) ? savedPage : undefined;
    }
  );
  const appPopState = useRef(false);

  useEffect(() => {
    const onPopState = (event: PopStateEvent) => {
      const state = event.state;
      if (!state?.appPage) return;
      appPopState.current = true;
      setPage(state.appPage as Page);
      setDashboardActive(isNavPage(state.dashboardNavigation?.page)
        ? state.dashboardNavigation.page
        : isNavPage(state.dashboardActive) ? state.dashboardActive : undefined);
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    const existing = window.history.state || {};
    const state = { ...existing, appPage: page, dashboardActive };
    if (appPopState.current) {
      window.history.replaceState(state, '');
      appPopState.current = false;
    } else if (existing.appPage !== page || existing.dashboardActive !== dashboardActive) {
      window.history.pushState(state, '');
    }
  }, [page, dashboardActive]);
  useEffect(() => {
    sessionStorage.setItem("page", page);

    if (dashboardActive) {
      sessionStorage.setItem(
        "dashboardActive",
        dashboardActive
      );
    } else if (page !== 'dashboard') {
      sessionStorage.removeItem("dashboardActive");
    }
  }, [page, dashboardActive]);

  const navigate = (p: string, email?: string) => {
    if (p === 'verify-pending') {
      setPendingVerificationEmail(email || '');
      setPage('verify-pending');
      return;
    }
    if (p.startsWith('dashboard:')) {
      const [, sub] = p.split(':');

      const validSub = sub && isNavPage(sub)
        ? sub
        : undefined;

      window.history.replaceState({
        ...(window.history.state || {}),
        dashboardNavigation: { page: validSub || 'Dashboard', ticketId: null },
      }, '');

      if (!isAuthenticated) {
        setPage('signin');
        setDashboardActive(validSub);
        return;
      }

  setDashboardActive(validSub);
  setPage('dashboard');
  return;
}

    if (p === 'dashboard') {
      window.history.replaceState({
        ...(window.history.state || {}),
        dashboardNavigation: { page: 'Dashboard', ticketId: null },
      }, '');
      if (!isAuthenticated) {
        setPage('signin');
        setDashboardActive(undefined);
        return;
      }

      setDashboardActive(undefined);
      setPage('dashboard');
      return;
    }

    setDashboardActive(undefined);
    setPage(p as Page);

    window.scrollTo(0, 0);
  };

  useEffect(() => {
    if (
      !authLoading &&
      page === 'dashboard'
      && !isAuthenticated
    ) {
      setPage('signin');
    }
  }, [
    authLoading,
    isAuthenticated,
    page,
  ]);

  if (authLoading) {
  return null;
  }

  if (page === 'signin') {
    return (
      <SignInPage
        onNavigate={navigate}
      />
    );
  }

  if (page === 'signup') {
    return (
      <SignUpPage
        onNavigate={navigate}
      />
    );
  }

  if (page === 'verify') {
    return <VerifyEmailPage onNavigate={navigate} />;
  }

  if (page === 'verify-pending') {
    return <VerificationPendingPage email={pendingVerificationEmail} onNavigate={navigate} />;
  }

  if (page === 'dashboard') {
    if (!user) {
      return null;
    }

    if (user.role === 'Support Manager') {
      return (
        <SupportManagerDashboard
          onNavigate={navigate}
          initialPage={dashboardActive}
        />
      );
    }

    if (user.role === 'Agent') {
      return (
        <AgentDashboard
          onNavigate={navigate}
          initialPage={dashboardActive}
        />
      );
    }

    if (user.role === 'Admin') {
      return (
        <AdminDashboard
          onNavigate={navigate}
          initialPage={dashboardActive}
        />
      );
    }

    return (
      <UserDashboard
        onNavigate={navigate}
        initialPage={dashboardActive}
      />
    );
  }

  return (
    <>
      <Navbar onNavigate={navigate} />

      <LandingPage
        onNavigate={navigate}
      />
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
