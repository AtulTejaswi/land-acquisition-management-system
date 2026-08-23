import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../store/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

export default function MobileProfile() {
  const { user } = useAuth();

  const info = [
    { label: 'Full Name', value: user?.full_name || '—' },
    { label: 'Email', value: user?.email || '—' },
    { label: 'Phone', value: user?.phone || '—' },
    { label: 'Role', value: 'Field Officer' },
    { label: 'State', value: user?.state_name || '—' },
    { label: 'District', value: user?.district_name || '—' },
  ];

  return (
    <div className="max-w-md mx-auto space-y-4 pb-20">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-xl font-bold text-slate-900">👤 Profile</h1>
      </motion.div>

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col items-center mb-6">
            <div className="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center text-3xl font-bold text-primary-600">
              {user?.full_name?.charAt(0) || 'F'}
            </div>
            <h2 className="text-lg font-bold text-slate-900 mt-3">{user?.full_name}</h2>
            <span className="text-xs text-slate-500 mt-1">Field Officer</span>
          </div>

          <div className="space-y-3">
            {info.map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <span className="text-sm text-slate-500">{item.label}</span>
                <span className="text-sm font-medium text-slate-900">{item.value}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Button variant="outline" className="w-full">Edit Profile</Button>
    </div>
  );
}
