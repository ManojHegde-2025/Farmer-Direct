import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { getListings } from '../services/api';
import { Listing } from '../types';
import {
  Sprout,
  ShoppingBag,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  MapPin,
  Scale,
  Users,
  Building2,
  BarChart3,
  HelpCircle,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { t, language } = useLanguage();
  const [featuredListings, setFeaturedListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    getListings({ limit: 4 })
      .then((res) => {
        setFeaturedListings(res.data);
      })
      .catch((err) => {
        console.error('Error loading featured listings', err);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* 1. Hero Section */}
      <section className="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800 text-white pt-16 pb-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/30 px-3.5 py-1.5 rounded-full text-emerald-400 text-xs font-medium">
            <Sprout className="w-3.5 h-3.5" />
            <span>Serving Udupi & Dakshina Kannada Coastal Districts</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            {t.hero.title}
          </h1>

          <p className="max-w-2xl mx-auto text-slate-300 text-base sm:text-lg leading-relaxed font-normal">
            {t.hero.subtitle}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/marketplace"
              className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg transition flex items-center justify-center space-x-2"
            >
              <ShoppingBag className="w-5 h-5" />
              <span>{t.hero.exploreBtn}</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/register?role=FARMER"
              className="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold px-6 py-3.5 rounded-xl transition flex items-center justify-center space-x-2"
            >
              <Sprout className="w-5 h-5 text-emerald-400" />
              <span>I am a Farmer</span>
            </Link>

            <Link
              to="/register?role=BUYER"
              className="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold px-6 py-3.5 rounded-xl transition flex items-center justify-center space-x-2"
            >
              <Building2 className="w-5 h-5 text-blue-400" />
              <span>I am a Commercial Buyer</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. Key Commodities Showcase */}
      <section className="py-12 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-xs uppercase tracking-wider font-semibold text-emerald-600">Regional Agricultural Focus</h2>
            <p className="text-2xl font-bold text-slate-900 mt-1">Core Commodities Cultivated in Coastal Karnataka</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {[
              { name: 'Arecanut', name_kn: 'ಅಡಿಕೆ', variety: 'Chali, Rashi', icon: '🌰' },
              { name: 'Coconut', name_kn: 'ತೆಂಗಿನಕಾಯಿ', variety: 'Tall, Dehusked', icon: '🥥' },
              { name: 'Red Paddy / Rice', name_kn: 'ಭತ್ತ / ಅಕ್ಕಿ', variety: 'Jaya, Jyothi', icon: '🌾' },
              { name: 'Black Pepper', name_kn: 'ಕರಿಮೆಣಸು', variety: 'Garbled Bold', icon: '🌶️' },
              { name: 'Raw Cashew', name_kn: 'ಗೋಡಂಬಿ', variety: 'Orchard Dried', icon: '🥜' },
              { name: 'Plantain Banana', name_kn: 'ಬಾಳೆಹಣ್ಣು', variety: 'Robusta, Elakki', icon: '🍌' },
            ].map((crop, idx) => (
              <div key={idx} className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 text-center hover:border-emerald-400 hover:shadow-sm transition">
                <div className="text-3xl mb-2">{crop.icon}</div>
                <div className="font-semibold text-slate-900 text-sm">{language === 'kn' ? crop.name_kn : crop.name}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">{crop.variety}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. How It Works (4-Step Workflow) */}
      <section className="py-16 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs uppercase tracking-wider font-semibold text-emerald-600">Fair & Transparent</h2>
            <p className="text-3xl font-extrabold text-slate-900 mt-1">How FarmerDirect Works</p>
            <p className="text-sm text-slate-600 mt-2">
              From harvest to settlement: direct communication without unnecessary middlemen.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Register & Verify',
                desc: 'Farmers submit land & crop details; buyers submit business verification for admin review.',
                icon: ShieldCheck,
              },
              {
                step: '02',
                title: 'List or Post Need',
                desc: 'Growers list verified stock with asking rates; buyers post procurement specs and volume.',
                icon: Sprout,
              },
              {
                step: '03',
                title: 'Match & Negotiate',
                desc: 'Deterministic rules match compatible parties. Exchange transparent offers and counteroffers.',
                icon: Scale,
              },
              {
                step: '04',
                title: 'Order & Settle',
                desc: 'Accepted offer atomically reserves inventory. Coordinate pickup/transport and verify payment.',
                icon: CheckCircle2,
              },
            ].map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 relative shadow-sm">
                  <div className="text-3xl font-black text-slate-200 absolute top-4 right-4">{step.step}</div>
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-slate-900 text-base mb-2">{step.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. Marketplace Preview with DEMO DATA banner */}
      <section className="py-16 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
            <div>
              <div className="inline-flex items-center space-x-1.5 bg-amber-50 text-amber-800 text-[11px] font-semibold px-2 py-0.5 rounded border border-amber-200 mb-2">
                <span>Demonstration Dataset</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Live Marketplace Preview</h2>
              <p className="text-xs text-slate-500 mt-1">Recent active lots from farmers in Udupi & DK</p>
            </div>
            <Link
              to="/marketplace"
              className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center space-x-1"
            >
              <span>Explore All Listings</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-400 text-sm">Loading produce lots...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredListings.map((l) => (
                <div key={l.id} className="bg-slate-50 border border-slate-200 rounded-2xl p-5 hover:border-emerald-400 hover:shadow-md transition flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                      <span className="font-medium text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded">
                        {l.commodity_name}
                      </span>
                      <span className="flex items-center space-x-1 text-slate-500">
                        <MapPin className="w-3 h-3" />
                        <span>{l.farmer?.district === 'DAKSHINA_KANNADA' ? 'DK' : 'Udupi'}</span>
                      </span>
                    </div>

                    <h3 className="font-bold text-slate-900 text-sm line-clamp-2 mb-2">{l.title}</h3>

                    <div className="text-xs text-slate-600 space-y-1 mb-4">
                      <div>Variety: <span className="font-medium text-slate-800">{l.variety || 'Standard'}</span></div>
                      <div>Available: <span className="font-medium text-slate-800">{l.available_quantity} {l.unit}</span></div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-200 flex items-center justify-between">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Asking Price</div>
                      <div className="text-lg font-bold text-slate-900">₹{l.price_per_unit}<span className="text-xs font-normal text-slate-500">/{l.unit}</span></div>
                    </div>
                    <Link
                      to={`/marketplace/${l.id}`}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-3 py-1.5 rounded-lg shadow-sm transition"
                    >
                      View
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* 5. Benefits Comparison (Farmers vs Buyers) */}
      <section className="py-16 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs uppercase tracking-wider font-semibold text-emerald-600">Mutual Value Creation</h2>
            <p className="text-3xl font-extrabold text-slate-900 mt-1">Built for Real Agricultural Participants</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Farmer Column */}
            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-emerald-100 text-emerald-700 rounded-xl flex items-center justify-center">
                  <Sprout className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900">For Coastal Farmers</h3>
                  <p className="text-xs text-slate-500">Smallholders, family growers, and plantation owners</p>
                </div>
              </div>
              <ul className="space-y-3.5 text-sm text-slate-700">
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span><strong>Set Asking Prices:</strong> Establish your own rates rather than accepting distress mandi quotes.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span><strong>Direct Negotiation:</strong> Counteroffer with wholesalers and millers transparently.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span><strong>Net Proceeds Breakdown:</strong> Calculate estimated proceeds minus actual agreed handling or logistics fees.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span><strong>Regional Reach:</strong> Connect with commercial buyers in Mangaluru, Kundapura, Udupi, and Puttur.</span>
                </li>
              </ul>
              <div className="mt-8 pt-6 border-t border-slate-100">
                <Link
                  to="/register?role=FARMER"
                  className="block text-center bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 rounded-xl transition text-sm"
                >
                  Register as Farmer
                </Link>
              </div>
            </div>

            {/* Buyer Column */}
            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-blue-100 text-blue-700 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900">For Commercial Buyers</h3>
                  <p className="text-xs text-slate-500">Wholesalers, processors, oil millers, and retailers</p>
                </div>
              </div>
              <ul className="space-y-3.5 text-sm text-slate-700">
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                  <span><strong>Post Procurement Needs:</strong> Publish volume requirements with target delivery dates and budgets.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                  <span><strong>Deterministic Matching:</strong> Receive explainable compatibility recommendations across variety, location, and volume.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                  <span><strong>Traceable Source:</strong> Direct provenance and verified grower profiles for quality assurance.</span>
                </li>
                <li className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                  <span><strong>Guaranteed Stock Reservation:</strong> Accepted agreements lock inventory atomically without overselling.</span>
                </li>
              </ul>
              <div className="mt-8 pt-6 border-t border-slate-100">
                <Link
                  to="/register?role=BUYER"
                  className="block text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 rounded-xl transition text-sm"
                >
                  Register as Buyer
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Transparency & Disclaimers Section */}
      <section className="py-14 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-4">
          <div className="w-12 h-12 bg-slate-100 text-slate-700 rounded-full flex items-center justify-center mx-auto">
            <Scale className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Price Transparency & Objective Principles</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            FarmerDirect does not artificially fix commodity rates or claim guaranteed profits. Instead, we publish dated APMC benchmarks (clearly labeled DEMO_DATA for testing), preserve negotiation history, and provide an explainable matching algorithm to foster mutual trust in Udupi and Dakshina Kannada.
          </p>
        </div>
      </section>
    </div>
  );
};
