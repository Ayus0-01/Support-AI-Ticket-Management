import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { Bot, Headphones, Zap, ShieldCheck, BarChart3, Sparkles, MessageSquare, Workflow, CheckCircle2, ArrowRight, Mail, MapPin, Phone, Moon, Sun, Twitter, Github, Linkedin } from 'lucide-react';

interface LandingPageProps {
  onNavigate: (page: string) => void;
}

export default function LandingPage({ onNavigate }: LandingPageProps) {
  const { isDark, toggleTheme } = useTheme();
  const { isAuthenticated } = useAuth();

  const features = [
    { icon: Bot, title: 'AI-Powered Routing', desc: 'Tickets are automatically assigned to the right agent based on topic, urgency, and workload.' },
    { icon: Zap, title: 'Instant Auto-Responses', desc: 'AI generates context-aware replies for common questions — resolving tickets in seconds.' },
    { icon: BarChart3, title: 'Smart Analytics', desc: 'Track resolution times, agent performance, and customer satisfaction in real time.' },
    { icon: ShieldCheck, title: 'Secure & Compliant', desc: 'Enterprise-grade encryption ensures customer data stays protected at every step.' },
    { icon: Workflow, title: 'Automation Workflows', desc: 'Build custom rules that escalate, tag, and route tickets without lifting a finger.' },
    { icon: Sparkles, title: 'Sentiment Analysis', desc: 'AI detects frustrated customers and prioritizes their tickets automatically.' },
  ];

  const templates = [
    {
      img: '/images/dashboard.png',
      title: 'Customer Support Dashboard',
      desc: 'A clean inbox view to triage, assign, and resolve customer tickets efficiently.',
      tag: 'Support',
    },
    {
      img: '/images/communicate.png',
      title: 'AI Agent Workspace',
      desc: 'Collaborate with your AI assistant to draft replies and summarize conversations.',
      tag: 'AI Assistant',
    },
    {
      img: '/images/client.png',
      title: 'Analytics & Insights',
      desc: 'Visualize support performance with live metrics and trend reports.',
      tag: 'Analytics',
    },
  ];

  const steps = [
    { icon: MessageSquare, title: 'Connect Your Channels', desc: 'Integrate email, chat, and social inboxes into one unified workspace.' },
    { icon: Bot, title: 'Let AI Triage', desc: 'The AI agent categorizes, tags, and routes every incoming ticket automatically.' },
    { icon: CheckCircle2, title: 'Resolve Faster', desc: 'Suggested replies and automation help your team close tickets in record time.' },
  ];

  return (
    <div className={isDark ? 'bg-gray-950' : 'bg-white'}>
      {/* Hero */}
      <section className={`relative overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gradient-to-b from-blue-50 to-white'}`}>
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-cyan-400 rounded-full mix-blend-multiply filter blur-3xl"></div>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24">
          <div className="text-center max-w-3xl mx-auto">
            <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-6 ${isDark ? 'bg-gray-800 text-blue-400 border border-gray-700' : 'bg-blue-100 text-blue-700'}`}>
              <Sparkles className="w-3 h-3" /> AI-Native Ticket Management
            </div>
            <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Support tickets, <span className="text-blue-600">resolved intelligently</span>
            </h1>
            <p className={`mt-6 text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'} max-w-2xl mx-auto`}>
              AITicketPilot uses AI to route, categorize, and respond to customer tickets — so your team
              focuses on conversations that matter, not on sorting inboxes.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => onNavigate(isAuthenticated ? 'dashboard' : 'signin')}
                className="bg-blue-600 text-white font-semibold px-7 py-3.5 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
              >
                {isAuthenticated ? 'Open Dashboard' : 'Get Started Free'} <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onNavigate('dashboard')}
                className={`font-semibold px-7 py-3.5 rounded-xl border transition-colors ${isDark ? 'border-gray-700 text-gray-200 hover:bg-gray-800' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}
              >
                View Demo Dashboard
              </button>
            </div>
            <div className={`mt-10 flex items-center justify-center gap-8 text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-green-500" /> No credit card</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-green-500" /> 14-day trial</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-green-500" /> Cancel anytime</span>
            </div>
          </div>

          {/* Hero mockup */}
          <div className="mt-16 max-w-5xl mx-auto">
            <div className={`rounded-2xl border shadow-2xl overflow-hidden ${isDark ? 'border-gray-800 bg-gray-900' : 'border-gray-200 bg-white'}`}>
              <div className={`flex items-center gap-2 px-4 py-3 border-b ${isDark ? 'border-gray-800 bg-gray-900' : 'border-gray-100 bg-gray-50'}`}>
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <span className={`ml-2 text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>aiticketpilot.app/dashboard</span>
              </div>
              <div className="relative overflow-hidden">
                <img src="/images/main.png" alt="Support dashboard preview" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/30 via-transparent to-transparent" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logos / trust bar */}
      <section className={`py-10 border-y ${isDark ? 'border-gray-800 bg-gray-950' : 'border-gray-100 bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <p className={`text-center text-xs uppercase tracking-wider font-semibold ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Trusted by modern support teams</p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-12 gap-y-4">
            {['Nimbus', 'Quanta', 'Vertex', 'Lumina', 'Orbit', 'Cobalt'].map(name => (
              <span key={name} className={`text-xl font-bold tracking-tight ${isDark ? 'text-gray-600' : 'text-gray-300'}`}>{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className={`py-24 ${isDark ? 'bg-gray-950' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className={`text-3xl sm:text-4xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Everything you need to scale support</h2>
            <p className={`mt-4 text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Powerful features that help your team resolve more tickets with less effort.</p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(f => (
              <div key={f.title} className={`p-6 rounded-2xl border transition-all hover:shadow-lg ${isDark ? 'bg-gray-900 border-gray-800 hover:border-gray-700' : 'bg-white border-gray-200 hover:border-blue-200'}`}>
                <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-600/20">
                  <f.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className={`mt-4 text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{f.title}</h3>
                <p className={`mt-2 text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className={`py-24 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className={`text-3xl sm:text-4xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>How it works</h2>
            <p className={`mt-4 text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Three steps from messy inbox to resolved tickets.</p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((s, i) => (
              <div key={s.title} className="relative text-center">
                <div className="relative inline-flex">
                  <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20">
                    <s.icon className="w-7 h-7 text-white" />
                  </div>
                  <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-white text-blue-600 text-xs font-bold flex items-center justify-center border border-gray-200">{i + 1}</span>
                </div>
                <h3 className={`mt-5 text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{s.title}</h3>
                <p className={`mt-2 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{s.desc}</p>
                {i < steps.length - 1 && (
                  <ArrowRight className={`hidden md:block absolute top-8 -right-4 w-6 h-6 ${isDark ? 'text-gray-700' : 'text-gray-300'}`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Templates */}
      <section id="templates" className={`py-24 ${isDark ? 'bg-gray-950' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className={`text-3xl sm:text-4xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Templates for every team</h2>
            <p className={`mt-4 text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Start from a ready-made layout tailored to your support workflow.</p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {templates.map(t => (
              <div key={t.title} className={`group rounded-2xl border overflow-hidden transition-all hover:shadow-xl ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'}`}>
                <div className="aspect-[4/3] overflow-hidden bg-gray-100">
                  <img src={t.img} alt={t.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                </div>
                <div className="p-6">
                  <span className={`inline-block text-xs font-semibold px-2.5 py-1 rounded-full ${isDark ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>{t.tag}</span>
                  <h3 className={`mt-3 text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{t.title}</h3>
                  <p className={`mt-2 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{t.desc}</p>
                  <button
                    onClick={() => onNavigate(isAuthenticated ? 'dashboard' : 'signin')}
                    className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    Use this template <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className={`py-24 ${isDark ? 'bg-gray-950' : 'bg-white'}`}>
        <div className="max-w-5xl mx-auto px-4">
          <div className={`rounded-3xl p-12 text-center relative overflow-hidden ${isDark ? 'bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-800' : 'bg-gradient-to-br from-blue-600 to-cyan-500'}`}>
            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-bold text-white">Ready to transform your support?</h2>
              <p className="mt-4 text-blue-100 max-w-xl mx-auto">Join thousands of teams using AITicketPilot to resolve tickets faster with AI.</p>
              <button
                onClick={() => {
                  const section = document.getElementById('templates');
                  if (section) {
                    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  } else {
                    onNavigate(isAuthenticated ? 'dashboard' : 'signin');
                  }
                }}
                className="mt-8 bg-white text-blue-600 font-semibold px-8 py-3.5 rounded-xl hover:bg-blue-50 transition-colors inline-flex items-center gap-2"
              >
                Contact <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`${isDark ? 'bg-gray-900 border-t border-gray-800' : 'bg-gray-50 border-t border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2">
              <img src="/images/logo.png" alt="AITicketPilot logo" className="h-9 w-9 object-contain" />
              <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>AITicketPilot</span>
            </div>
            <p className={`mt-3 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>AI-native ticket management for modern support teams.</p>
            <div className="mt-4 flex gap-3">
              {[Twitter, Github, Linkedin].map((Icon, i) => (
                <a key={i} href="#" className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDark ? 'bg-gray-800 text-gray-400 hover:text-white' : 'bg-white text-gray-500 hover:text-gray-900 border border-gray-200'}`}><Icon className="w-4 h-4" /></a>
              ))}
            </div>
          </div>
          {[
            { title: 'Product', links: ['Features', 'Templates', 'Pricing', 'Integrations'] },
            { title: 'Company', links: ['About', 'Blog', 'Careers', 'Contact'] },
            { title: 'Resources', links: ['Docs', 'Help Center', 'Community', 'Status'] },
          ].map(col => (
            <div key={col.title}>
              <h4 className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{col.title}</h4>
              <ul className="mt-3 space-y-2">
                {col.links.map(l => (
                  <li key={l}><a href="#" className={`text-sm ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>{l}</a></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className={`border-t px-4 py-6 ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>© 2026 AITicketPilot. All rights reserved.</p>
            <div className={`flex items-center gap-4 text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
              <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> lakshmipriya@gmail.com</span>
              <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> +1 (555) 014-2026</span>
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> San Francisco, CA</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
