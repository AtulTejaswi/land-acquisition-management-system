import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { Card, CardContent } from '../../components/ui/card';
import { formatDateTime } from '../../lib/utils';
import { motion } from 'framer-motion';

export default function NotificationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const { data } = await api.get('/notifications', { params: { page_size: 50 } });
      return data;
    },
  });

  const typeIcons: Record<string, string> = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    alert: '🚨',
  };

  if (isLoading) {
    return <div className="space-y-3">{[...Array(5)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Notifications</h1>
      <div className="space-y-2">
        {data?.items?.length === 0 && (
          <div className="text-center py-12 text-slate-400">No notifications yet</div>
        )}
        {data?.items?.map((notif: any, idx: number) => (
          <motion.div
            key={notif.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.03 }}
          >
            <Card className={`${!notif.is_read ? 'border-l-4 border-l-primary-500 bg-blue-50/30' : ''}`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <span className="text-lg">{typeIcons[notif.type] || '📢'}</span>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900">{notif.title}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{notif.body}</div>
                    <div className="text-xs text-slate-400 mt-1">{formatDateTime(notif.created_at)}</div>
                  </div>
                  {!notif.is_read && <span className="h-2 w-2 rounded-full bg-primary-500" />}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
