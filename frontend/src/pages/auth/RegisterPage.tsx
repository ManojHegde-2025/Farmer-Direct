import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { Sprout, Building2, UserPlus, AlertCircle, CheckCircle2 } from 'lucide-react';
import { UserRole } from '../../types';

export const RegisterPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialRole = (searchParams.get('role') as UserRole) || 'FARMER';

  const navigate = useNavigate();
  const { login } = useAuth();

  const [role, setRole] = useState<'FARMER' | 'BUYER'>(initialRole === 'BUYER' ? 'BUYER' : 'FARMER');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      // 1. Register User
      await api.post('/auth/register', {
        email,
        full_name: fullName,
        phone: phone || null,
        password,
        role,
      });

      // 2. Auto-login upon registration
      const loginRes = await api.post('/auth/login', { email, password });
      await login(loginRes.data.access_token);

      if (role === 'FARMER') {
        navigate('/farmer/dashboard');
      } else {
        navigate('/buyer/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please check your information.');
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
          <span>Rajya Krishi Banda</span>
        </Link>
        <h2 className="mt-4 text-2xl font-bold tracking-tight text-slate-900">Create an Account</h2>
        <p className="mt-1 text-xs text-slate-500">
          Join the agricultural marketplace for Udupi & Dakshina Kannada
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

          {/* Role Selection Tabs */}
          <div className="mb-6">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Select Account Role</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setRole('FARMER')}
                className={`flex flex-col items-center p-3 rounded-xl border text-center transition ${
                  role === 'FARMER'
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-900 font-semibold shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 text-slate-600 bg-slate-50'
                }`}
              >
                <Sprout className={`w-5 h-5 mb-1 ${role === 'FARMER' ? 'text-emerald-600' : 'text-slate-400'}`} />
                <span className="text-xs">Farmer / Grower</span>
              </button>

              <button
                type="button"
                onClick={() => setRole('BUYER')}
                className={`flex flex-col items-center p-3 rounded-xl border text-center transition ${
                  role === 'BUYER'
                    ? 'border-blue-600 bg-blue-50 text-blue-900 font-semibold shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 text-slate-600 bg-slate-50'
                }`}
              >
                <Building2 className={`w-5 h-5 mb-1 ${role === 'BUYER' ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className="text-xs">Commercial Buyer</span>
              </button>
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">Full Name / Business Contact</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={role === 'FARMER' ? 'e.g. Mahabaleshwara Bhat' : 'e.g. Anand Prabhu'}
                className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

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
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">Phone Number (Optional)</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+919845012345"
                className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">Password (Min. 8 characters)</label>
              <input
                type="password"
                required
                minLength={8}
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
              <UserPlus className="w-4 h-4" />
              <span>{loading ? 'Creating Account...' : `Register as ${role === 'FARMER' ? 'Farmer' : 'Buyer'}`}</span>
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-600">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-emerald-600 hover:text-emerald-500">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
