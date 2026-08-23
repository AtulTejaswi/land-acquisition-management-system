import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { KPICard } from '../../components/shared/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { formatCurrency } from '../../lib/utils';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

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

  const statusData = data?.charts?.[0]?.data || [];
  const priorityData = data?.charts?.[1]?.data || [];
  const stateProgress = data?.state_progress || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">National Dashboard</h1>
        <p className="text-slate-500 text-sm">Overview of all land acquisition projects across India</p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data?.kpis?.map((kpi: any, i: number) => (
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

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Projects by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {statusData.map((_: any, idx: number) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects by Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {priorityData.map((_: any, idx: number) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* India Heatmap (State Progress) */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>🇮🇳 India Heatmap — State-wise Acquisition Progress</CardTitle>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-semibold">AI Insights • Beta</span>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {stateProgress.map((sp: any) => (
              <Link
                key={sp.state_id}
                to={`/state/dashboard`}
                className="group rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all hover:border-primary-300"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-900">{sp.state_name}</span>
                  <span className="text-xs text-slate-400">{sp.code}</span>
                </div>
                <div className="text-2xl font-bold tabular-nums text-slate-900">{sp.total_projects}</div>
                <div className="text-xs text-slate-500">{sp.completed} completed</div>
                <div className="mt-2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.min(sp.progress_pct, 100)}%`,
                      backgroundColor: sp.progress_pct > 50 ? '#10B981' : sp.progress_pct > 20 ? '#F59E0B' : '#94A3B8',
                    }}
                  />
                </div>
                <div className="text-xs text-slate-400 mt-1">{sp.progress_pct}% progress</div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
