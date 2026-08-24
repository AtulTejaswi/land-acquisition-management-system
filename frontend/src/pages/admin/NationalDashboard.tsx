import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { KPICard } from '../../components/shared/KPICard';
import { TrendChart } from '../../components/dashboard/TrendChart';
import { HeatmapIndia } from '../../components/dashboard/HeatmapIndia';

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
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">National Dashboard</h1>
        <p className="text-slate-500 text-sm">
          Overview of all land acquisition projects across India
        </p>
      </motion.div>

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

      <TrendChart statusData={statusData} priorityData={priorityData} />

      <HeatmapIndia stateProgress={stateProgress} />
    </div>
  );
}
