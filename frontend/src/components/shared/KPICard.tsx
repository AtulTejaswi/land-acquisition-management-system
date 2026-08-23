import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '../ui/card';
import { cn } from '@/lib/utils';

interface KPICardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: string;
  index?: number;
}

export function KPICard({ label, value, change, changeLabel, icon, index = 0 }: KPICardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
    >
      <Card className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="text-2xl font-bold text-slate-900 tabular-nums">{value}</p>
          </div>
          {icon && (
            <div className="rounded-lg bg-primary-50 p-2">
              <svg className="h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          )}
        </div>
        {change !== undefined && (
          <div className="mt-2 flex items-center gap-1">
            <span className={cn('text-xs font-medium', change >= 0 ? 'text-emerald-600' : 'text-red-600')}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
            </span>
            {changeLabel && <span className="text-xs text-slate-400">{changeLabel}</span>}
          </div>
        )}
      </Card>
    </motion.div>
  );
}
