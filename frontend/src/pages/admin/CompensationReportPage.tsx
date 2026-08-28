import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { KPICard } from '../../components/shared/KPICard';
import { StatusBadge } from '../../components/shared/StatusBadge';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

function formatCurrency(val: number) {
  if (val >= 1e7) return `₹${(val / 1e7).toFixed(2)} Cr`;
  if (val >= 1e5) return `₹${(val / 1e5).toFixed(2)} L`;
  return `₹${val.toLocaleString('en-IN')}`;
}

export default function CompensationReportPage() {
  const { data: compData, isLoading: compLoading } = useQuery({
    queryKey: ['compensation-report-all'],
    queryFn: async () => {
      const items: any[] = [];
      let page = 1;
      let hasMore = true;
      while (hasMore) {
        const { data } = await api.get('/compensation', { params: { page, page_size: 100 } });
        items.push(...(data.items || []));
        hasMore = items.length < data.total;
        page++;
        if (page > 10) break;
      }
      return items;
    },
  });

  const { data: parcelData } = useQuery({
    queryKey: ['comp-report-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/parcels', { params: { page_size: 200 } });
      return data.items || [];
    },
  });

  const { data: paymentData } = useQuery({
    queryKey: ['comp-report-payments'],
    queryFn: async () => {
      const items: any[] = [];
      let page = 1;
      let hasMore = true;
      while (hasMore) {
        const { data } = await api.get('/payments', { params: { page, page_size: 100 } });
        items.push(...(data.items || []));
        hasMore = items.length < data.total;
        page++;
        if (page > 10) break;
      }
      return items;
    },
  });

  const compensations = compData || [];
  const parcels = parcelData || [];
  const payments = paymentData || [];

  // Build parcel lookup
  const parcelMap: Record<string, any> = {};
  parcels.forEach((p: any) => { parcelMap[p.id] = p; });

  // KPI calculations
  const totalMarketValue = compensations.reduce((s: number, c: any) => s + (c.market_value || 0), 0);
  const totalSolatium = compensations.reduce((s: number, c: any) => s + (c.solatium || 0), 0);
  const totalAward = compensations.reduce((s: number, c: any) => s + (c.total_award || 0), 0);
  const totalDisbursed = payments.reduce((s: number, p: any) => s + (p.payment_status === 'disbursed' ? (p.amount || 0) : 0), 0);

  // Status distribution
  const statusCounts: Record<string, number> = {};
  compensations.forEach((c: any) => {
    statusCounts[c.status] = (statusCounts[c.status] || 0) + 1;
  });
  const statusPieData = Object.entries(statusCounts).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    value,
  }));

  // Top 5 awards
  const topAwards = [...compensations]
    .sort((a: any, b: any) => (b.total_award || 0) - (a.total_award || 0))
    .slice(0, 5)
    .map((c: any) => {
      const parcel = parcelMap[c.parcel_id] || {};
      return {
        name: parcel.survey_number || c.parcel_id?.slice(0, 8),
        award: c.total_award || 0,
        market: c.market_value || 0,
        solatium: c.solatium || 0,
      };
    });

  // Payment status breakdown
  const paymentStatusCounts: Record<string, number> = {};
  payments.forEach((p: any) => {
    paymentStatusCounts[p.payment_status] = (paymentStatusCounts[p.payment_status] || 0) + 1;
  });
  const paymentPieData = Object.entries(paymentStatusCounts).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    value,
  }));

  if (compLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="skeleton h-80 rounded-xl" />
          <div className="skeleton h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">💰 Compensation Report</h1>
        <p className="text-slate-500 text-sm">
          Comprehensive overview of compensation assessments, awards, and disbursements under RFCTLARR Act, 2013
        </p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Assessments" value={compensations.length} icon="📝" index={0} />
        <KPICard label="Total Market Value" value={formatCurrency(totalMarketValue)} icon="📊" index={1} />
        <KPICard label="Total Award Value" value={formatCurrency(totalAward)} icon="💰" index={2} />
        <KPICard label="Total Disbursed" value={formatCurrency(totalDisbursed)} icon="🏦" index={3} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Status Pie Chart */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Compensation Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {statusPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={statusPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {statusPieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`${value} records`, 'Count']} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-slate-400 text-sm">No data</div>
            )}
          </CardContent>
        </Card>

        {/* Top Awards Bar Chart */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Top 5 Compensation Awards</CardTitle>
          </CardHeader>
          <CardContent>
            {topAwards.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={topAwards} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v)} />
                  <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Bar dataKey="market" fill="#3B82F6" name="Market Value" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="solatium" fill="#10B981" name="Solatium" radius={[0, 4, 4, 0]} />
                  <Legend />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-slate-400 text-sm">No data</div>
            )}
          </CardContent>
        </Card>

        {/* Payment Status Pie */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Payment Disbursement Status</CardTitle>
          </CardHeader>
          <CardContent>
            {paymentPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={paymentPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {paymentPieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`${value} payments`, 'Count']} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-slate-400 text-sm">No payment data</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Breakdown Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Detailed Compensation Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 px-3 text-xs font-semibold text-slate-500">Parcel</th>
                  <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">Market Value</th>
                  <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">Solatium (100%)</th>
                  <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">Additional</th>
                  <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">Total Award</th>
                  <th className="text-center py-2 px-3 text-xs font-semibold text-slate-500">Status</th>
                  <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">Disbursed</th>
                </tr>
              </thead>
              <tbody>
                {compensations.map((c: any) => {
                  const parcel = parcelMap[c.parcel_id] || {};
                  const compPayments = payments.filter((p: any) => p.compensation_id === c.id);
                  const disbursed = compPayments
                    .filter((p: any) => p.payment_status === 'disbursed')
                    .reduce((s: number, p: any) => s + (p.amount || 0), 0);
                  return (
                    <tr key={c.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-2.5 px-3">
                        <div className="font-medium text-slate-900">{parcel.survey_number || '—'}</div>
                        <div className="text-xs text-slate-500">{parcel.village_name || '—'}</div>
                      </td>
                      <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(c.market_value || 0)}</td>
                      <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(c.solatium || 0)}</td>
                      <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(c.additional_compensation || 0)}</td>
                      <td className="py-2.5 px-3 text-right font-semibold text-emerald-700 tabular-nums">{formatCurrency(c.total_award || 0)}</td>
                      <td className="py-2.5 px-3 text-center"><StatusBadge status={c.status} /></td>
                      <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(disbursed)}</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-300 font-bold">
                  <td className="py-2.5 px-3">Total ({compensations.length} records)</td>
                  <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(totalMarketValue)}</td>
                  <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(totalSolatium)}</td>
                  <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(compensations.reduce((s: number, c: any) => s + (c.additional_compensation || 0), 0))}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-700 tabular-nums">{formatCurrency(totalAward)}</td>
                  <td />
                  <td className="py-2.5 px-3 text-right tabular-nums">{formatCurrency(totalDisbursed)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Legal Reference */}
      <Card className="bg-indigo-50 border-indigo-200">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚖️</span>
            <div>
              <div className="font-bold text-indigo-900 text-sm">Legal Framework</div>
              <p className="text-xs text-indigo-700 mt-1">
                All compensation assessments follow the Right to Fair Compensation and Transparency in Land Acquisition,
                Rehabilitation and Resettlement Act, 2013 (RFCTLARR). Includes Section 26 market value computation,
                Section 30(1) mandatory 100% solatium, and Section 30(3) additional 12% p.a. market value.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
