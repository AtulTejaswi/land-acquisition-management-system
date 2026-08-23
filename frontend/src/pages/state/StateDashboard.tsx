import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../store/AuthContext';
import api from '../../services/api';
import { KPICard } from '../../components/shared/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { motion } from 'framer-motion';

export default function StateDashboard() {
  const { user } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ['state-dashboard', user?.state_id],
    queryFn: async () => {
      const { data } = await api.get(`/dashboard/state/${user?.state_id}`);
      return data;
    },
    enabled: !!user?.state_id,
  });

  if (isLoading) {
    return <div className="space-y-4">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}</div>;
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">State Dashboard</h1>
        <p className="text-slate-500 text-sm">Land acquisition overview for your state</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data?.kpis?.map((kpi: any, i: number) => (
          <KPICard key={i} label={kpi.label} value={kpi.value} icon={kpi.icon} index={i} />
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>District-wise Progress</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {data?.district_progress?.map((dp: any) => (
              <div key={dp.district_id} className="border border-slate-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
                <div className="font-medium text-slate-900">{dp.district_name}</div>
                <div className="text-sm text-slate-500">{dp.total_projects} projects</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
