import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../store/AuthContext';
import api from '../../services/api';
import { KPICard } from '../../components/shared/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { motion } from 'framer-motion';

export default function DistrictDashboard() {
  const { user } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ['district-dashboard', user?.district_id],
    queryFn: async () => {
      const { data } = await api.get(`/dashboard/district/${user?.district_id}`);
      return data;
    },
    enabled: !!user?.district_id,
  });

  if (isLoading) {
    return <div className="space-y-4">{[...Array(3)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}</div>;
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">District Dashboard</h1>
        <p className="text-slate-500 text-sm">Land acquisition overview for your district</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data?.kpis?.map((kpi: any, i: number) => (
          <KPICard key={i} label={kpi.label} value={kpi.value} icon={kpi.icon} index={i} />
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Recent Projects</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data?.recent_projects?.map((proj: any) => (
              <div key={proj.id} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:shadow-sm">
                <div className="font-medium text-slate-900">{proj.name}</div>
                <StatusBadge status={proj.status} />
              </div>
            ))}
            {data?.recent_projects?.length === 0 && (
              <p className="text-slate-400 text-center py-6">No projects in your district</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
