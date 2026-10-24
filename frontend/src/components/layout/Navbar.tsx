import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Sprout, ShoppingBag, ShieldCheck, UserCheck, LogOut, LogIn, Globe, LayoutDashboard, MessageSquare } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const navigate = useNavigate();

  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-emerald-600 group-hover:bg-emerald-500 transition-colors p-2 rounded-xl text-white shadow-sm flex items-center justify-center">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-xl tracking-tight text-white">FarmerDirect</span>
                <span className="bg-emerald-500/20 text-emerald-400 text-[10px] font-semibold px-1.5 py-0.5 rounded border border-emerald-500/30">
                  Udupi & DK
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal">Direct Agricultural Marketplace</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              to="/marketplace"
              className="text-slate-300 hover:text-white transition-colors text-sm font-medium flex items-center space-x-1.5"
            >
              <ShoppingBag className="w-4 h-4 text-emerald-400" />
              <span>{t.nav.marketplace}</span>
            </Link>

            {user?.role === 'FARMER' && (
              <Link
                to="/farmer/dashboard"
                className="text-slate-300 hover:text-white transition-colors text-sm font-medium flex items-center space-x-1.5"
              >
                <Sprout className="w-4 h-4 text-emerald-400" />
                <span>{t.nav.farmerDashboard}</span>
              </Link>
            )}

            {user?.role === 'BUYER' && (
              <Link
                to="/buyer/dashboard"
                className="text-slate-300 hover:text-white transition-colors text-sm font-medium flex items-center space-x-1.5"
              >
                <LayoutDashboard className="w-4 h-4 text-emerald-400" />
                <span>{t.nav.buyerDashboard}</span>
              </Link>
            )}

            {(user?.role === 'FARMER' || user?.role === 'BUYER') && (
              <Link
                to="/messages"
                className="text-slate-300 hover:text-white transition-colors text-sm font-medium flex items-center space-x-1.5"
              >
                <MessageSquare className="w-4 h-4 text-emerald-400" />
                <span>{(t.nav as any).messages || 'Messages'}</span>
              </Link>
            )}

            {user?.role === 'ADMIN' && (
              <Link
                to="/admin/dashboard"
                className="text-amber-400 hover:text-amber-300 transition-colors text-sm font-medium flex items-center space-x-1.5 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>{t.nav.adminDashboard}</span>
              </Link>
            )}
          </div>

          {/* Right Section: Language & Auth */}
          <div className="flex items-center space-x-4">
            {/* Language Toggle */}
            <button
              onClick={() => setLanguage(language === 'en' ? 'kn' : 'en')}
              className="flex items-center space-x-1 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
              title="Toggle Language (English / ಕನ್ನಡ)"
            >
              <Globe className="w-3.5 h-3.5 text-emerald-400" />
              <span>{language === 'en' ? 'ಕನ್ನಡ' : 'English'}</span>
            </button>

            {user ? (
              <div className="flex items-center space-x-3">
                <div className="hidden sm:block text-right">
                  <div className="text-xs font-semibold text-white">{user.full_name}</div>
                  <div className="text-[10px] text-emerald-400 uppercase tracking-wider font-medium">{user.role}</div>
                </div>

                <button
                  onClick={logout}
                  className="bg-slate-800 hover:bg-red-950/40 hover:text-red-400 text-slate-300 p-2 rounded-lg border border-slate-700 transition flex items-center text-xs"
                  title={t.nav.logout}
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="text-slate-300 hover:text-white px-3 py-1.5 text-sm font-medium transition"
                >
                  {t.nav.login}
                </Link>
                <Link
                  to="/register"
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-lg text-sm font-medium shadow-sm transition"
                >
                  {t.nav.register}
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
