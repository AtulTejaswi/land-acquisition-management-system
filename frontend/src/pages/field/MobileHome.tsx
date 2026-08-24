import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { Card, CardContent } from '../../components/ui/card';
import { useAuth } from '../../store/AuthContext';

export default function MobileHome() {
  const { user } = useAuth();

  const { data: surveys } = useQuery({
    queryKey: ['field-surveys-count'],
    queryFn: async () => {
      const { data } = await api.get('/surveys');
      return data;
    },
  });

  const { data: parcels } = useQuery({
    queryKey: ['field-assigned-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/parcels', { params: { page_size: 50 } });
      return data;
    },
  });

  const completedSurveys = surveys?.filter((s: any) => s.status === 'completed')?.length || 0;
  const pendingSurveys = surveys?.filter((s: any) => s.status === 'scheduled')?.length || 0;

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } },
  };

  const item = {
    hidden: { opacity: 0, y: 8 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <div className="max-w-md mx-auto space-y-4 pb-20">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-xl font-bold text-slate-900">🏠 Home</h1>
        <p className="text-sm text-slate-500">Welcome, {user?.full_name}</p>
      </motion.div>

      {/* Quick Stats */}
      <motion.div className="grid grid-cols-2 gap-3" variants={container} initial="hidden" animate="show">
        <motion.div variants={item}>
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-700 tabular-nums">{surveys?.length || 0}</div>
              <div className="text-xs text-blue-600 font-medium">Total Surveys</div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={item}>
          <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 border-emerald-200">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-emerald-700 tabular-nums">{completedSurveys}</div>
              <div className="text-xs text-emerald-600 font-medium">Completed</div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={item}>
          <Card className="bg-gradient-to-br from-amber-50 to-amber-100/50 border-amber-200">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-amber-700 tabular-nums">{pendingSurveys}</div>
              <div className="text-xs text-amber-600 font-medium">Pending</div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={item}>
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100/50 border-purple-200">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-700 tabular-nums">{parcels?.total || 0}</div>
              <div className="text-xs text-purple-600 font-medium">Assigned Parcels</div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Quick Actions */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <Link to="/field/surveys" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]">
            <span className="text-xl">📋</span>
            <div>
              <div className="text-sm font-medium text-slate-900">My Surveys</div>
              <div className="text-xs text-slate-500">View and manage field surveys</div>
            </div>
          </Link>
          <Link to="/field/camera" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]">
            <span className="text-xl">📸</span>
            <div>
              <div className="text-sm font-medium text-slate-900">Camera</div>
              <div className="text-xs text-slate-500">Capture geo-tagged photos</div>
            </div>
          </Link>
          <Link to="/field/profile" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors min-h-[44px]">
            <span className="text-xl">👤</span>
            <div>
              <div className="text-sm font-medium text-slate-900">My Profile</div>
              <div className="text-xs text-slate-500">View your details and assignments</div>
            </div>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
