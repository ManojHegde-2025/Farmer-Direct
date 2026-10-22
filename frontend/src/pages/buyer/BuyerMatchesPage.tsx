import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMatchesForRequirement, getRequirementById } from '../../services/api';
import { MatchResult, BuyerRequirement } from '../../types';
import {
  Sparkles,
  ArrowLeft,
  ShieldCheck,
  MapPin,
  CheckCircle2,
  TrendingUp,
  Tag,
  ArrowRight,
} from 'lucide-react';

export const BuyerMatchesPage: React.FC = () => {
  const { reqId } = useParams<{ reqId: string }>();

  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [requirement, setRequirement] = useState<BuyerRequirement | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('score');

  const fetchMatches = () => {
    if (!reqId) return;
    setLoading(true);
    Promise.all([
      getRequirementById(Number(reqId)),
      getMatchesForRequirement(Number(reqId), { sort_by: sortBy }),
    ])
      .then(([reqRes, matchRes]) => {
        setRequirement(reqRes.data);
        setMatches(matchRes.data.matches);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMatches();
  }, [reqId, sortBy]);

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <Link to="/buyer/dashboard" className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Buyer Portal</span>
        </Link>

        {/* Spec Overview Card */}
        {requirement && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full w-fit">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Deterministic Matching Engine (PHASE 10 Rules)</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">
              Matches for {requirement.quantity_needed} {requirement.unit || 'KG'} of {requirement.commodity_name}
            </h1>
            <div className="text-xs text-slate-600 flex flex-wrap gap-x-4 gap-y-1 pt-1">
              <span>Variety: <strong>{requirement.variety_preference || 'Any'}</strong></span>
              <span>Target Budget: <strong>{requirement.max_price_per_unit ? `₹${requirement.max_price_per_unit}` : 'Negotiable'}</strong></span>
              <span>District: <strong>{requirement.delivery_district}</strong></span>
              {requirement.needed_by && <span>Needed By: <strong>{requirement.needed_by}</strong></span>}
            </div>
          </div>
        )}

        {/* Sort Controls */}
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-slate-600">
            {matches.length} Compatible Growers Recommended
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-500">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs text-slate-800 focus:outline-none"
            >
              <option value="score">Match Score (Highest)</option>
              <option value="price">Lowest Asking Price</option>
              <option value="quantity">Largest Available Quantity</option>
            </select>
          </div>
        </div>

        {/* Matches List */}
        {loading ? (
          <div className="text-center py-16 text-slate-400 text-sm">Evaluating compatibility constraints...</div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-2">
            <p className="font-bold text-slate-800">No compatible lots match this specification currently.</p>
            <p className="text-xs text-slate-500">Check back as farmers in Udupi & Dakshina Kannada log new harvests.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((m) => {
              const l = m.listing;
              return (
                <div
                  key={m.listing_id}
                  className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:border-emerald-400 transition space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-lg font-bold text-slate-900">{l.title}</span>
                        {l.farmer?.is_verified && (
                          <span className="flex items-center space-x-0.5 text-emerald-700 bg-emerald-50 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-emerald-200">
                            <ShieldCheck className="w-3 h-3 text-emerald-600" />
                            <span>Verified</span>
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-500 flex items-center space-x-2 mt-0.5">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>{l.farmer?.taluk ? `${l.farmer.taluk}, ` : ''}{l.farmer?.district}</span>
                        <span>•</span>
                        <span>Cultivator: <strong>{l.farmer?.full_name}</strong></span>
                      </div>
                    </div>

                    {/* Match Score Badge */}
                    <div className="flex items-center space-x-3 bg-emerald-50/80 border border-emerald-200/80 px-3.5 py-2 rounded-xl">
                      <div className="text-right">
                        <div className="text-[10px] text-emerald-800 uppercase font-semibold">Match Score</div>
                        <div className="text-2xl font-black text-emerald-700">{m.match_score}<span className="text-xs font-normal text-emerald-600">/100</span></div>
                      </div>
                    </div>
                  </div>

                  {/* Explainable Reasons */}
                  <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200/80 space-y-1.5">
                    <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                      Why this lot matches your requirement:
                    </div>
                    <ul className="space-y-1">
                      {m.match_reasons.map((reason, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-xs text-slate-700">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Stock, Rate & Action */}
                  <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center space-x-6 text-xs text-slate-700">
                      <div>
                        Asking Rate: <strong className="text-base text-slate-900 font-bold">₹{l.price_per_unit}</strong>/{l.unit}
                      </div>
                      <div>
                        Available: <strong className="text-slate-900">{l.available_quantity} {l.unit}</strong>
                      </div>
                      <div>
                        Fulfillable Now: <strong className="text-emerald-700 font-bold">{m.fulfillable_quantity} {l.unit}</strong>
                      </div>
                    </div>

                    <Link
                      to={`/marketplace/${l.id}`}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-sm transition flex items-center justify-center space-x-1.5"
                    >
                      <span>Review & Make Offer</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
