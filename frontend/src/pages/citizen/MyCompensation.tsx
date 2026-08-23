import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { formatCurrency, formatDate, getStatusColor } from '../../lib/utils';
import { EmptyState } from '../../components/shared/EmptyState';

export default function MyCompensation() {
  const { data: compensations, isLoading } = useQuery({
    queryKey: ['citizen-compensations'],
    queryFn: async () => {
      const { data } = await api.get('/compensation', { params: { page_size: 50 } });
      return data;
    },
  });

  const { data: payments } = useQuery({
    queryKey: ['citizen-payments'],
    queryFn: async () => {
      const { data } = await api.get('/payments', { params: { page_size: 50 } });
      return data;
    },
  });

  const totalAwarded = compensations?.items?.reduce((sum: number, c: any) => sum + Number(c.total_award || 0), 0) || 0;
  const totalPaid = payments?.items?.filter((p: any) => p.payment_status === 'disbursed')
    .reduce((sum: number, p: any) => sum + Number(p.amount || 0), 0) || 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">💰 My Compensation</h1>
        <p className="text-slate-500 text-sm">View your compensation awards and payment history</p>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 border-emerald-200">
          <CardContent className="p-4">
            <div className="text-sm text-emerald-600 font-medium">Total Awarded</div>
            <div className="text-2xl font-bold text-emerald-700 tabular-nums">{formatCurrency(totalAwarded)}</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200">
          <CardContent className="p-4">
            <div className="text-sm text-blue-600 font-medium">Total Disbursed</div>
            <div className="text-2xl font-bold text-blue-700 tabular-nums">{formatCurrency(totalPaid)}</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-50 to-amber-100/50 border-amber-200">
          <CardContent className="p-4">
            <div className="text-sm text-amber-600 font-medium">Pending</div>
            <div className="text-2xl font-bold text-amber-700 tabular-nums">{formatCurrency(totalAwarded - totalPaid)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Compensation Records */}
      <Card>
        <CardHeader>
          <CardTitle>Compensation Awards</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-24 rounded-lg" />)}
            </div>
          ) : compensations?.items?.length === 0 ? (
            <EmptyState icon="📋" title="No compensation records" description="Compensation will appear here once assessed by the district authority." />
          ) : (
            <div className="space-y-3">
              {compensations?.items?.map((comp: any) => (
                <div key={comp.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-slate-900">Award Amount: {formatCurrency(Number(comp.total_award))}</div>
                      <div className="text-sm text-slate-500 mt-1 space-x-4">
                        <span>Market Value: <span className="tabular-nums">{formatCurrency(Number(comp.market_value))}</span></span>
                        <span>Solatium: <span className="tabular-nums">{formatCurrency(Number(comp.solatium))}</span></span>
                        {comp.additional_compensation > 0 && (
                          <span>Additional: <span className="tabular-nums">{formatCurrency(Number(comp.additional_compensation))}</span></span>
                        )}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        Assessed: {formatDate(comp.assessment_date)}
                      </div>
                    </div>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(comp.status)}`}>
                      {comp.status?.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payment Records */}
      <Card>
        <CardHeader>
          <CardTitle>🏦 Payment History</CardTitle>
        </CardHeader>
        <CardContent>
          {payments?.items?.length === 0 ? (
            <EmptyState icon="🏦" title="No payments yet" description="Payment disbursement information will appear here." />
          ) : (
            <div className="space-y-3">
              {payments?.items?.map((pay: any) => (
                <div key={pay.id} className="border border-slate-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-slate-900 tabular-nums">{formatCurrency(Number(pay.amount))}</div>
                      <div className="text-xs text-slate-500 mt-1">PFMS Ref: {pay.pfms_reference || '—'}</div>
                      <div className="text-xs text-slate-500">Bank Verification: {pay.bank_verification_status?.replace(/_/g, ' ')}</div>
                      {pay.disbursed_date && <div className="text-xs text-slate-400">Disbursed: {formatDate(pay.disbursed_date)}</div>}
                    </div>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(pay.payment_status)}`}>
                      {pay.payment_status?.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
