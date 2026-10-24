import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  getBuyerProfile,
  getBuyerStats,
  getRequirements,
  getOffers,
  getOrders,
  recordPayment,
  updateOrderStatus,
} from '../../services/api';
import { BuyerRequirement, Offer, Order, BuyerProfile } from '../../types';
import {
  Building2,
  Plus,
  Search,
  Scale,
  ShoppingBag,
  IndianRupee,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  MessageSquare,
} from 'lucide-react';

export const BuyerDashboard: React.FC = () => {
  const { user } = useAuth();

  const [profile, setProfile] = useState<BuyerProfile | null>(null);
  const [stats, setStats] = useState<any>({
    active_requirements_count: 0,
    pending_offers_count: 0,
    active_orders_count: 0,
    total_spend: 0,
  });

  const [requirements, setRequirements] = useState<BuyerRequirement[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [profRes, statsRes, reqRes, offRes, ordRes] = await Promise.all([
        getBuyerProfile(),
        getBuyerStats(),
        getRequirements({ my_only: true }),
        getOffers({ role_view: 'buyer' }),
        getOrders({ role_view: 'buyer' }),
      ]);
      setProfile(profRes.data);
      setStats(statsRes.data);
      setRequirements(reqRes.data);
      setOffers(offRes.data);
      setOrders(ordRes.data);
    } catch (err) {
      console.error('Error loading buyer dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [user]);

  const handleSimulatePayment = async (order: Order) => {
    try {
      await recordPayment({
        order_id: order.id,
        amount: order.total_price,
        reference_number: `SIM-TXN-${Date.now()}`,
      });
      alert('Simulated payment logged! Order marked as PAYMENT_CONFIRMED.');
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Payment record failed');
    }
  };

  const handleConfirmReceived = async (orderId: number) => {
    try {
      await updateOrderStatus(orderId, 'COMPLETED');
      alert('Order completed! Produce verified and received.');
      loadAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Could not complete order');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Commercial Buyer Portal</h1>
              {profile?.verification_status === 'APPROVED' ? (
                <span className="flex items-center space-x-1 bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-emerald-300">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Verified Buyer</span>
                </span>
              ) : (
                <span className="flex items-center space-x-1 bg-slate-100 text-slate-700 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-slate-300">
                  <span>{profile?.verification_status || 'Registered'}</span>
                </span>
              )}
            </div>
            <p className="text-sm text-slate-600 mt-1">
              {profile?.business_name || user?.full_name} • Coastal Agricultural Procurement
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              to="/marketplace"
              className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 px-4 py-2.5 rounded-xl font-semibold text-sm shadow-sm transition flex items-center space-x-1.5"
            >
              <Search className="w-4 h-4 text-slate-500" />
              <span>Browse Lots</span>
            </Link>
            <Link
              to="/buyer/create-requirement"
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2.5 rounded-xl font-semibold text-sm shadow-sm transition flex items-center space-x-1.5"
            >
              <Plus className="w-4 h-4" />
              <span>Post Requirement</span>
            </Link>
          </div>
        </div>

        {/* Operational Statistics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Specs</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{stats.active_requirements_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Offers</div>
            <div className="text-2xl font-black text-amber-600 mt-1">{stats.pending_offers_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Purchases</div>
            <div className="text-2xl font-black text-blue-600 mt-1">{stats.active_orders_count}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Spend</div>
            <div className="text-2xl font-black text-emerald-600 mt-1">₹{Number(stats.total_spend).toLocaleString('en-IN')}</div>
          </div>
        </div>

        {/* Section 1: Active Procurement Requirements & Matches */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Scale className="w-5 h-5 text-emerald-600" />
              <span>My Procurement Requirements</span>
            </h2>
            <Link
              to="/buyer/create-requirement"
              className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center space-x-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Requirement</span>
            </Link>
          </div>

          {requirements.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">
              No active procurement specs posted yet. Post what commodity and volume you need to find matched growers.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {requirements.map((req) => (
                <div key={req.id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{req.commodity_name}</span>
                      <span className="text-[10px] bg-emerald-50 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-200">
                        Needed: {req.quantity_needed} {req.unit || 'KG'}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Variety Pref: <strong>{req.variety_preference || 'Any'}</strong> • Max Budget: <strong>{req.max_price_per_unit ? `₹${req.max_price_per_unit}/${req.unit}` : 'Negotiable'}</strong>
                    </div>
                    {req.needed_by && (
                      <div className="text-[11px] text-slate-500">Needed by: {req.needed_by}</div>
                    )}
                  </div>

                  <Link
                    to={`/buyer/matches/${req.id}`}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition flex items-center space-x-1.5 shadow-sm"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Find Matching Growers</span>
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 2: Outgoing Offers & Status */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Clock className="w-5 h-5 text-amber-600" />
              <span>Offers & Negotiations Sent</span>
            </h2>
          </div>

          {offers.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">No offers currently submitted.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {offers.map((off) => (
                <div key={off.id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">To: {off.seller_name}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        off.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                        off.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                        off.status === 'COUNTERED' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {off.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Produce: <strong>{off.listing_title}</strong> • Qty: <strong>{off.quantity} {off.unit}</strong> @ <strong>₹{off.price_per_unit}/{off.unit}</strong>
                    </div>
                    <div className="text-xs text-slate-500">
                      Total: ₹{Number(off.total_price).toLocaleString('en-IN')}
                    </div>
                  </div>

                  <Link
                    to={`/marketplace/${off.listing_id}`}
                    className="text-xs font-semibold text-emerald-600 hover:text-emerald-700"
                  >
                    View Listing
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 3: Orders & Fulfilment */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <ShoppingBag className="w-5 h-5 text-blue-600" />
              <span>Purchase Orders</span>
            </h2>
          </div>

          {orders.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">No active purchase orders.</div>
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
                      Grower: <strong>{ord.seller_name}</strong> • Reserved: <strong>{ord.reserved_quantity} {ord.unit}</strong> • Agreed: <strong>₹{ord.price_per_unit}/{ord.unit}</strong>
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
                      <span>Message Farmer</span>
                    </Link>

                    {ord.status === 'PAYMENT_PENDING' && (
                      <button
                        onClick={() => handleSimulatePayment(ord)}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Simulate Payment
                      </button>
                    )}

                    {ord.status === 'DELIVERED' && (
                      <button
                        onClick={() => handleConfirmReceived(ord.id)}
                        className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                      >
                        Confirm Receipt & Complete
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
