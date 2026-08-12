import { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';

interface SignUpPageProps {
  onNavigate: (page: string) => void;
}

export default function SignUpPage({ onNavigate }: SignUpPageProps) {
  const { isDark } = useTheme();
  const { register, isAuthenticated } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  const [role, setRole] = useState<'User'|'Agent'|'Admin'>('User');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError('');
  if (!name || !email || !password || !confirmPassword) {
    setError('Please fill all required fields');
    return;
  }
  if (password !== confirmPassword) {
    setError('Passwords do not match');
    return;
  }
  setLoading(true);
  const res = await register(
    name,
    email,
    password,
    mobile,
    role
  );
  setLoading(false);
  if (res.success) {
    onNavigate('dashboard:My Tickets');
  } else {
    setError(res.message || 'Registration failed. Please try again.');
  }
};

  return (
  <div className={`min-h-screen flex ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
    <div className="w-full max-w-md mx-auto p-6">

      <h1
        className={`text-2xl font-bold ${
          isDark ? 'text-white' : 'text-gray-900'
        }`}
      >
        Create your account
      </h1>

      <p
        className={`mt-1 text-sm ${
          isDark ? 'text-gray-400' : 'text-gray-600'
        }`}
      >
        Enter your details to create your account.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">

        {/* Username */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Username
          </label>

          <input
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full rounded-xl border px-3 py-2"
            placeholder="Enter your username"
          />
        </div>

        {/* Email */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Email
          </label>

          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full rounded-xl border px-3 py-2"
            placeholder="Enter your email"
          />
        </div>

        {/* Mobile - Optional */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Mobile number{' '}
            <span className="text-gray-400">(optional)</span>
          </label>

          <input
            value={mobile}
            onChange={e => setMobile(e.target.value)}
            className="w-full rounded-xl border px-3 py-2"
            placeholder="Enter your mobile number"
          />
        </div>

        {/* Role */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Account type
          </label>

          <select
            value={role}
            onChange={e =>
              setRole(e.target.value as 'User' | 'Agent' | 'Admin')
            }
            className="w-full rounded-xl border px-3 py-2"
          >
            <option value="User">User</option>
            <option value="Agent">Agent</option>
            <option value="Admin">Admin</option>
          </select>
        </div>

        {/* Password */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Password
          </label>

          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full rounded-xl border px-3 py-2"
            placeholder="Create a password"
          />
        </div>

        {/* Confirm Password */}
        <div>
          <label
            className={`block text-sm font-medium mb-1.5 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Confirm password
          </label>

          <input
            type="password"
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            className="w-full rounded-xl border px-3 py-2"
            placeholder="Confirm your password"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex items-center justify-between gap-3">

          <button
            type="button"
            onClick={() => onNavigate('signin')}
            className="px-4 py-2 rounded-xl border"
          >
            Back
          </button>

          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-blue-600 text-white"
          >
            {loading ? 'Creating...' : 'Create account'}
          </button>

        </div>

      </form>

    </div>
  </div>
);
}
