import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { KPICard } from '../../components/shared/KPICard';
import { Bar, PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const PIE_COLORS = ['#F97316', '#8B5CF6', '#10B981', '#F59E0B', '#3B82F6'];

export default function NationalDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['national-dashboard'],
    queryFn: async () => {
      const { data } = await api.get('/dashboard/national');
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="skeleton h-80 rounded-xl" />
          <div className="skeleton h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  const kpis = data?.kpis || [];
  const charts = data?.charts || [];
  const stateProgress = data?.state_progress || [];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">National Dashboard</h1>
        <p className="text-slate-500 text-sm">
          Odisha, Khordha District — 1 state onboarded with real bhoomirashi land-record data
        </p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi: any, i: number) => (
          <KPICard
            key={i}
            label={kpi.label}
            value={kpi.value}
            change={kpi.change}
            changeLabel={kpi.change_label}
            icon={kpi.icon}
            index={i}
          />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Parcels by Village */}
        {charts[0] && (
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-base font-semibold text-slate-900 mb-4">{charts[0].title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <Bar data={charts[0].data} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </Bar>
            </ResponsiveContainer>
          </div>
        )}

        {/* Ownership Split */}
        {charts[1] && (
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-base font-semibold text-slate-900 mb-4">{charts[1].title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={charts[1].data}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {charts[1].data.map((_: any, i: number) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Land Type Distribution */}
        {charts[2] && (
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-base font-semibold text-slate-900 mb-4">{charts[2].title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={charts[2].data}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {charts[2].data.map((_: any, i: number) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Co-ownership Distribution */}
        {charts[3] && (
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-base font-semibold text-slate-900 mb-4">{charts[3].title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <Bar data={charts[3].data} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
                <Tooltip />
                <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </Bar>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* State overview card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-900">
            🇮🇳 Onboarded States
          </h3>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-semibold">
            Real Data
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {stateProgress.map((sp: any) => (
            <div
              key={sp.state_id}
              className="rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all hover:border-blue-300"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-900">{sp.state_name}</span>
                <span className="text-xs text-slate-400">{sp.code}</span>
              </div>
              <div className="text-2xl font-bold tabular-nums text-slate-900">
                {sp.total_projects}
              </div>
              <div className="text-xs text-slate-500">parcels imported</div>
              <div className="mt-2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all bg-green-500"
                  style={{ width: `${sp.progress_pct}%` }}
                />
              </div>
              <div className="text-xs text-slate-400 mt-1">{sp.progress_pct}% complete</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
