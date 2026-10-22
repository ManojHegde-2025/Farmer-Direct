import React, { useEffect, useState } from 'react';
import {
  getAdminStats,
  getPendingVerifications,
  verifyFarmer,
  verifyBuyer,
  getAdminUsers,
  getDisputes,
  resolveDispute,
} from '../../services/api';
import {
  ShieldCheck,
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Scale,
  ShoppingBag,
  IndianRupee,
  Clock,
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<any>({
    total_farmers: 0,
    total_buyers: 0,
    pending_verifications: 0,
    active_listings: 0,
    total_orders: 0,
    total_trade_volume_inr: 0,
    open_disputes_count: 0,
  });

  const [verifications, setVerifications] = useState<any>({ farmers: [], buyers: [] });
  const [users, setUsers] = useState<any[]>([]);
  const [disputes, setDisputes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sRes, vRes, uRes, dRes] = await Promise.all([
        getAdminStats(),
        getPendingVerifications(),
        getAdminUsers(),
        getDisputes(),
      ]);
      setStats(sRes.data);
      setVerifications(vRes.data);
      setUsers(uRes.data);
      setDisputes(dRes.data);
    } catch (err) {
      console.error('Error loading admin data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFarmerDecision = async (profileId: number, status: 'APPROVED' | 'REJECTED') => {
    try {
      await verifyFarmer(profileId, { status, reason: 'Admin manual review completed' });
      alert(`Farmer profile marked as ${status}`);
      loadData();
    } catch (err: any) {
      alert('Verification decision failed');
    }
  };

  const handleBuyerDecision = async (profileId: number, status: 'APPROVED' | 'REJECTED') => {
    try {
      await verifyBuyer(profileId, { status, reason: 'Commercial documents verified' });
      alert(`Buyer profile marked as ${status}`);
      loadData();
    } catch (err: any) {
      alert('Verification decision failed');
    }
  };

  const handleResolveDispute = async (disputeId: number) => {
    const resolution = prompt('Enter resolution notes / settlement terms:');
    if (!resolution) return;
    try {
      await resolveDispute(disputeId, { status: 'RESOLVED', resolution });
      alert('Dispute resolved');
      loadData();
    } catch (err) {
      alert('Could not resolve dispute');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-800 rounded-xl border border-amber-500/20">
            <ShieldCheck className="w-6 h-6 text-amber-700" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">System Administration</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Agricultural verification, dispute resolution & marketplace oversight (Udupi & Dakshina Kannada)
            </p>
          </div>
        </div>

        {/* Real-time DB Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Verified Farmers</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{stats.total_farmers}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Commercial Buyers</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{stats.total_buyers}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Verifications</div>
            <div className="text-2xl font-black text-amber-600 mt-1">{stats.pending_verifications}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Orders Volume</div>
            <div className="text-2xl font-black text-emerald-600 mt-1">₹{Number(stats.total_trade_volume_inr).toLocaleString('en-IN')}</div>
          </div>
        </div>

        {/* Section 1: Farmer Verification Queue */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Clock className="w-5 h-5 text-amber-600" />
              <span>Grower Verification Queue ({verifications.farmers.length})</span>
            </h2>
          </div>

          {verifications.farmers.length === 0 ? (
            <div className="text-center py-6 text-slate-400 text-xs">No growers currently awaiting verification.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {verifications.farmers.map((f: any) => (
                <div key={f.profile_id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{f.full_name}</span>
                      <span className="text-xs text-slate-500">({f.email})</span>
                      <span className="text-[10px] bg-amber-50 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-200">
                        {f.verification_status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Estate: <strong>{f.farm_name || 'Family Farm'}</strong> • District: <strong>{f.district}</strong> • Taluk: <strong>{f.taluk}</strong> • Crops: <strong>{f.primary_crops}</strong>
                    </div>
                    {f.verification_document_path && (
                      <div className="text-[11px] text-blue-600 font-mono">
                        Document Record ID: {f.verification_document_path}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleFarmerDecision(f.profile_id, 'APPROVED')}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                    >
                      Approve Grower
                    </button>
                    <button
                      onClick={() => handleFarmerDecision(f.profile_id, 'REJECTED')}
                      className="bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold px-3 py-1.5 rounded-lg border border-red-200 transition"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 2: Commercial Buyer Verification Queue */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Clock className="w-5 h-5 text-blue-600" />
              <span>Commercial Buyer Verification Queue ({verifications.buyers.length})</span>
            </h2>
          </div>

          {verifications.buyers.length === 0 ? (
            <div className="text-center py-6 text-slate-400 text-xs">No buyers currently awaiting verification.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {verifications.buyers.map((b: any) => (
                <div key={b.profile_id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{b.business_name || b.full_name}</span>
                      <span className="text-xs text-slate-500">({b.email})</span>
                      <span className="text-[10px] bg-blue-50 text-blue-800 font-bold px-2 py-0.5 rounded border border-blue-200">
                        {b.verification_status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Type: <strong>{b.business_type}</strong> • GST: <strong>{b.gst_number || 'Unspecified'}</strong>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleBuyerDecision(b.profile_id, 'APPROVED')}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                    >
                      Approve Buyer
                    </button>
                    <button
                      onClick={() => handleBuyerDecision(b.profile_id, 'REJECTED')}
                      className="bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold px-3 py-1.5 rounded-lg border border-red-200 transition"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 3: Open Disputes */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span>Disputes & Claims Mediation</span>
            </h2>
          </div>

          {disputes.length === 0 ? (
            <div className="text-center py-6 text-slate-400 text-xs">No disputes currently filed.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {disputes.map((d: any) => (
                <div key={d.id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">Dispute #{d.id} - Order #{d.order_id}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-800">
                        {d.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600">
                      Raised by: <strong>{d.raised_by_name}</strong> vs <strong>{d.against_name}</strong> • Category: <strong>{d.category}</strong>
                    </div>
                    <div className="text-xs text-slate-700 font-medium">"{d.description}"</div>
                    {d.resolution && (
                      <div className="text-xs text-emerald-700">Resolution: {d.resolution}</div>
                    )}
                  </div>

                  {d.status === 'OPEN' && (
                    <button
                      onClick={() => handleResolveDispute(d.id)}
                      className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                    >
                      Mediate & Resolve
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 4: Platform Accounts Overview */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Users className="w-5 h-5 text-slate-700" />
              <span>Platform Accounts ({users.length})</span>
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 uppercase text-[10px] font-bold text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Email</th>
                  <th className="py-2.5 px-3">Role</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Verified</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono">{u.id}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{u.full_name}</td>
                    <td className="py-2.5 px-3">{u.email}</td>
                    <td className="py-2.5 px-3 font-semibold">{u.role}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${u.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      {u.is_verified ? '✅ Verified' : '⏳ Pending'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
