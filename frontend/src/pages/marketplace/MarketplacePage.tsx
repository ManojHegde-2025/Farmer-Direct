import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getListings, getCommodities } from '../../services/api';
import { Listing, Commodity } from '../../types';
import { useLanguage } from '../../contexts/LanguageContext';
import {
  Search,
  Filter,
  MapPin,
  ShieldCheck,
  Tag,
  Truck,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

export const MarketplacePage: React.FC = () => {
  const { t, language } = useLanguage();

  const [listings, setListings] = useState<Listing[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [search, setSearch] = useState('');
  const [selectedCommodity, setSelectedCommodity] = useState<string>('');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('');
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [minQuantity, setMinQuantity] = useState<string>('');

  const fetchFilteredListings = () => {
    setLoading(true);
    const params: any = {};
    if (search) params.q = search;
    if (selectedCommodity) params.commodity_id = selectedCommodity;
    if (selectedDistrict) params.district = selectedDistrict;
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    if (minQuantity) params.min_quantity = minQuantity;

    getListings(params)
      .then((res) => setListings(res.data))
      .catch((err) => console.error('Failed to load listings', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    getCommodities()
      .then((res) => setCommodities(res.data))
      .catch((err) => console.error(err));
    fetchFilteredListings();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFilteredListings();
  };

  const handleResetFilters = () => {
    setSearch('');
    setSelectedCommodity('');
    setSelectedDistrict('');
    setMinPrice('');
    setMaxPrice('');
    setMinQuantity('');
    getListings()
      .then((res) => setListings(res.data))
      .finally(() => setLoading(false));
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Title & Subtitle */}
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {t.marketplace.title}
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            {t.marketplace.subtitle}
          </p>
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t.marketplace.searchPlaceholder}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
              />
            </div>
            <button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl font-medium text-sm transition shadow-sm"
            >
              Search Produce
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2.5 rounded-xl text-sm font-medium transition flex items-center justify-center space-x-1"
              title="Reset Filters"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </form>

          {/* Filter Dropdowns */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-100">
            {/* Commodity */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Commodity
              </label>
              <select
                value={selectedCommodity}
                onChange={(e) => {
                  setSelectedCommodity(e.target.value);
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="">{t.marketplace.allCommodities}</option>
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>
                    {language === 'kn' && c.name_kn ? c.name_kn : c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* District */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                District
              </label>
              <select
                value={selectedDistrict}
                onChange={(e) => {
                  setSelectedDistrict(e.target.value);
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="">{t.marketplace.allDistricts}</option>
                <option value="UDUPI">Udupi (ಉಡುಪಿ)</option>
                <option value="DAKSHINA_KANNADA">Dakshina Kannada (ದಕ್ಷಿಣ ಕನ್ನಡ)</option>
              </select>
            </div>

            {/* Price Max */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Max Price (₹)
              </label>
              <input
                type="number"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                placeholder="e.g. 500"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            {/* Apply button */}
            <div className="flex items-end">
              <button
                type="button"
                onClick={fetchFilteredListings}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 py-1.5 px-3 rounded-lg text-xs font-semibold transition"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>

        {/* Listings Grid */}
        {loading ? (
          <div className="text-center py-20 text-slate-400 text-sm">Loading verified lots...</div>
        ) : listings.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-slate-200 p-8">
            <Tag className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="font-bold text-slate-800 text-base">{t.marketplace.noListings}</h3>
            <p className="text-xs text-slate-500 mt-1">Try widening your filters or search terms.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((l) => (
              <div
                key={l.id}
                className="bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-emerald-400 hover:shadow-md transition flex flex-col justify-between"
              >
                <div className="p-5 space-y-3">
                  {/* Badge & District */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200/60 px-2.5 py-0.5 rounded-full">
                      {language === 'kn' && l.commodity_name_kn ? l.commodity_name_kn : l.commodity_name}
                    </span>
                    <div className="flex items-center space-x-1 text-xs text-slate-500">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{l.farmer?.district === 'DAKSHINA_KANNADA' ? 'Dakshina Kannada' : 'Udupi'}</span>
                    </div>
                  </div>

                  {/* Title & Variety */}
                  <div>
                    <h3 className="font-bold text-slate-900 text-base leading-snug line-clamp-2">
                      {l.title}
                    </h3>
                    <div className="text-xs text-slate-500 mt-1 flex items-center space-x-2">
                      <span>Variety: <strong className="text-slate-700">{l.variety || 'Standard'}</strong></span>
                      <span>•</span>
                      <span>Grade: <strong className="text-slate-700">{l.quality_grade}</strong></span>
                    </div>
                  </div>

                  {/* Grower verification */}
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-1.5">
                      {l.farmer?.is_verified ? (
                        <span className="flex items-center space-x-1 text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded text-[11px]">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Verified Grower</span>
                        </span>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Pending Verification</span>
                      )}
                    </div>
                    <span className="text-slate-500 text-[11px]">
                      {l.farmer?.full_name || 'Grower'}
                    </span>
                  </div>

                  {/* Logistics preference */}
                  <div className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                    <Truck className="w-3.5 h-3.5 text-slate-400" />
                    <span>{l.delivery_available ? 'Delivery Available (Radius agreed)' : 'Farmer Depot Pickup'}</span>
                  </div>
                </div>

                {/* Pricing & CTA footer */}
                <div className="bg-slate-50 border-t border-slate-100 px-5 py-3.5 flex items-center justify-between">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
                      Asking Rate
                    </div>
                    <div className="text-xl font-bold text-slate-900">
                      ₹{l.price_per_unit}
                      <span className="text-xs font-normal text-slate-500">/{l.unit}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Stock: <strong className="text-slate-700">{l.available_quantity} {l.unit}</strong>
                    </div>
                  </div>

                  <Link
                    to={`/marketplace/${l.id}`}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs px-4 py-2 rounded-xl shadow-sm transition"
                  >
                    View & Offer
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
