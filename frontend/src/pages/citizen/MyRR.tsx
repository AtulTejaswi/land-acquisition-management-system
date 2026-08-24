import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { EmptyState } from '../../components/shared/EmptyState';
import { StageProgress } from '../../components/rr/StageProgress';
import { BenefitTracker } from '../../components/rr/BenefitTracker';

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
        <h1 className="text-2xl font-bold text-slate-900">
          🏘️ My Rehabilitation & Resettlement
        </h1>
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
          {families.map((family: any) => (
            <Card key={family.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{family.family_head_name}</CardTitle>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      family.current_stage === 'resettled'
                        ? 'bg-emerald-100 text-emerald-700'
                        : family.current_stage === 'benefit_disbursement'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {family.current_stage?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                  </span>
                </div>
                <p className="text-xs text-slate-500">
                  Family ID: {family.family_id_number || '—'} • {family.member_count || 0}{' '}
                  members
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <StageProgress currentStage={family.current_stage} />

                <div className="pt-4 border-t">
                  <BenefitTracker
                    displacedStatus={family.displaced_status}
                    housingStatus={family.housing_benefit_status}
                    employmentStatus={family.employment_benefit_status}
                    monetaryAmount={family.monetary_benefit_amount || 0}
                  />
                </div>

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
          ))}
        </div>
      )}
    </div>
  );
}
