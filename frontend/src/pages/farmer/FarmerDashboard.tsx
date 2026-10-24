import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  getFarmerProfile,
  getFarmerStats,
  getListings,
  getOffers,
  getOrders,
  acceptOffer,
  rejectOffer,
  counterOffer,
  updateOrderStatus,
  getOrderBreakdown,
  submitFarmerVerification,
} from '../../services/api';
import { Listing, Offer, Order, FarmerProfile } from '../../types';
import {
  Sprout,
  Plus,
  ShoppingBag,
  TrendingUp,
  ShieldCheck,
  Clock,
  CheckCircle2,
  XCircle,
  Truck,
  IndianRupee,
  FileText,
  AlertCircle,
  ArrowRight,
  MessageSquare,
} from 'lucide-react';

export const FarmerDashboard: React.FC = () => {
  const { user } = useAuth();

  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [stats, setStats] = useState<any>({
    active_listings_count: 0,
    pending_offers_count: 0,
    active_orders_count: 0,
    completed_revenue: 0,
  });

  const [listings, setListings] = useState<Listing[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  // Counter offer modal/state
  const [counterModalOpen, setCounterModalOpen] = useState(false);
  const [activeOffer, setActiveOffer] = useState<Offer | null>(null);
  const [counterPrice, setCounterPrice] = useState('');
  const [counterQty, setCounterQty] = useState('');
  const [counterMsg, setCounterMsg] = useState('');

  // Net Proceeds modal state
  const [breakdownModalOpen, setBreakdownModalOpen] = useState(false);
  const [selectedBreakdown, setSelectedBreakdown] = useState<any | null>(null);

  // Verification submission state
  const [docPath, setDocPath] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [verifyMsg, setVerifyMsg] = useState<string | null>(null);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [profRes, statsRes, listRes, offRes, ordRes] = await Promise.all([
        getFarmerProfile(),
        getFarmerStats(),
        getListings({ status_filter: 'ACTIVE' }),
        getOffers({ role_view: 'seller' }),
        getOrders({ role_view: 'seller' }),
      ]);
      setProfile(profRes.data);
      setStats(statsRes.data);
      // Filter listings for current farmer
      setListings(listRes.data.filter((l: any) => l.farmer?.id === user?.id));
      setOffers(offRes.data);
      setOrders(ordRes.data);
    } catch (err) {
      console.error('Error loading farmer dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [user]);

  const handleAcceptOffer = async (offerId: number) => {
    try {
      await acceptOffer(offerId);
      alert('Offer accepted! Confirmed order created and stock reserved.');
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to accept offer');
    }
  };

  const handleRejectOffer = async (offerId: number) => {
    try {
      await rejectOffer(offerId);
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reject offer');
    }
  };

  const openCounterModal = (offer: Offer) => {
    setActiveOffer(offer);
    setCounterPrice(offer.price_per_unit.toString());
    setCounterQty(offer.quantity.toString());
    setCounterMsg('');
    setCounterModalOpen(true);
  };

  const handleSendCounter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeOffer) return;
    try {
      await counterOffer(activeOffer.id, {
        quantity: parseFloat(counterQty),
        price_per_unit: parseFloat(counterPrice),
        message: counterMsg || undefined,
      });
      setCounterModalOpen(false);
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to send counteroffer');
    }
  };

  const viewOrderBreakdown = async (orderId: number) => {
    try {
      const res = await getOrderBreakdown(orderId);
      setSelectedBreakdown(res.data);
      setBreakdownModalOpen(true);
    } catch (err: any) {
      alert('Could not fetch breakdown');
    }
  };

  const handleOrderStatusUpdate = async (orderId: number, nextStatus: string) => {
    try {
      await updateOrderStatus(orderId, nextStatus);
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Status transition invalid');
    }
  };

  const handleVerificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docPath) return;
    setVerifying(true);
    try {
      const res = await submitFarmerVerification({ verification_document_path: docPath });
      setVerifyMsg(res.data.message);
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Verification submission failed');
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Farmer Portal</h1>
              {profile?.verification_status === 'APPROVED' ? (
                <span className="flex items-center space-x-1 bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-emerald-300">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Verified Grower</span>
                </span>
              ) : (
                <span className="flex items-center space-x-1 bg-amber-100 text-amber-800 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-amber-300">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{profile?.verification_status || 'Unverified'}</span>
                </span>
              )}
            </div>
            <p className="text-sm text-slate-600 mt-1">
              Welcome back, {user?.full_name}. Direct farm-to-buyer sales management.
            </p>
          </div>

          <Link
            to="/farmer/create-listing"
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2.5 rounded-xl font-semibold text-sm shadow-sm transition flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>List Produce</span>
          </Link>
        </div>

        {/* Verification Alert Banner if not approved */}
        {profile && profile.verification_status !== 'APPROVED' && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-amber-900">Verification Pending</h4>
                <p className="text-xs text-amber-700 mt-0.5">
                  To publish active listings directly, please submit your RTC/Pahani or land record identifier for administrative verification.
                </p>
              </div>
            </div>
            <form onSubmit={handleVerificationSubmit} className="flex items-center space-x-2 w-full sm:w-auto">
              <input
                type="text"
                value={docPath}
                onChange={(e) => setDocPath(e.target.value)}
                placeholder="e.g. RTC-KARKALA-2026-44"
                className="px-3 py-1.5 bg-white border border-amber-300 rounded-lg text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
              <button
                type="submit"
                disabled={verifying || !docPath}
                className="bg-amber-700 hover:bg-amber-800 text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition disabled:opacity-50"
              >
                {verifying ? 'Submitting...' : 'Submit'}
              </button>
            </form>
          </div>
        )}
        {verifyMsg && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl p-3 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{verifyMsg}</span>
          </div>
        )}

        {/* Key Operational Statistics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Lots</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{stats.active_listings_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Offers</div>
            <div className="text-2xl font-black text-amber-600 mt-1">{stats.pending_offers_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Orders</div>
            <div className="text-2xl font-black text-blue-600 mt-1">{stats.active_orders_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed Revenue</div>
            <div className="text-2xl font-black text-emerald-600 mt-1">₹{Number(stats.completed_revenue).toLocaleString('en-IN')}</div>
          </div>
        </div>

        {/* Section 1: Incoming Buyer Offers & Negotiation */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              <span>Incoming Buyer Offers</span>
            </h2>
            <span className="text-xs font-semibold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full">
              {offers.filter(o => o.status === 'PENDING').length} Action Required
            </span>
          </div>

          {offers.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">No buyer offers received yet.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {offers.map((off) => (
                <div key={off.id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{off.buyer_name}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        off.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                        off.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                        off.status === 'COUNTERED' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {off.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Offered: <strong className="text-slate-900">{off.quantity} {off.unit}</strong> @ <strong className="text-emerald-700">₹{off.price_per_unit}/{off.unit}</strong>
                      <span className="ml-2 text-slate-400">Total: ₹{Number(off.total_price).toLocaleString('en-IN')}</span>
                    </div>
                    {off.message && (
                      <div className="text-[11px] text-slate-500 italic">"{off.message}"</div>
                    )}
                  </div>

                  {off.status === 'PENDING' && (
                    <div className="flex items-center space-x-2 w-full sm:w-auto">
                      <button
                        onClick={() => handleAcceptOffer(off.id)}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => openCounterModal(off)}
                        className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Counter
                      </button>
                      <button
                        onClick={() => handleRejectOffer(off.id)}
                        className="bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Decline
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 2: Active Orders & Fulfilment */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <ShoppingBag className="w-5 h-5 text-blue-600" />
              <span>Orders & Fulfilment</span>
            </h2>
          </div>

          {orders.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">No active orders yet. Accepted offers will appear here.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {orders.map((ord) => (
                <div key={ord.id} className="py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">Order #{ord.id} - {ord.commodity_name}</span>
                      <span className="text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-200">
                        {ord.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Buyer: <strong>{ord.buyer_name}</strong> • Quantity: <strong>{ord.quantity} {ord.unit}</strong> • Agreed: <strong>₹{ord.price_per_unit}/{ord.unit}</strong>
                    </div>
                    <div className="text-xs text-emerald-700 font-semibold">
                      Contract Value: ₹{Number(ord.total_price).toLocaleString('en-IN')}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/messages?orderId=${ord.id}`}
                      className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold px-3 py-1.5 rounded-lg border border-emerald-200 transition flex items-center space-x-1"
                      title="Coordinate delivery & logistics"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      <span>Message Buyer</span>
                    </Link>

                    <button
                      onClick={() => viewOrderBreakdown(ord.id)}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 transition flex items-center space-x-1"
                    >
                      <IndianRupee className="w-3.5 h-3.5" />
                      <span>Net Proceeds</span>
                    </button>

                    {ord.status === 'CONFIRMED' && (
                      <button
                        onClick={() => handleOrderStatusUpdate(ord.id, 'PAYMENT_PENDING')}
                        className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Request Payment
                      </button>
                    )}

                    {ord.status === 'PAYMENT_CONFIRMED' && (
                      <button
                        onClick={() => handleOrderStatusUpdate(ord.id, 'READY_FOR_PICKUP')}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Ready for Pickup
                      </button>
                    )}

                    {ord.status === 'READY_FOR_PICKUP' && (
                      <button
                        onClick={() => handleOrderStatusUpdate(ord.id, 'DISPATCHED')}
                        className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Mark Dispatched
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Counter Offer Modal */}
      {counterModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Submit Counter-Offer</h3>
            <form onSubmit={handleSendCounter} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">Quantity ({activeOffer?.unit})</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={counterQty}
                  onChange={(e) => setCounterQty(e.target.value)}
                  className="mt-1 w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">Your Counter Rate per Unit (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={counterPrice}
                  onChange={(e) => setCounterPrice(e.target.value)}
                  className="mt-1 w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">Note / Message to Buyer</label>
                <textarea
                  rows={2}
                  value={counterMsg}
                  onChange={(e) => setCounterMsg(e.target.value)}
                  className="mt-1 w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setCounterModalOpen(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold"
                >
                  Send Counter
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* PHASE 13: Estimated Net Proceeds Breakdown Modal */}
      {breakdownModalOpen && selectedBreakdown && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900">Estimated Net Proceeds</h3>
              <button onClick={() => setBreakdownModalOpen(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Gross Sale Value:</span>
                <strong className="text-slate-900">₹{selectedBreakdown.gross_sale_value.toLocaleString('en-IN')}</strong>
              </div>
              <div className="flex justify-between py-1 text-red-600 text-xs">
                <span>- Seller Transport Deductions:</span>
                <span>₹{selectedBreakdown.deductions.seller_transport_cost}</span>
              </div>
              <div className="flex justify-between py-1 text-red-600 text-xs">
                <span>- Packaging & Handling Expenses:</span>
                <span>₹{selectedBreakdown.deductions.packaging_and_handling}</span>
              </div>
              <div className="flex justify-between py-1 text-red-600 text-xs border-b border-slate-100 pb-2">
                <span>- Disclosed Platform Charges:</span>
                <span>₹{selectedBreakdown.deductions.disclosed_platform_charges} (0%)</span>
              </div>
              <div className="flex justify-between py-2 bg-emerald-50 px-3 rounded-xl text-emerald-900 text-base font-bold">
                <span>Estimated Net Proceeds:</span>
                <span>₹{selectedBreakdown.estimated_net_proceeds.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 italic leading-relaxed">
              {selectedBreakdown.disclaimer}
            </p>

            <div className="text-right pt-2">
              <button
                onClick={() => setBreakdownModalOpen(false)}
                className="bg-slate-900 text-white text-xs font-semibold px-4 py-2 rounded-xl"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
