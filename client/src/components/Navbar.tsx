import { useState } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { Bot, Menu, X, Sun, Moon } from 'lucide-react';

interface NavbarProps {
  onNavigate: (page: string) => void;
}

export default function Navbar({ onNavigate }: NavbarProps) {
  const { isDark, toggleTheme } = useTheme();
  const { isAuthenticated } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const links = [
    { label: 'Features', target: 'features' },
    { label: 'How It Works', target: 'how-it-works' },
    { label: 'Contact', target: 'templates' },
  ];

  const handleScrollToSection = (target: string) => {
    const section = document.getElementById(target);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      onNavigate('home');
      setTimeout(() => {
        document.getElementById(target)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
    setMobileOpen(false);
  };

  return (
    <nav className={`sticky top-0 z-50 border-b ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'} shadow-sm`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button onClick={() => onNavigate('home')} className="flex items-center gap-2">
            <img src="/images/logo.png" alt="AITicketPilot logo" className="h-10 w-10 object-contain shrink-0" />
            <div className="text-left">
              <div className={`font-bold text-base leading-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>AITicketPilot</div>
              <div className={`text-[9px] font-semibold tracking-wider uppercase ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>Smarter Support</div>
            </div>
          </button>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-8">
            {links.map(link => (
              <button
                key={link.label}
                type="button"
                onClick={() => handleScrollToSection(link.target)}
                className={`text-sm font-medium transition-colors ${isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}
              >
                {link.label}
              </button>
            ))}
          </div>

          {/* Right actions */}
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${isDark ? 'hover:bg-gray-800 text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            {isAuthenticated ? (
              <button
                onClick={() => onNavigate('dashboard')}
                className="bg-blue-600 text-white text-sm font-semibold px-5 py-2 rounded-xl hover:bg-blue-700 transition-colors"
              >
                Dashboard
              </button>
            ) : (
              <>
                <button
                  onClick={() => onNavigate('signin')}
                  className={`text-sm font-medium px-4 py-2 rounded-xl transition-colors ${isDark ? 'text-gray-300 hover:text-white hover:bg-gray-800' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  Sign In
                </button>
                <button
                  onClick={() => onNavigate('signin')}
                  className="bg-blue-600 text-white text-sm font-semibold px-5 py-2 rounded-xl hover:bg-blue-700 transition-colors"
                >
                  Get Started
                </button>
              </>
            )}
          </div>

          {/* Mobile menu toggle */}
          <div className="flex md:hidden items-center gap-2">
            <button onClick={toggleTheme} className={`p-2 rounded-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <button onClick={() => setMobileOpen(o => !o)} className={`p-2 rounded-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className={`md:hidden border-t px-4 py-4 space-y-3 ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'}`}>
          {links.map(link => (
            <button
              key={link.label}
              type="button"
              onClick={() => handleScrollToSection(link.target)}
              className={`block w-full text-left text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}
            >
              {link.label}
            </button>
          ))}
          <div className="flex gap-3 pt-2">
            <button onClick={() => { onNavigate('signin'); setMobileOpen(false); }} className={`flex-1 text-sm font-medium py-2 rounded-xl border ${isDark ? 'border-gray-700 text-gray-300' : 'border-gray-200 text-gray-700'}`}>Sign In</button>
            <button onClick={() => { onNavigate('signin'); setMobileOpen(false); }} className="flex-1 bg-blue-600 text-white text-sm font-semibold py-2 rounded-xl hover:bg-blue-700">Get Started</button>
          </div>
        </div>
      )}
    </nav>
  );
}
