import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { EmptyState } from '../../components/shared/EmptyState';
import { formatCurrency } from '../../lib/utils';

const STAGE_LABELS: Record<string, string> = {
  identification: 'Identification',
  verification: 'Verification',
  benefit_disbursement: 'Benefit Disbursement',
  resettled: 'Resettled',
};

const STAGE_ORDER = ['identification', 'verification', 'benefit_disbursement', 'resettled'];

export default function MyRR() {
  const { data: rrData, isLoading } = useQuery({
    queryKey: ['citizen-rr'],
    queryFn: async () => {
      const { data } = await api.get('/rr/families', { params: { page_size: 50 } });
      return data;
    },
  });

  const families = rrData?.items || [];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">🏘️ My Rehabilitation & Resettlement</h1>
        <p className="text-slate-500 text-sm">
          Track your R&R entitlements, benefits, and resettlement progress
        </p>
      </motion.div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="skeleton h-40 rounded-xl" />
          ))}
        </div>
      ) : families.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <EmptyState
              icon="🏘️"
              title="No R&R records found"
              description="Your rehabilitation and resettlement records will appear here once created by the district authority."
            />
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {families.map((family: any) => {
            const currentStageIdx = STAGE_ORDER.indexOf(family.current_stage);
            return (
              <Card key={family.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">
                      {family.family_head_name}
                    </CardTitle>
                    <StatusBadge status={family.current_stage} />
                  </div>
                  <p className="text-xs text-slate-500">
                    Family ID: {family.family_id_number || '—'} •{' '}
                    {family.member_count || 0} members
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Stage Progress */}
                  <div className="flex items-center gap-0">
                    {STAGE_ORDER.map((stage, idx) => {
                      const isCompleted = idx < currentStageIdx;
                      const isCurrent = idx === currentStageIdx;
                      return (
                        <React.Fragment key={stage}>
                          <div className="flex flex-col items-center flex-shrink-0" style={{ width: '120px' }}>
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-xs font-bold ${
                                isCompleted
                                  ? 'bg-emerald-500 border-emerald-500 text-white'
                                  : isCurrent
                                  ? 'bg-blue-500 border-blue-500 text-white pulse-dot'
                                  : 'bg-white border-slate-300 text-slate-400'
                              }`}
                            >
                              {isCompleted ? '✓' : idx + 1}
                            </div>
                            <span
                              className={`mt-1.5 text-[10px] text-center leading-tight ${
                                isCurrent
                                  ? 'text-blue-600 font-semibold'
                                  : isCompleted
                                  ? 'text-emerald-600'
                                  : 'text-slate-400'
                              }`}
                            >
                              {STAGE_LABELS[stage]}
                            </span>
                          </div>
                          {idx < STAGE_ORDER.length - 1 && (
                            <div
                              className={`h-0.5 flex-1 -mt-5 ${
                                idx < currentStageIdx ? 'bg-emerald-500' : 'bg-slate-200'
                              }`}
                            />
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>

                  {/* Benefits Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-4 border-t">
                    <div className="text-center">
                      <div className="text-xs text-slate-500 mb-1">Displacement</div>
                      <StatusBadge status={family.displaced_status} />
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-slate-500 mb-1">Housing</div>
                      <StatusBadge status={family.housing_benefit_status} />
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-slate-500 mb-1">Employment</div>
                      <StatusBadge status={family.employment_benefit_status} />
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-slate-500 mb-1">Monetary Benefit</div>
                      <div className="text-sm font-semibold text-slate-900 tabular-nums">
                        {formatCurrency(family.monetary_benefit_amount || 0)}
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div>
                    <div className="flex justify-between text-xs text-slate-500 mb-1">
                      <span>Overall Progress</span>
                      <span className="tabular-nums">{family.progress_percentage || 0}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full transition-all"
                        style={{ width: `${family.progress_percentage || 0}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
