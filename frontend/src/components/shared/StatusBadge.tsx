import React from 'react';
import { getStatusColor, getPriorityColor } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'priority';
}

export function StatusBadge({ status, type = 'status' }: StatusBadgeProps) {
  const className = type === 'priority' ? getPriorityColor(status) : getStatusColor(status);
  const label = status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${className}`}>
      {label}
    </span>
  );
}
