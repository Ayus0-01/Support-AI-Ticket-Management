import { useState, useEffect, useRef } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import {
  Bot, Sun, Moon, LayoutDashboard, Ticket, PlusCircle, Sparkles, BarChart3,
  BookOpen, Users, Settings, LogOut, Search, Bell, HelpCircle, MessageSquare,
  Send, ChevronRight, Tag, Filter, Menu, X, TrendingUp, Ticket as TicketIcon,
  PlayCircle, CheckCircle2, AlertCircle, Zap,
} from 'lucide-react';

interface DashboardProps {
  onNavigate: (page: string) => void;
}

type NavPage = 'Dashboard' | 'My Tickets' | 'Create Ticket' | 'AI Assistant' | 'Reports' | 'Knowledge Base' | 'Users' | 'Settings';

interface Ticket {
  id: string;
  subject: string;
  category: 'Bug' | 'Other' | 'Login' | 'Feature Request' | 'Billing' | 'Integration';
  priority: 'High' | 'Medium' | 'Low';
  status: 'In Progress' | 'Resolved' | 'Open';
}

const TICKETS: Ticket[] = [
  { id: 'TCK-128', subject: 'Sample Bug issue #1119',            category: 'Bug',             priority: 'High',   status: 'In Progress' },
  { id: 'TCK-127', subject: 'Sample Other issue #1118',          category: 'Other',           priority: 'Low',    status: 'Resolved'    },
  { id: 'TCK-126', subject: 'Sample Login issue #1117',          category: 'Login',           priority: 'Medium', status: 'In Progress' },
  { id: 'TCK-125', subject: 'Sample Bug issue #1116',            category: 'Bug',             priority: 'High',   status: 'In Progress' },
  { id: 'TCK-124', subject: 'Sample Feature Request issue #1115',category: 'Feature Request', priority: 'Medium', status: 'Resolved'    },
  { id: 'TCK-123', subject: 'Sample Billing issue #1114',        category: 'Billing',         priority: 'High',   status: 'Open'        },
  { id: 'TCK-122', subject: 'Sample Integration issue #1113',    category: 'Integration',     priority: 'Low',    status: 'Open'        },
  { id: 'TCK-121', subject: 'Sample Bug issue #1112',            category: 'Bug',             priority: 'Medium', status: 'Resolved'    },
];

const STATS = [
  { label: 'TOTAL TICKETS', value: 128, change: '+12.5%', icon: TicketIcon,    bg: 'bg-blue-50',   iconBg: 'bg-blue-100',   iconColor: 'text-blue-500'  },
  { label: 'OPEN TICKETS',  value: 27,  change: '+8.3%',  icon: AlertCircle,   bg: 'bg-amber-50',  iconBg: 'bg-amber-100',  iconColor: 'text-amber-500' },
  { label: 'IN PROGRESS',   value: 55,  change: '+5.7%',  icon: PlayCircle,    bg: 'bg-purple-50', iconBg: 'bg-purple-100', iconColor: 'text-purple-500'},
  { label: 'RESOLVED',      value: 46,  change: '+15.2%', icon: CheckCircle2,  bg: 'bg-green-50',  iconBg: 'bg-green-100',  iconColor: 'text-green-500' },
];

const priorityStyle: Record<string, string> = {
  High:   'bg-red-100 text-red-600',
  Medium: 'bg-amber-100 text-amber-600',
  Low:    'bg-green-100 text-green-600',
};
const statusStyle: Record<string, string> = {
  'In Progress': 'bg-blue-100 text-blue-600',
  Resolved:      'bg-green-100 text-green-600',
  Open:          'bg-gray-100 text-gray-600',
};
const darkPriorityStyle: Record<string, string> = {
  High:   'bg-red-500/15 text-red-400',
  Medium: 'bg-amber-500/15 text-amber-400',
  Low:    'bg-green-500/15 text-green-400',
};
const darkStatusStyle: Record<string, string> = {
  'In Progress': 'bg-blue-500/15 text-blue-400',
  Resolved:      'bg-green-500/15 text-green-400',
  Open:          'bg-gray-500/15 text-gray-400',
};

const AI_QUICK_ACTIONS = ['Summarize tickets', 'Show unresolved tickets', 'Draft reply', 'Escalate ticket'];

function DashboardHeroArt({ isDark, compact = false }: { isDark: boolean; compact?: boolean }) {
  return (
    <div className={`relative w-full overflow-hidden ${compact ? 'h-[180px]' : 'h-[420px]'}`}>
      <svg viewBox="0 0 1400 420" className="h-full w-full" role="img" aria-label="Customer support illustration">
        <defs>
          <linearGradient id="dashPanelBg" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#f2ebc7" />
            <stop offset="100%" stopColor="#efe7ba" />
          </linearGradient>
          <linearGradient id="heroBlue" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#0d6be6" />
            <stop offset="100%" stopColor="#0d4fa8" />
          </linearGradient>
          <linearGradient id="heroBlueSoft" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#67c8ff" />
            <stop offset="100%" stopColor="#1f6ae6" />
          </linearGradient>
        </defs>

        <rect width="1400" height="420" fill="url(#dashPanelBg)" />

        <g opacity="0.18">
          <rect x="38" y="96" width="220" height="160" rx="18" fill="#d1b7c6" />
          <rect x="260" y="110" width="150" height="190" rx="18" fill="#c7d5bc" />
          <rect x="970" y="90" width="240" height="160" rx="18" fill="#d5d5d5" />
        </g>

        <g transform="translate(40 50)">
          <g transform="translate(20 104)">
            <rect x="0" y="18" width="168" height="158" rx="22" fill="#1c6fe4" opacity="0.2" />
            <rect x="20" y="40" width="118" height="110" rx="12" fill="#e4effb" />
            <rect x="33" y="54" width="92" height="52" rx="8" fill="#93a9d9" opacity="0.45" />
            <rect x="38" y="114" width="18" height="20" rx="4" fill="#93a9d9" opacity="0.5" />
            <rect x="60" y="114" width="18" height="20" rx="4" fill="#93a9d9" opacity="0.5" />
            <rect x="82" y="114" width="18" height="20" rx="4" fill="#93a9d9" opacity="0.5" />
            <rect x="104" y="114" width="18" height="20" rx="4" fill="#93a9d9" opacity="0.5" />
          </g>

          <g transform="translate(160 110)">
            <circle cx="0" cy="0" r="14" fill="#f2c6b7" />
            <path d="M-18 40 L-4 22 L18 40 L10 110 L-10 110 Z" fill="#f2c6b7" />
            <path d="M-8 20 Q0 -24 18 10 L30 90 L-30 90 L-18 10 Z" fill="#f8d5cb" />
            <circle cx="0" cy="0" r="10" fill="#0b0d15" />
            <ellipse cx="-18" cy="-16" rx="8" ry="12" fill="#f3d9d1" />
            <ellipse cx="18" cy="-16" rx="8" ry="12" fill="#f3d9d1" />
            <rect x="-22" y="70" width="44" height="60" rx="20" fill="#d7e4ff" opacity="0.3" />
          </g>

          <g transform="translate(350 78)">
            <path d="M10 60 Q108 -10 190 52 L182 176 L20 180 Z" fill="#2aa370" opacity="0.94" />
            <path d="M70 20 L110 20 L126 100 L50 100 Z" fill="#f4f5f7" opacity="0.9" />
            <path d="M70 20 L90 10 L132 16 L126 100 L50 100 Z" fill="#dfe2ea" opacity="0.8" />
            <path d="M46 104 L178 104" stroke="#f2f5f8" strokeWidth="8" strokeLinecap="round" />
            <path d="M54 110 L96 108 L130 110" stroke="#94a6c7" strokeWidth="6" strokeLinecap="round" opacity="0.7" />
            <circle cx="110" cy="40" r="26" fill="#f0d768" />
            <circle cx="110" cy="40" r="12" fill="#fff" opacity="0.8" />
            <path d="M92 110 Q100 90 122 110" stroke="#0d111c" strokeWidth="10" strokeLinecap="round" fill="none" />
            <path d="M58 70 L38 90" stroke="#0d111c" strokeWidth="10" strokeLinecap="round" />
            <path d="M134 68 L167 93" stroke="#0d111c" strokeWidth="10" strokeLinecap="round" />
          </g>

          <g transform="translate(610 45)">
            <g>
              <circle cx="220" cy="180" r="160" fill="#0e5ec7" opacity="0.9" />
              <circle cx="220" cy="180" r="106" fill="#e4eef9" opacity="0.18" />
              <circle cx="220" cy="180" r="140" fill="none" stroke="#1d6be6" strokeWidth="18" opacity="0.6" />
              <circle cx="220" cy="180" r="120" fill="none" stroke="#a8d7ff" strokeWidth="9" opacity="0.7" />
              <path d="M92 183 C120 130, 170 105, 220 105 C278 105, 322 134, 344 183" fill="none" stroke="#0f50b8" strokeWidth="16" opacity="0.55" />
              <circle cx="220" cy="180" r="76" fill="#f0f5ff" />
              <circle cx="220" cy="180" r="60" fill="#f8f8f8" />
              <circle cx="220" cy="180" r="16" fill="#f0bf43" />
              <path d="M214 174 Q226 154 236 176" stroke="#3a4c7d" strokeWidth="9" strokeLinecap="round" fill="none" />
              <path d="M184 152 C196 137, 214 132, 222 142 C224 169, 204 170, 190 176" fill="#0b101e" opacity="0.9" />
              <path d="M252 150 C266 136, 280 136, 292 142 C300 160, 292 176, 274 180" fill="#0b101e" opacity="0.9" />
              <path d="M136 217 C161 253, 185 266, 220 266 C264 266, 286 245, 304 220" fill="none" stroke="#0d101d" strokeWidth="12" strokeLinecap="round" />
            </g>
            <g fill="#f5f7fb">
              <circle cx="110" cy="160" r="21" />
              <circle cx="150" cy="110" r="21" />
              <circle cx="294" cy="116" r="19" />
              <circle cx="332" cy="178" r="20" />
              <circle cx="298" cy="246" r="18" />
              <circle cx="144" cy="254" r="22" />
            </g>
            <g fill="#f3b82f">
              <circle cx="110" cy="160" r="9" />
              <circle cx="150" cy="110" r="9" />
              <circle cx="294" cy="116" r="8" />
              <circle cx="332" cy="178" r="8" />
              <circle cx="298" cy="246" r="8" />
              <circle cx="144" cy="254" r="8" />
            </g>
          </g>

          <g transform="translate(1160 95)">
            <rect x="0" y="30" width="90" height="140" rx="20" fill="#f6f5f5" opacity="0.9" />
            <rect x="18" y="54" width="52" height="68" rx="10" fill="#0f2b78" opacity="0.95" />
            <rect x="24" y="66" width="40" height="14" rx="7" fill="#0d9ae7" opacity="0.85" />
            <rect x="24" y="90" width="40" height="14" rx="7" fill="#72ccff" opacity="0.7" />
            <rect x="26" y="118" width="18" height="18" rx="9" fill="#f1b834" opacity="0.9" />
            <rect x="46" y="118" width="18" height="18" rx="9" fill="#f1b834" opacity="0.9" />
          </g>
        </g>
      </svg>
    </div>
  );
}

const navItems: { name: NavPage; icon: React.ElementType; badge?: string }[] = [
  { name: 'Dashboard',     icon: LayoutDashboard },
  { name: 'My Tickets',    icon: Ticket          },
  { name: 'Create Ticket', icon: PlusCircle      },
  { name: 'AI Assistant',  icon: Sparkles,  badge: 'BETA' },
  { name: 'Reports',       icon: BarChart3       },
  { name: 'Knowledge Base',icon: BookOpen        },
  { name: 'Users',         icon: Users           },
  { name: 'Settings',      icon: Settings        },
];

/* ─── sub-pages ──────────────────────────────────────────────────── */

function MyTicketsPage({ isDark }: { isDark: boolean }) {
  return (
    <div className="space-y-4">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>My Tickets</h2>
      <div className={`rounded-2xl border overflow-hidden ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        <table className="w-full text-sm">
          <thead>
            <tr className={isDark ? 'bg-gray-800' : 'bg-gray-50'}>
              {['Ticket ID', 'Subject', 'Category', 'Priority', 'Status'].map(h => (
                <th key={h} className={`text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className={`divide-y ${isDark ? 'divide-gray-800' : 'divide-gray-100'}`}>
            {TICKETS.map(t => (
              <tr key={t.id} className={isDark ? 'hover:bg-gray-800/60' : 'hover:bg-gray-50'}>
                <td className={`px-4 py-3 font-mono text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{t.id}</td>
                <td className={`px-4 py-3 font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{t.id}: {t.subject}</td>
                <td className={`px-4 py-3 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>{t.category}</td>
                <td className="px-4 py-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${isDark ? darkPriorityStyle[t.priority] : priorityStyle[t.priority]}`}>{t.priority}</span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${isDark ? darkStatusStyle[t.status] : statusStyle[t.status]}`}>{t.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CreateTicketPage({ isDark }: { isDark: boolean }) {
  const [form, setForm] = useState({ subject: '', category: 'Bug', priority: 'Medium', description: '' });
  const [submitted, setSubmitted] = useState(false);
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));
  const submit = (e: React.FormEvent) => { e.preventDefault(); setSubmitted(true); setTimeout(() => setSubmitted(false), 3000); };
  const field = `w-full px-3 py-2.5 rounded-xl border text-sm outline-none transition-colors focus:border-blue-500 ${isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900'}`;
  return (
    <div className="max-w-xl space-y-4">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Create Ticket</h2>
      {submitted && <div className="p-3 bg-green-50 border border-green-200 text-green-700 rounded-xl text-sm">Ticket created successfully!</div>}
      <form onSubmit={submit} className={`space-y-4 p-6 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        <div>
          <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Subject</label>
          <input value={form.subject} onChange={e => set('subject', e.target.value)} placeholder="Describe the issue briefly" className={field} required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Category</label>
            <select value={form.category} onChange={e => set('category', e.target.value)} className={field}>
              {['Bug', 'Feature Request', 'Billing', 'Login', 'Integration', 'Other'].map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Priority</label>
            <select value={form.priority} onChange={e => set('priority', e.target.value)} className={field}>
              {['Low', 'Medium', 'High'].map(p => <option key={p}>{p}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Description</label>
          <textarea value={form.description} onChange={e => set('description', e.target.value)} rows={4} placeholder="Provide details about the issue..." className={field} />
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-xl hover:bg-blue-700 transition-colors">Submit Ticket</button>
      </form>
    </div>
  );
}

function ReportsPage({ isDark }: { isDark: boolean }) {
  const bars = [65, 40, 80, 55, 90, 45, 70];
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return (
    <div className="space-y-6">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Reports</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`p-6 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
          <h3 className={`text-sm font-semibold mb-4 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Tickets This Week</h3>
          <div className="flex items-end gap-3 h-36">
            {bars.map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full bg-blue-500 rounded-t-lg" style={{ height: `${h}%` }} />
                <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{days[i]}</span>
              </div>
            ))}
          </div>
        </div>
        <div className={`p-6 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
          <h3 className={`text-sm font-semibold mb-4 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Tickets by Priority</h3>
          <div className="space-y-3">
            {[['High', 38, 'bg-red-500'], ['Medium', 44, 'bg-amber-500'], ['Low', 18, 'bg-green-500']].map(([label, pct, color]) => (
              <div key={label as string}>
                <div className="flex justify-between text-xs mb-1">
                  <span className={isDark ? 'text-gray-300' : 'text-gray-700'}>{label}</span>
                  <span className={isDark ? 'text-gray-400' : 'text-gray-500'}>{pct}%</span>
                </div>
                <div className={`h-2 rounded-full ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                  <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function KnowledgeBasePage({ isDark }: { isDark: boolean }) {
  const articles = [
    { title: 'How to reset your password', views: 1240, category: 'Login' },
    { title: 'Understanding your invoice', views: 980, category: 'Billing' },
    { title: 'API rate limiting explained', views: 756, category: 'Integration' },
    { title: 'Submitting a feature request', views: 543, category: 'Feature Request' },
    { title: 'Common bug reporting tips', views: 489, category: 'Bug' },
  ];
  return (
    <div className="space-y-4">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Knowledge Base</h2>
      <div className="grid gap-3">
        {articles.map(a => (
          <div key={a.title} className={`flex items-center gap-4 p-4 rounded-2xl border cursor-pointer transition-colors ${isDark ? 'bg-gray-900 border-gray-800 hover:border-gray-700' : 'bg-white border-gray-200 hover:border-blue-300'}`}>
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shrink-0"><BookOpen className="w-5 h-5 text-white" /></div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{a.title}</p>
              <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{a.category} · {a.views.toLocaleString()} views</p>
            </div>
            <ChevronRight className={`w-4 h-4 shrink-0 ${isDark ? 'text-gray-600' : 'text-gray-300'}`} />
          </div>
        ))}
      </div>
    </div>
  );
}

function UsersPage({ isDark }: { isDark: boolean }) {
  const users = [
    { name: 'Lakshmipriya Gutti', email: 'lakshmipriya@gmail.com', role: 'Admin', tickets: 32, avatar: 'L' },
    { name: 'Priya Mehra',        email: 'priya.m@company.com',    role: 'Agent', tickets: 21, avatar: 'P' },
    { name: 'Ravi Shankar',       email: 'ravi.s@company.com',     role: 'Agent', tickets: 18, avatar: 'R' },
    { name: 'Anita Rao',          email: 'anita.r@company.com',    role: 'Viewer',tickets: 5,  avatar: 'A' },
  ];
  return (
    <div className="space-y-4">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Users</h2>
      <div className={`rounded-2xl border overflow-hidden ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        <table className="w-full text-sm">
          <thead>
            <tr className={isDark ? 'bg-gray-800' : 'bg-gray-50'}>
              {['User', 'Role', 'Tickets Assigned'].map(h => (
                <th key={h} className={`text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className={`divide-y ${isDark ? 'divide-gray-800' : 'divide-gray-100'}`}>
            {users.map(u => (
              <tr key={u.email} className={isDark ? 'hover:bg-gray-800/60' : 'hover:bg-gray-50'}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white text-xs font-bold">{u.avatar}</div>
                    <div>
                      <p className={`font-medium text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>{u.name}</p>
                      <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{u.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${u.role === 'Admin' ? isDark ? 'bg-blue-500/15 text-blue-400' : 'bg-blue-100 text-blue-600' : isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>{u.role}</span>
                </td>
                <td className={`px-4 py-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{u.tickets}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SettingsPage({ isDark, toggleTheme }: { isDark: boolean; toggleTheme: () => void }) {
  return (
    <div className="max-w-xl space-y-4">
      <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Settings</h2>
      <div className={`p-6 rounded-2xl border space-y-5 ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>Dark Mode</p>
            <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Toggle between light and dark theme</p>
          </div>
          <button onClick={toggleTheme} className={`relative w-11 h-6 rounded-full transition-colors ${isDark ? 'bg-blue-600' : 'bg-gray-200'}`}>
            <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${isDark ? 'translate-x-5' : ''}`} />
          </button>
        </div>
        {[
          { label: 'Email Notifications', desc: 'Receive updates about ticket activity' },
          { label: 'AI Auto-Replies',     desc: 'Let AI send suggested replies automatically' },
          { label: 'Weekly Reports',      desc: 'Get a summary report every Monday' },
        ].map(s => (
          <div key={s.label} className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{s.label}</p>
              <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{s.desc}</p>
            </div>
            <button className="relative w-11 h-6 rounded-full bg-blue-600">
              <span className="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow translate-x-5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function AIAssistantPage({ isDark, chat, setChat }: { isDark: boolean; chat: { role: 'user' | 'ai'; text: string }[]; setChat: React.Dispatch<React.SetStateAction<{ role: 'user' | 'ai'; text: string }[]>> }) {
  const [msg, setMsg] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const send = () => {
    if (!msg.trim()) return;
    const text = msg;
    setMsg('');
    setChat(c => [...c, { role: 'user', text }]);
    setTimeout(() => setChat(c => [...c, { role: 'ai', text: "I've analyzed your request. Based on the current ticket queue, I recommend prioritizing the High-priority bug reports first. Want me to draft responses for them?" }]), 700);
  };
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chat]);
  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      <div className="flex items-center gap-3 mb-4">
        <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>AI Assistant</h2>
        <span className="text-xs font-bold bg-blue-600 text-white px-2 py-0.5 rounded-full">BETA</span>
      </div>
      <div className={`flex-1 overflow-y-auto rounded-2xl border p-5 space-y-4 ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        {chat.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'ai' && <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center mr-2 mt-0.5 shrink-0"><Sparkles className="w-3.5 h-3.5 text-white" /></div>}
            <div className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm ${m.role === 'user' ? 'bg-blue-600 text-white rounded-br-md' : isDark ? 'bg-gray-800 text-gray-200 rounded-bl-md' : 'bg-gray-100 text-gray-800 rounded-bl-md'}`}>{m.text}</div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className={`mt-3 flex items-center gap-2 px-4 py-3 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
        <input value={msg} onChange={e => setMsg(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} placeholder="Ask AI anything..." className={`flex-1 bg-transparent outline-none text-sm ${isDark ? 'text-white placeholder-gray-600' : 'text-gray-900 placeholder-gray-400'}`} />
        <button onClick={send} className="w-9 h-9 bg-blue-600 hover:bg-blue-700 rounded-xl flex items-center justify-center transition-colors"><Send className="w-4 h-4 text-white" /></button>
      </div>
    </div>
  );
}

/* ─── main dashboard ─────────────────────────────────────────────── */

export default function Dashboard({ onNavigate }: DashboardProps) {
  const { isDark, toggleTheme } = useTheme();
  const { user, signOut } = useAuth();
  const [activePage, setActivePage] = useState<NavPage>('Dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [quickInfo, setQuickInfo] = useState<'help' | 'messages' | 'alerts' | null>(null);
  const [aiChat, setAiChat] = useState<{ role: 'user' | 'ai'; text: string }[]>([
    { role: 'ai', text: `Hi ${user?.name?.split(' ')[0] ?? 'there'}! I am your AI helpdesk assistant. Click on a fast action chip below or ask me anything to get started.` },
  ]);
  const [aiInput, setAiInput] = useState('');

  const sendAi = (text?: string) => {
    const msg = text ?? aiInput;
    if (!msg.trim()) return;
    setAiInput('');
    setAiChat(c => [...c, { role: 'user', text: msg }]);
    setTimeout(() => setAiChat(c => [...c, { role: 'ai', text: "Got it! I've found 3 unresolved High-priority tickets. Shall I draft replies for each one and tag them for follow-up?" }]), 700);
  };

  const quickInfoContent = {
    help: {
      title: 'Help Center',
      text: 'Browse onboarding guides, escalation steps, and SLA policies for your support team.',
    },
    messages: {
      title: 'Messages',
      text: 'Customer replies are waiting for review. Use AI to draft responses and prioritize follow-ups.',
    },
    alerts: {
      title: 'Alerts',
      text: 'Three urgent tickets need attention and two SLA thresholds are approaching the deadline.',
    },
  };

  const handleQuickAction = (type: 'help' | 'messages' | 'alerts') => {
    setQuickInfo(current => (current === type ? null : type));
  };

  const handleSignOut = () => { signOut(); onNavigate('home'); };

  const renderPage = () => {
    switch (activePage) {
      case 'My Tickets':    return <MyTicketsPage isDark={isDark} />;
      case 'Create Ticket': return <CreateTicketPage isDark={isDark} />;
      case 'AI Assistant':  return <AIAssistantPage isDark={isDark} chat={aiChat} setChat={setAiChat} />;
      case 'Reports':       return <ReportsPage isDark={isDark} />;
      case 'Knowledge Base':return <KnowledgeBasePage isDark={isDark} />;
      case 'Users':         return <UsersPage isDark={isDark} />;
      case 'Settings':      return <SettingsPage isDark={isDark} toggleTheme={toggleTheme} />;
      default:              return null;
    }
  };

  return (
    <div className={`min-h-screen flex ${isDark ? 'bg-gray-950' : 'bg-slate-50'}`}>

      {/* ── Sidebar ───────────────────────────────────────────────── */}
      <>
        {sidebarOpen && <div className="fixed inset-0 bg-black/40 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />}
        <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:sticky top-0 z-40 h-screen w-64 shrink-0 flex flex-col transition-transform duration-300 ${isDark ? 'bg-gray-900 border-r border-gray-800' : 'bg-white border-r border-gray-200'}`}>

          {/* Logo */}
          <div className={`flex items-center gap-3 px-5 h-16 border-b shrink-0 ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
            <img src="/images/logo.png" alt="AITicketPilot logo" className="h-9 w-9 object-contain shrink-0" />
            <div>
              <p className={`text-sm font-bold leading-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>AITicketPilot</p>
              <p className={`text-[9px] font-semibold tracking-widest uppercase ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Smarter Support. Faster Resolution.</p>
            </div>
          </div>

          {/* Nav */}
          <nav className="flex-1 overflow-y-auto p-3 space-y-0.5">
            {navItems.map(item => {
              const active = activePage === item.name;
              return (
                <button
                  key={item.name}
                  onClick={() => { setActivePage(item.name); setSidebarOpen(false); }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${active ? 'bg-blue-600 text-white shadow-sm' : isDark ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
                >
                  <item.icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className={`ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full ${active ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-600'}`}>{item.badge}</span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User card */}
          <div className={`p-3 border-t shrink-0 ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
            <div className={`flex items-center gap-3 p-3 rounded-xl ${isDark ? 'bg-gray-800' : 'bg-gray-50'}`}>
              <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0">{user?.avatar}</div>
              <div className="min-w-0">
                <p className={`text-sm font-semibold truncate ${isDark ? 'text-white' : 'text-gray-900'}`}>{user?.name}</p>
                <p className="text-xs text-green-500 flex items-center gap-1"><span className="w-1.5 h-1.5 bg-green-500 rounded-full inline-block" /> {user?.role}</p>
              </div>
              <button onClick={handleSignOut} title="Sign out" className={`ml-auto p-1.5 rounded-lg ${isDark ? 'text-gray-500 hover:text-gray-300 hover:bg-gray-700' : 'text-gray-400 hover:text-gray-700 hover:bg-gray-200'}`}>
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </aside>
      </>

      {/* ── Main area ─────────────────────────────────────────────── */}
      <div className="flex-1 min-w-0 flex flex-col">

        {/* Top bar */}
        <header className={`sticky top-0 z-20 h-16 flex items-center gap-3 px-4 sm:px-6 border-b shrink-0 ${isDark ? 'bg-gray-950/90 border-gray-800 backdrop-blur' : 'bg-white/90 border-gray-200 backdrop-blur'}`}>
          <button onClick={() => setSidebarOpen(true)} className={`lg:hidden p-2 rounded-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
            <Menu className="w-5 h-5" />
          </button>

          <div>
            <h1 className={`text-lg font-bold leading-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>{activePage}</h1>
            {activePage === 'Dashboard' && (
              <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Welcome back, {user?.name?.split(' ')[0]} &#x1F44B;</p>
            )}
          </div>

          {/* Search */}
          <div className={`hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl flex-1 max-w-sm ml-4 ${isDark ? 'bg-gray-900' : 'bg-gray-100'}`}>
            <Search className={`w-4 h-4 shrink-0 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
            <input placeholder="Search tickets, users..." className={`bg-transparent outline-none text-sm flex-1 ${isDark ? 'text-white placeholder-gray-600' : 'text-gray-900 placeholder-gray-400'}`} />
          </div>

          <div className="flex items-center gap-1.5 ml-auto">
            <button onClick={toggleTheme} className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}>
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            <div className="relative">
              <button
                onClick={() => handleQuickAction('help')}
                className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <HelpCircle className="w-4 h-4" />
              </button>
              {quickInfo === 'help' && (
                <div className={`absolute right-0 top-11 w-64 rounded-xl border p-3 shadow-lg z-30 ${isDark ? 'bg-gray-900 border-gray-700 text-gray-200' : 'bg-white border-gray-200 text-gray-700'}`}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">Help Center</p>
                  <p className="mt-2 text-sm leading-relaxed">Browse onboarding guides, escalation steps, and SLA policies for your support team.</p>
                </div>
              )}
            </div>

            <div className="relative">
              <button
                onClick={() => handleQuickAction('messages')}
                className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <MessageSquare className="w-4 h-4" />
              </button>
              {quickInfo === 'messages' && (
                <div className={`absolute right-0 top-11 w-64 rounded-xl border p-3 shadow-lg z-30 ${isDark ? 'bg-gray-900 border-gray-700 text-gray-200' : 'bg-white border-gray-200 text-gray-700'}`}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">Messages</p>
                  <p className="mt-2 text-sm leading-relaxed">Customer replies are waiting for review. Use AI to draft responses and prioritize follow-ups.</p>
                </div>
              )}
            </div>

            <div className="relative">
              <button
                onClick={() => handleQuickAction('alerts')}
                className={`relative p-2 rounded-lg transition-colors ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
              </button>
              {quickInfo === 'alerts' && (
                <div className={`absolute right-0 top-11 w-64 rounded-xl border p-3 shadow-lg z-30 ${isDark ? 'bg-gray-900 border-gray-700 text-gray-200' : 'bg-white border-gray-200 text-gray-700'}`}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">Alerts</p>
                  <p className="mt-2 text-sm leading-relaxed">Three urgent tickets need attention and two SLA thresholds are approaching the deadline.</p>
                </div>
              )}
            </div>
            {/* User avatar */}
            <div className="relative ml-2 pl-3 border-l border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setProfileOpen(o => !o)}
                className="flex items-center gap-2 rounded-xl px-2 py-1.5 transition-colors hover:bg-gray-100/80 dark:hover:bg-gray-800"
              >
                <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">{user?.avatar}</div>
                <div className="hidden sm:block text-left">
                  <p className={`text-sm font-semibold leading-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>{user?.name}</p>
                  <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{user?.role}</p>
                </div>
              </button>

              {profileOpen && (
                <div className={`absolute right-0 top-12 w-56 rounded-xl border shadow-xl z-40 ${isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}`}>
                  <div className={`border-b px-3 py-2 ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                    <p className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{user?.name}</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{user?.email}</p>
                  </div>
                  <div className="p-2 space-y-1">
                    {[
                      { label: 'Profile', action: () => { setActivePage('Users'); setProfileOpen(false); } },
                      { label: 'Settings', action: () => { setActivePage('Settings'); setProfileOpen(false); } },
                      { label: 'Help', action: () => { handleQuickAction('help'); setProfileOpen(false); } },
                      { label: 'Logout', danger: true, action: () => { setProfileOpen(false); handleSignOut(); } },
                    ].map(item => (
                      <button
                        key={item.label}
                        onClick={item.action}
                        className={`w-full flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors ${item.danger ? (isDark ? 'text-red-400 hover:bg-red-500/10' : 'text-red-600 hover:bg-red-50') : (isDark ? 'text-gray-200 hover:bg-gray-800' : 'text-gray-700 hover:bg-gray-100')}`}
                      >
                        <span>{item.label}</span>
                        <span className={item.danger ? 'text-base' : 'text-xs'}>{item.label === 'Help' ? '?' : item.label === 'Settings' ? '⚙' : item.label === 'Profile' ? '👤' : '→'}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 overflow-y-auto">

          {activePage !== 'Dashboard' ? (
            renderPage()
          ) : (
            /* ── Dashboard Home ─────────────────────────────────── */
            <div className="space-y-6">

              {/* Stat cards */}
              <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
                {STATS.map(s => (
                  <div key={s.label} className={`relative overflow-hidden p-5 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
                    <p className={`text-xs font-semibold tracking-wider ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{s.label}</p>
                    <p className={`text-4xl font-bold mt-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>{s.value}</p>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-xs text-green-500 font-semibold">{s.change} <span className={`font-normal ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>from last week</span></span>
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isDark ? 'bg-gray-800' : s.iconBg}`}>
                        <s.icon className={`w-5 h-5 ${s.iconColor}`} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Main two-column */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

                {/* Recent Tickets table */}
                <div className={`xl:col-span-2 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
                  <div className={`flex items-start justify-between px-5 pt-5 pb-4 border-b ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
                    <div>
                      <h2 className={`text-base font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>Recent Tickets</h2>
                      <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Overview of the latest cases reported</p>
                    </div>
                    <button
                      onClick={() => setActivePage('My Tickets')}
                      className="text-sm text-blue-600 font-semibold flex items-center gap-1 hover:text-blue-700 shrink-0"
                    >
                      View All <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Table header */}
                  <div className={`grid grid-cols-12 px-5 py-2.5 text-xs font-semibold uppercase tracking-wide ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    <span className="col-span-6">Subject</span>
                    <span className="col-span-2">Category</span>
                    <span className="col-span-2">Priority</span>
                    <span className="col-span-2">Status</span>
                  </div>

                  {/* Rows */}
                  <div className={`divide-y ${isDark ? 'divide-gray-800' : 'divide-gray-100'}`}>
                    {TICKETS.map(t => (
                      <div key={t.id} className={`grid grid-cols-12 items-center px-5 py-3.5 cursor-pointer transition-colors ${isDark ? 'hover:bg-gray-800/60' : 'hover:bg-gray-50'}`}>
                        <span className={`col-span-6 text-sm font-medium truncate pr-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>{t.id}: {t.subject}</span>
                        <span className={`col-span-2 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{t.category}</span>
                        <span className="col-span-2">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${isDark ? darkPriorityStyle[t.priority] : priorityStyle[t.priority]}`}>{t.priority}</span>
                        </span>
                        <span className="col-span-2">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${isDark ? darkStatusStyle[t.status] : statusStyle[t.status]}`}>{t.status}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Assistant panel */}
                <div className={`rounded-2xl border flex flex-col ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`} style={{ minHeight: 440 }}>
                  {/* Header */}
                  <div className={`flex items-center gap-3 px-4 pt-4 pb-3 border-b ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>AI Assistant</p>
                        <span className="text-[10px] font-bold bg-blue-600 text-white px-1.5 py-0.5 rounded-full">BETA</span>
                      </div>
                      <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Powered by AITicketPilot AI Agent</p>
                    </div>
                  </div>

                  {/* Chat */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {aiChat.map((m, i) => (
                      <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[88%] px-3.5 py-2.5 text-sm rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white rounded-br-sm' : isDark ? 'bg-gray-800 text-gray-200 rounded-bl-sm' : 'bg-gray-100 text-gray-800 rounded-bl-sm'}`}>
                          {m.text}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Quick actions */}
                  <div className={`px-4 pb-3 border-b ${isDark ? 'border-gray-800' : 'border-gray-100'}`}>
                    <div className="flex flex-wrap gap-2">
                      {AI_QUICK_ACTIONS.slice(0, 2).map(a => (
                        <button key={a} onClick={() => sendAi(a)} className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border transition-colors ${isDark ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                          <Zap className="w-3 h-3 text-amber-500" /> {a}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Input */}
                  <div className="p-3">
                    <div className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
                      <input
                        value={aiInput}
                        onChange={e => setAiInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendAi()}
                        placeholder="Ask AI anything..."
                        className={`flex-1 bg-transparent outline-none text-sm ${isDark ? 'text-white placeholder-gray-600' : 'text-gray-900 placeholder-gray-400'}`}
                      />
                      <button onClick={() => sendAi()} className="w-8 h-8 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center justify-center transition-colors shrink-0">
                        <Send className="w-3.5 h-3.5 text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Ticket Overview + Tickets by Priority */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className={`xl:col-span-2 p-5 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
                  <h3 className={`text-base font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>Ticket Overview <span className={`text-xs font-normal ml-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Weekly Volume</span></h3>
                  <div className="flex items-end gap-3 h-28">
                    {[55, 38, 70, 48, 90, 62, 44].map((h, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1">
                        <div className="w-full bg-blue-500 rounded-t-lg transition-all" style={{ height: `${h}%` }} />
                        <span className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>{['M','T','W','T','F','S','S'][i]}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className={`p-5 rounded-2xl border ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
                  <h3 className={`text-base font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>Tickets by Priority</h3>
                  <div className="space-y-3">
                    {[['High', 38, 'bg-red-500'], ['Medium', 44, 'bg-amber-400'], ['Low', 18, 'bg-green-500']].map(([label, pct, color]) => (
                      <div key={label as string}>
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className={isDark ? 'text-gray-300' : 'text-gray-700'}>{label}</span>
                          <span className={isDark ? 'text-gray-500' : 'text-gray-400'}>{pct}%</span>
                        </div>
                        <div className={`h-2 rounded-full ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                          <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          )}
        </main>
      </div>

      {/* Floating chat button */}
      <button
        onClick={() => setActivePage('AI Assistant')}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-xl flex items-center justify-center transition-all z-50"
      >
        <MessageSquare className="w-6 h-6" />
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-[10px] font-bold flex items-center justify-center">3</span>
      </button>
    </div>
  );
}
