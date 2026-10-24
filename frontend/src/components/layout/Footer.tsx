import React from 'react';
import { Sprout, ShieldCheck, Info, Scale } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 text-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand & Purpose */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2 text-white font-bold text-lg">
              <Sprout className="w-5 h-5 text-emerald-500" />
              <span>Rajya Krishi Banda</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-md">
              A transparent digital agricultural marketplace serving farmers and commercial buyers in Udupi and Dakshina Kannada districts of Karnataka. Designed to reduce unnecessary intermediaries and promote direct contract negotiation.
            </p>
            <div className="flex items-center space-x-4 pt-2 text-xs text-slate-400">
              <span className="flex items-center space-x-1">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Verified Coastal Growers</span>
              </span>
              <span className="flex items-center space-x-1">
                <Scale className="w-4 h-4 text-blue-400" />
                <span>Fair Price Transparency</span>
              </span>
            </div>
          </div>

          {/* Districts & Commodities */}
          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">Districts & Crops</h4>
            <ul className="space-y-1.5 text-xs">
              <li>Udupi District (Kundapura, Karkala, Udupi, Brahmavara)</li>
              <li>Dakshina Kannada (Mangaluru, Belthangady, Puttur, Bantwal, Sullia)</li>
              <li className="text-slate-300 font-medium pt-1">Arecanut, Coconut, Red Paddy, Pepper, Cashew</li>
            </ul>
          </div>

          {/* Platform Standards */}
          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">Governance & Policies</h4>
            <ul className="space-y-1.5 text-xs">
              <li>Verified Identity Requirements</li>
              <li>Transparent Indicative Benchmarks</li>
              <li>Mutual Delivery Agreements</li>
              <li>Dispute Mediation Protocol</li>
            </ul>
          </div>
        </div>

        {/* Clear Regulatory & Operational Disclaimers */}
        <div className="border-t border-slate-800/80 pt-6 space-y-2 text-[11px] text-slate-400 leading-relaxed">
          <div className="flex items-start space-x-2">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <p>
              <strong>Platform Notice:</strong> Rajya Krishi Banda is an agricultural discovery and negotiation facilitator. The platform does not guarantee that farmers will always earn higher prices or that middlemen can be completely eliminated. Market reference benchmarks are clearly labeled indicative historical records (DEMO_DATA).
            </p>
          </div>
          <p className="text-slate-400">
            Logistics, transport fees, and simulated settlement flows are negotiated and agreed directly between verified transacting parties. Rajya Krishi Banda does not provide transportation or hold financial escrow.
          </p>
          <div className="pt-2 text-slate-400 flex flex-col sm:flex-row justify-between items-center text-[11px]">
            <span>© 2026 Rajya Krishi Banda Karnataka Coastal Agriculture Initiative.</span>
            <span className="mt-1 sm:mt-0">Private Open-Source Architecture • Dev Hack 2026</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
