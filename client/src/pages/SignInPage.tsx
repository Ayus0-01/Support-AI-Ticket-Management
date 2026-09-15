import { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { Bot, Sun, Moon, ArrowLeft, Eye, EyeOff, Lock, Mail, ShieldCheck, Sparkles } from 'lucide-react';

interface SignInPageProps {
  onNavigate: (page: string) => void;
}

const REMEMBER_KEY = 'aiticket_remember';

export default function SignInPage({ onNavigate }: SignInPageProps) {
  const { isDark, toggleTheme } = useTheme();
  const { signIn, isAuthenticated } = useAuth();

  const saved = (() => {
    try { return JSON.parse(localStorage.getItem(REMEMBER_KEY) ?? 'null'); } catch { return null; }
  })();

  const [email, setEmail] = useState<string>(saved?.email ?? '');
  const [password, setPassword] = useState<string>(saved?.password ?? '');
  const [showPw, setShowPw]     = useState(false);
  const [remember, setRemember] = useState<boolean>(!!saved);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [shouldNavigateToDashboard, setShouldNavigateToDashboard] = useState(false);

  /* Keep saved state in sync when remember toggle changes */
  useEffect(() => {
    if (!remember) localStorage.removeItem(REMEMBER_KEY);
  }, [remember]);

  // signIn schedules a React state update. Wait until this component receives
  // the authenticated context value before asking App to render the dashboard.
  useEffect(() => {
    if (shouldNavigateToDashboard && isAuthenticated) {
      setShouldNavigateToDashboard(false);
      onNavigate('dashboard');
    }
  }, [isAuthenticated, onNavigate, shouldNavigateToDashboard]);

  const attemptSignIn = async (usr: string, pw: string) => {
    setError("");
    setLoading(true);

    try {
      const res = await signIn(usr, pw);
      setLoading(false);

      if (res.success) {
        setShouldNavigateToDashboard(true);
      } else {
        setError(res.message || "Invalid email or password.");
      }
    } catch (error) {
      setLoading(false);
      setError("Unable to connect to the server.");
      console.error(error);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    attemptSignIn(email, password);
  };

  return (
    <div className={`min-h-screen flex ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>

      {/* ── Left brand panel ──────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-1/2 relative p-12 flex-col justify-between overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/images/login.jpg')" }}
        />
        {/* Dark contrast gradient overlay so white text is crisp and readable while keeping background image visible */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950/85 via-slate-950/65 to-gray-950/50 backdrop-blur-[1px]" />

        <div className="relative z-10">
          <button onClick={() => onNavigate('home')} className="flex items-center gap-2 text-white">
            <img src="/images/logo.png" alt="AITicketPilot logo" className="h-10 w-10 object-contain shrink-0 drop-shadow-md" />
            <div>
              <p className="font-bold text-base leading-tight text-white drop-shadow-sm">AITicketPilot</p>
              <p className="text-[9px] font-bold tracking-widest uppercase text-blue-200 drop-shadow-sm">Smarter Support. Faster Resolution.</p>
            </div>
          </button>
        </div>

        <div className="relative z-10 text-white max-w-[700px]">
          <Sparkles className="w-10 h-10 mb-6 text-blue-400 drop-shadow-md" />
          <h2 className="text-4xl font-extrabold leading-tight text-white drop-shadow-md">Resolve tickets faster with your AI copilot.</h2>
          <p className="mt-4 text-blue-100 text-lg font-bold drop-shadow-md">Smart routing, instant replies, and live analytics — all in one workspace.</p>
          <div className="mt-10 space-y-4">
            {['AI-powered ticket routing', 'Instant suggested replies', 'Real-time support analytics'].map(t => (
              <div key={t} className="flex items-center gap-3 text-white font-bold drop-shadow-sm">
                <ShieldCheck className="w-5 h-5 text-blue-400 shrink-0" />
                <span className="text-sm font-bold">{t}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-gray-200 text-xs font-bold drop-shadow-md">© 2026 AITicketPilot. All rights reserved.</p>
      </div>

      {/* ── Right form panel ──────────────────────────────────────── */}
      <div className="flex-1 flex flex-col">
        {/* Top row */}
        <div className="flex items-center justify-between px-6 pt-5 pb-2">
          <button
            onClick={() => onNavigate('home')}
            className={`flex items-center gap-1.5 text-sm font-medium ${isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}
          >
            <ArrowLeft className="w-4 h-4" /> Back to home
          </button>
          <button onClick={toggleTheme} className={`p-2 rounded-lg ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}>
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>

        <div className="flex-1 flex items-center justify-center px-6 py-10">
          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="lg:hidden flex items-center gap-2 mb-8">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className={`font-bold text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>AITicketPilot</span>
            </div>

            <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Welcome back</h1>
            <p className={`mt-1 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Sign in to your support workspace.</p>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4 mt-6">
              {/* Email */}
              <div>
                <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Email address</label>
                <div className="relative">
                  <Mail className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm outline-none transition-colors focus:border-blue-500 ${isDark ? 'bg-gray-900 border-gray-700 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'}`}
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Password</label>
                  <a href="#" className="text-xs font-medium text-blue-600 hover:text-blue-700">Forgot password?</a>
                </div>
                <div className="relative">
                  <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
                  <input
                    type={showPw ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className={`w-full pl-10 pr-10 py-3 rounded-xl border text-sm outline-none transition-colors focus:border-blue-500 ${isDark ? 'bg-gray-900 border-gray-700 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'}`}
                    required
                  />
                  <button type="button" onClick={() => setShowPw(p => !p)} className={`absolute right-3 top-1/2 -translate-y-1/2 ${isDark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'}`}>
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember me */}
              <div className="flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => setRemember(r => !r)}
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors shrink-0 ${remember ? 'bg-blue-600 border-blue-600' : isDark ? 'border-gray-600 bg-transparent' : 'border-gray-300 bg-white'}`}
                >
                  {remember && (
                    <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>
                <span className={`text-sm select-none cursor-pointer ${isDark ? 'text-gray-300' : 'text-gray-600'}`} onClick={() => setRemember(r => !r)}>
                  Remember me — save my password on this device
                </span>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">{error}</div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2 mt-1"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                    </svg>
                    Signing in...
                  </>
                ) : 'Sign In'}
              </button>
            </form>

            <p className={`mt-6 text-center text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Don't have an account?{' '}
              <button onClick={() => onNavigate('signup')} className="font-semibold text-blue-600 hover:text-blue-700"> Get started free </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
