import React from 'react';
import { StatusBadge } from '../shared/StatusBadge';

interface BenefitTrackerProps {
  displacedStatus: string;
  housingStatus: string;
  employmentStatus: string;
  monetaryAmount?: number;
  layout?: 'grid' | 'row';
}

export function BenefitTracker({
  displacedStatus,
  housingStatus,
  employmentStatus,
  monetaryAmount,
  layout = 'grid',
}: BenefitTrackerProps) {
  const formatCurrency = (amount: number) => {
    if (amount >= 1e7) return `\u20b9${(amount / 1e7).toFixed(1)}Cr`;
    if (amount >= 1e5) return `\u20b9${(amount / 1e5).toFixed(1)}L`;
    return `\u20b9${amount.toLocaleString('en-IN')}`;
  };

  if (layout === 'row') {
    return (
      <div className="flex items-center gap-2 text-xs">
        <StatusBadge status={displacedStatus} />
        <StatusBadge status={housingStatus} />
        <StatusBadge status={employmentStatus} />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="text-center">
        <div className="text-xs text-slate-500 mb-1">Displacement</div>
        <StatusBadge status={displacedStatus} />
      </div>
      <div className="text-center">
        <div className="text-xs text-slate-500 mb-1">Housing</div>
        <StatusBadge status={housingStatus} />
      </div>
      <div className="text-center">
        <div className="text-xs text-slate-500 mb-1">Employment</div>
        <StatusBadge status={employmentStatus} />
      </div>
      {monetaryAmount !== undefined && (
        <div className="text-center">
          <div className="text-xs text-slate-500 mb-1">Monetary Benefit</div>
          <div className="text-sm font-semibold text-slate-900 tabular-nums">
            {formatCurrency(monetaryAmount)}
          </div>
        </div>
      )}
    </div>
  );
}
