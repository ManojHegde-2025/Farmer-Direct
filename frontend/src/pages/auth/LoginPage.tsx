import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';
import { Sprout, LogIn, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Quick helper accounts for demo testing
  const fillDemoAccount = (demoEmail: string, demoPw: string) => {
    setEmail(demoEmail);
    setPassword(demoPw);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.post('/auth/login', { email, password });
      await login(res.data.access_token);

      // Check current user role to redirect appropriately
      const meRes = await api.get('/auth/me');
      const role = meRes.data.role;

      if (role === 'FARMER') {
        navigate('/farmer/dashboard');
      } else if (role === 'BUYER') {
        navigate('/buyer/dashboard');
      } else if (role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/marketplace');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center space-x-2 text-slate-900 font-bold text-2xl">
          <div className="bg-emerald-600 p-2 rounded-xl text-white">
            <Sprout className="w-6 h-6" />
          </div>
          <span>FarmerDirect</span>
        </Link>
        <h2 className="mt-4 text-2xl font-bold tracking-tight text-slate-900">Sign in to your account</h2>
        <p className="mt-1 text-xs text-slate-500">
          Udupi and Dakshina Kannada Direct Agricultural Portal
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm border border-slate-200 sm:rounded-2xl sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center space-x-2 py-3 px-4 border border-transparent rounded-xl text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 shadow-sm transition disabled:opacity-50"
            >
              <LogIn className="w-4 h-4" />
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            </button>
          </form>

          {/* Quick Seed Demo Logins */}
          <div className="mt-6 pt-6 border-t border-slate-200">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Demo Quick-Fill Accounts:
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => fillDemoAccount('mahabaleshwara.bhat@agri.in', 'Farmer@123456')}
                className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 p-2 rounded-lg border border-slate-200 font-medium transition"
              >
                🌾 Farmer (Bhat)
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount('procurement@mangalorespices.com', 'Buyer@123456')}
                className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 p-2 rounded-lg border border-slate-200 font-medium transition"
              >
                🏢 Buyer (Spices)
              </button>
              <button
                type="button"
                onClick={() => fillDemoAccount('admin@farmerdirect.kar.gov.in', 'Admin@FarmerDirect2026')}
                className="text-[11px] bg-amber-50 hover:bg-amber-100 text-amber-800 p-2 rounded-lg border border-amber-200 font-medium transition"
              >
                🛡️ Admin
              </button>
            </div>
          </div>

          <div className="mt-6 text-center text-xs text-slate-600">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-emerald-600 hover:text-emerald-500">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
