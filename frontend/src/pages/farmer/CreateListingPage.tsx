import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getCommodities, createListing } from '../../services/api';
import { Commodity } from '../../types';
import { Sprout, ArrowLeft, AlertCircle, CheckCircle2 } from 'lucide-react';

export const CreateListingPage: React.FC = () => {
  const navigate = useNavigate();

  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [commodityId, setCommodityId] = useState('');
  const [title, setTitle] = useState('');
  const [variety, setVariety] = useState('');
  const [qualityGrade, setQualityGrade] = useState('UNGRADED');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('KG');
  const [pricePerUnit, setPricePerUnit] = useState('');
  const [minOrderQty, setMinOrderQty] = useState('');
  const [harvestDate, setHarvestDate] = useState('');
  const [availableFrom, setAvailableFrom] = useState('');
  const [availableUntil, setAvailableUntil] = useState('');
  const [pickupLocation, setPickupLocation] = useState('');
  const [deliveryAvailable, setDeliveryAvailable] = useState(false);
  const [deliveryRadiusKm, setDeliveryRadiusKm] = useState('');
  const [description, setDescription] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCommodities()
      .then((res) => {
        setCommodities(res.data);
        if (res.data.length > 0) {
          setCommodityId(res.data[0].id.toString());
          setUnit(res.data[0].unit);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  const handleCommodityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const cid = e.target.value;
    setCommodityId(cid);
    const selected = commodities.find((c) => c.id === Number(cid));
    if (selected) {
      setUnit(selected.unit);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const qty = parseFloat(quantity);
    const price = parseFloat(pricePerUnit);

    if (!qty || qty <= 0) {
      setError('Quantity must be greater than zero');
      return;
    }
    if (!price || price <= 0) {
      setError('Price per unit must be greater than zero');
      return;
    }

    setLoading(true);

    try {
      const payload: any = {
        commodity_id: Number(commodityId),
        title,
        variety: variety || null,
        quality_grade: qualityGrade,
        quantity: qty,
        unit,
        price_per_unit: price,
        min_order_quantity: minOrderQty ? parseFloat(minOrderQty) : null,
        harvest_date: harvestDate || null,
        available_from: availableFrom || null,
        available_until: availableUntil || null,
        pickup_location: pickupLocation || null,
        delivery_available: deliveryAvailable,
        delivery_radius_km: deliveryRadiusKm ? parseInt(deliveryRadiusKm) : null,
        description: description || null,
      };

      const res = await createListing(payload);
      alert(res.data.message);
      navigate('/farmer/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create listing');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <Link to="/farmer/dashboard" className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>

        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Publish Produce Lot</h1>
            <p className="text-xs text-slate-500 mt-1">
              List available crop harvest for buyers in Udupi & Dakshina Kannada.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Commodity & Title */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Commodity Type</label>
                <select
                  value={commodityId}
                  onChange={handleCommodityChange}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                >
                  {commodities.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} {c.name_kn ? `(${c.name_kn})` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Listing Headline</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Sun-Dried Chali Arecanut - 100 kg Lot"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
            </div>

            {/* Variety & Grade */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Variety (Optional)</label>
                <input
                  type="text"
                  value={variety}
                  onChange={(e) => setVariety(e.target.value)}
                  placeholder="e.g. Chali Whole Dried, West Coast Tall"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Quality Grade</label>
                <select
                  value={qualityGrade}
                  onChange={(e) => setQualityGrade(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                >
                  <option value="A">Grade A (Premium)</option>
                  <option value="B">Grade B (Standard)</option>
                  <option value="C">Grade C (Commercial)</option>
                  <option value="UNGRADED">Ungraded / Field Mix</option>
                </select>
              </div>
            </div>

            {/* Quantity, Unit, Price */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Total Quantity</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="e.g. 100"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Unit of Measure</label>
                <input
                  type="text"
                  disabled
                  value={unit}
                  className="w-full px-3 py-2.5 bg-slate-100 border border-slate-300 rounded-xl text-sm font-semibold text-slate-700"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Asking Rate (₹/{unit})</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={pricePerUnit}
                  onChange={(e) => setPricePerUnit(e.target.value)}
                  placeholder="e.g. 450"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
            </div>

            {/* Timing */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Available From</label>
                <input
                  type="date"
                  value={availableFrom}
                  onChange={(e) => setAvailableFrom(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Available Until</label>
                <input
                  type="date"
                  value={availableUntil}
                  onChange={(e) => setAvailableUntil(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>
            </div>

            {/* Logistics */}
            <div className="space-y-3 pt-2 border-t border-slate-100">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Pickup Location / Depot</label>
                <input
                  type="text"
                  value={pickupLocation}
                  onChange={(e) => setPickupLocation(e.target.value)}
                  placeholder="e.g. Miyar Farm Depot, Karkala Taluk"
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
                />
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="delivCheck"
                  checked={deliveryAvailable}
                  onChange={(e) => setDeliveryAvailable(e.target.checked)}
                  className="w-4 h-4 text-emerald-600 rounded"
                />
                <label htmlFor="delivCheck" className="text-xs font-medium text-slate-700">
                  Can arrange delivery to buyer facility (transport costs negotiated)
                </label>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Description / Quality Notes</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="State sun-drying process, moisture conditions, packing methods..."
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-xl text-sm shadow-md transition disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Create Produce Listing'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
