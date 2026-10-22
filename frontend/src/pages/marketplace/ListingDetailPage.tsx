import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getListingById, getCommodityReferencePrice, createOffer } from '../../services/api';
import { Listing, ReferencePrice } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import {
  Sprout,
  MapPin,
  ShieldCheck,
  Truck,
  Calendar,
  Scale,
  Send,
  AlertCircle,
  CheckCircle2,
  Info,
  ArrowLeft,
} from 'lucide-react';

export const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [listing, setListing] = useState<Listing | null>(null);
  const [refPriceData, setRefPriceData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Offer form state
  const [offerQty, setOfferQty] = useState('');
  const [offerPrice, setOfferPrice] = useState('');
  const [deliveryMethod, setDeliveryMethod] = useState('BUYER_PICKUP');
  const [offerMsg, setOfferMsg] = useState('');
  const [offerError, setOfferError] = useState<string | null>(null);
  const [offerSuccess, setOfferSuccess] = useState<string | null>(null);
  const [submittingOffer, setSubmittingOffer] = useState(false);

  useEffect(() => {
    if (!id) return;
    getListingById(Number(id))
      .then((res) => {
        setListing(res.data);
        if (res.data.commodity_id) {
          getCommodityReferencePrice(res.data.commodity_id)
            .then((rpRes) => setRefPriceData(rpRes.data))
            .catch((err) => console.error(err));
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  const handleMakeOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    setOfferError(null);
    setOfferSuccess(null);

    if (!user) {
      navigate('/login');
      return;
    }

    if (user.role !== 'BUYER' && user.role !== 'ADMIN') {
      setOfferError('Only registered buyers can submit purchase offers on listings.');
      return;
    }

    const qty = parseFloat(offerQty);
    const price = parseFloat(offerPrice);

    if (!qty || qty <= 0) {
      setOfferError('Quantity must be greater than zero');
      return;
    }

    if (listing && qty > listing.available_quantity) {
      setOfferError(`Offer quantity cannot exceed available stock (${listing.available_quantity} ${listing.unit})`);
      return;
    }

    if (!price || price <= 0) {
      setOfferError('Price per unit must be greater than zero');
      return;
    }

    setSubmittingOffer(true);

    try {
      await createOffer({
        listing_id: listing!.id,
        quantity: qty,
        price_per_unit: price,
        delivery_method: deliveryMethod,
        message: offerMsg || undefined,
      });

      setOfferSuccess('Your offer has been submitted directly to the farmer! You can track negotiations in your Buyer Portal.');
      setOfferQty('');
      setOfferPrice('');
      setOfferMsg('');
    } catch (err: any) {
      setOfferError(err.response?.data?.detail || 'Failed to submit offer.');
    } finally {
      setSubmittingOffer(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading lot specifications...</div>;
  }

  if (!listing) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4">
        <p className="text-slate-600">Produce listing not found.</p>
        <Link to="/marketplace" className="text-emerald-600 hover:underline">Back to Marketplace</Link>
      </div>
    );
  }

  const calculatedTotal = parseFloat(offerQty || '0') * parseFloat(offerPrice || '0');

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Back Link */}
        <Link to="/marketplace" className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Marketplace</span>
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Lot Details (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-6 shadow-sm">
              {/* Header Badges */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full uppercase tracking-wider">
                  {listing.commodity?.name || 'Produce'}
                </span>
                <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                  Status: <strong className="text-slate-800">{listing.status}</strong>
                </span>
              </div>

              {/* Title & Asking Price */}
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 leading-tight">
                  {listing.title}
                </h1>
                <div className="mt-3 flex items-baseline space-x-2">
                  <span className="text-3xl font-extrabold text-slate-900">₹{listing.price_per_unit}</span>
                  <span className="text-sm font-medium text-slate-500">per {listing.unit} (Asking Rate)</span>
                </div>
              </div>

              {/* Description */}
              {listing.description && (
                <div className="text-sm text-slate-700 leading-relaxed border-t border-slate-100 pt-4">
                  {listing.description}
                </div>
              )}

              {/* Specifications Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 border-t border-slate-100 pt-6">
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Available Stock</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">{listing.available_quantity} {listing.unit}</div>
                  <div className="text-[10px] text-slate-400">Total Lot: {listing.quantity} {listing.unit}</div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Variety</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">{listing.variety || 'Standard'}</div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Quality Grade</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">Grade {listing.quality_grade}</div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Min. Order Qty</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">
                    {listing.min_order_quantity ? `${listing.min_order_quantity} ${listing.unit}` : 'None'}
                  </div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Harvest Date</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">{listing.harvest_date || 'Recent'}</div>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Available Until</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">{listing.available_until || 'While in stock'}</div>
                </div>
              </div>

              {/* Farmer Profile & Provenance (Safe fields) */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-200/80 space-y-3">
                <h3 className="text-xs uppercase font-bold text-slate-500 tracking-wider">Cultivator & Provenance</h3>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <div className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                      <span>{listing.farmer?.full_name}</span>
                      {listing.farmer?.is_verified && (
                        <span className="flex items-center text-emerald-600 text-xs font-medium">
                          <ShieldCheck className="w-4 h-4 ml-1" />
                          <span className="ml-0.5">Verified Farmer</span>
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 flex items-center space-x-1 mt-0.5">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>
                        {listing.farmer?.taluk ? `${listing.farmer.taluk}, ` : ''}
                        {listing.farmer?.district === 'DAKSHINA_KANNADA' ? 'Dakshina Kannada' : 'Udupi District'}
                      </span>
                    </div>
                  </div>
                  {listing.farmer?.farm_name && (
                    <div className="text-xs text-slate-600 bg-white px-3 py-1.5 rounded-lg border border-slate-200">
                      Estate: <strong>{listing.farmer.farm_name}</strong>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* PHASE 9: Market Reference Price Benchmark */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-sm">
              <div className="flex items-center space-x-2 text-slate-900 font-bold text-base">
                <Scale className="w-5 h-5 text-blue-600" />
                <span>Indicative Mandi Benchmark (Reference Price)</span>
              </div>

              {refPriceData && refPriceData.available ? (
                <div className="bg-blue-50/60 border border-blue-200/80 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-[11px] text-blue-700 font-semibold uppercase tracking-wider">
                        Regional APMC Benchmark
                      </div>
                      <div className="text-2xl font-bold text-slate-900">
                        ₹{refPriceData.latest_price}
                        <span className="text-xs font-normal text-slate-500">/{refPriceData.unit}</span>
                      </div>
                    </div>
                    <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2.5 py-1 rounded-full border border-amber-300">
                      {refPriceData.classification}
                    </span>
                  </div>

                  <div className="text-xs text-slate-600 space-y-1 pt-1 border-t border-blue-200/60">
                    <div>Mandi / Market: <strong className="text-slate-800">{refPriceData.market}</strong></div>
                    <div>Observation Date: <strong className="text-slate-800">{refPriceData.observation_date}</strong></div>
                    <div>Source: <span className="text-slate-700">{refPriceData.source}</span></div>
                  </div>

                  <div className="text-[11px] text-slate-500 italic pt-1">
                    Reference prices are clearly classified historical demonstrations for comparison and do not guarantee actual realized settlement prices.
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-500 bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center space-x-2">
                  <Info className="w-4 h-4 text-slate-400 shrink-0" />
                  <span>No external APMC reference price record is currently published for this commodity.</span>
                </div>
              )}
            </div>
          </div>

          {/* Offer & Negotiation Box (Right col) */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-5 shadow-sm sticky top-24">
              <div>
                <h2 className="font-extrabold text-slate-900 text-lg">Direct Contract Offer</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Propose your target price and volume directly to the cultivator.
                </p>
              </div>

              {offerSuccess && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl p-3 flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{offerSuccess}</span>
                </div>
              )}

              {offerError && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{offerError}</span>
                </div>
              )}

              <form onSubmit={handleMakeOffer} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Quantity ({listing.unit})
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    max={listing.available_quantity}
                    value={offerQty}
                    onChange={(e) => setOfferQty(e.target.value)}
                    placeholder={`Max: ${listing.available_quantity}`}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Offered Price per {listing.unit} (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={offerPrice}
                    onChange={(e) => setOfferPrice(e.target.value)}
                    placeholder={`Farmer asks ₹${listing.price_per_unit}`}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Logistics / Delivery Preference
                  </label>
                  <select
                    value={deliveryMethod}
                    onChange={(e) => setDeliveryMethod(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
                  >
                    <option value="BUYER_PICKUP">Buyer Arranges Pickup at Farm Depot</option>
                    <option value="SELLER_DELIVERY">Farmer Delivers to Buyer's Facility</option>
                    <option value="THIRD_PARTY">Mutually Arranged Third-Party Transport</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Terms & Notes (Optional)
                  </label>
                  <textarea
                    rows={2}
                    value={offerMsg}
                    onChange={(e) => setOfferMsg(e.target.value)}
                    placeholder="e.g. Can collect this Saturday with local truck"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
                  />
                </div>

                {/* Calculation summary */}
                {calculatedTotal > 0 && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1">
                    <div className="flex justify-between text-slate-600">
                      <span>Proposed Gross Value:</span>
                      <strong className="text-slate-900">₹{calculatedTotal.toLocaleString('en-IN')}</strong>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={submittingOffer}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-xl text-sm shadow-md transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  <span>{submittingOffer ? 'Transmitting Offer...' : 'Send Direct Offer'}</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
