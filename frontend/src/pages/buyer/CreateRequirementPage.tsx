import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getCommodities, createRequirement } from '../../services/api';
import { Commodity } from '../../types';
import { ArrowLeft, AlertCircle } from 'lucide-react';

export const CreateRequirementPage: React.FC = () => {
  const navigate = useNavigate();

  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [commodityId, setCommodityId] = useState('');
  const [varietyPref, setVarietyPref] = useState('');
  const [qualityPref, setQualityPref] = useState('A');
  const [quantityNeeded, setQuantityNeeded] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [deliveryLocation, setDeliveryLocation] = useState('');
  const [deliveryDistrict, setDeliveryDistrict] = useState('DAKSHINA_KANNADA');
  const [neededBy, setNeededBy] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCommodities()
      .then((res) => {
        setCommodities(res.data);
        if (res.data.length > 0) {
          setCommodityId(res.data[0].id.toString());
        }
      })
      .catch((err) => console.error(err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const qty = parseFloat(quantityNeeded);
    if (!qty || qty <= 0) {
      setError('Quantity needed must be greater than zero');
      return;
    }

    setLoading(true);

    try {
      const res = await createRequirement({
        commodity_id: Number(commodityId),
        variety_preference: varietyPref || null,
        quality_preference: qualityPref || null,
        quantity_needed: qty,
        max_price_per_unit: maxPrice ? parseFloat(maxPrice) : null,
        delivery_location: deliveryLocation || null,
        delivery_district: deliveryDistrict,
        needed_by: neededBy || null,
      });

      alert(res.data.message);
      navigate(`/buyer/matches/${res.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to post requirement');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <Link to="/buyer/dashboard" className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Buyer Portal</span>
        </Link>

        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Post Procurement Requirement</h1>
            <p className="text-xs text-slate-500 mt-1">
              Specify your volume, target budget, and delivery timeline to trigger automated grower matching.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Target Commodity</label>
              <select
                value={commodityId}
                onChange={(e) => setCommodityId(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              >
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.name_kn ? `(${c.name_kn})` : ''} - Unit: {c.unit}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Variety Preference</label>
                <input
                  type="text"
                  value={varietyPref}
                  onChange={(e) => setVarietyPref(e.target.value)}
                  placeholder="e.g. Chali Whole Dried, Jaya Paddy"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Quality Grade Spec</label>
                <select
                  value={qualityPref}
                  onChange={(e) => setQualityPref(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                >
                  <option value="A">Grade A (Premium)</option>
                  <option value="B">Grade B (Standard)</option>
                  <option value="C">Grade C (Commercial)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Quantity Needed</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={quantityNeeded}
                  onChange={(e) => setQuantityNeeded(e.target.value)}
                  placeholder="e.g. 80"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Max Budget per Unit (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  placeholder="e.g. 470 (Optional)"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Destination District</label>
                <select
                  value={deliveryDistrict}
                  onChange={(e) => setDeliveryDistrict(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                >
                  <option value="DAKSHINA_KANNADA">Dakshina Kannada</option>
                  <option value="UDUPI">Udupi</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Needed By Date</label>
                <input
                  type="date"
                  value={neededBy}
                  onChange={(e) => setNeededBy(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Delivery / Facility Location</label>
              <input
                type="text"
                value={deliveryLocation}
                onChange={(e) => setDeliveryLocation(e.target.value)}
                placeholder="e.g. Bunder Wholesale Depot, Mangaluru"
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-xl text-sm shadow-md transition disabled:opacity-50"
            >
              {loading ? 'Publishing...' : 'Publish & Find Matching Growers'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
