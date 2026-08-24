import React from 'react';
import { Card, CardContent } from '../ui/card';
import { formatDateTime } from '../../lib/utils';
import { motion } from 'framer-motion';

const TYPE_ICONS: Record<string, string> = {
  info: 'ℹ️',
  success: '✅',
  warning: '⚠️',
  alert: '🚨',
};

interface NotificationItemProps {
  notification: {
    id: string;
    type: string;
    title: string;
    body: string;
    is_read: boolean;
    created_at: string;
  };
  index: number;
}

export function NotificationItem({ notification, index }: NotificationItemProps) {
  return (
    <motion.div
      key={notification.id}
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
    >
      <Card
        className={`${!notification.is_read ? 'border-l-4 border-l-primary-500 bg-blue-50/30' : ''}`}
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <span className="text-lg">{TYPE_ICONS[notification.type] || '📢'}</span>
            <div className="flex-1">
              <div className="text-sm font-medium text-slate-900">{notification.title}</div>
              <div className="text-xs text-slate-500 mt-0.5">{notification.body}</div>
              <div className="text-xs text-slate-400 mt-1">
                {formatDateTime(notification.created_at)}
              </div>
            </div>
            {!notification.is_read && (
              <span className="h-2 w-2 rounded-full bg-primary-500" />
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
