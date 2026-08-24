import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { NotificationItem } from '../../components/notifications/NotificationItem';

export default function NotificationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const { data } = await api.get('/notifications', { params: { page_size: 50 } });
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton h-16 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Notifications</h1>
      <div className="space-y-2">
        {data?.items?.length === 0 && (
          <div className="text-center py-12 text-slate-400">No notifications yet</div>
        )}
        {data?.items?.map((notif: any, idx: number) => (
          <NotificationItem key={notif.id} notification={notif} index={idx} />
        ))}
      </div>
    </div>
  );
}
