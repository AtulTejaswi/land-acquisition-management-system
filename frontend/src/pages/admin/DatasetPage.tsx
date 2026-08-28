import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';

const TABLE_META: Record<string, { icon: string; label: string; color: string }> = {
  projects: { icon: '📁', label: 'Projects', color: 'bg-blue-50 border-blue-200 text-blue-700' },
  parcels: { icon: '🗺️', label: 'Land Parcels', color: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
  users: { icon: '👥', label: 'Users', color: 'bg-violet-50 border-violet-200 text-violet-700' },
  compensations: { icon: '💰', label: 'Compensations', color: 'bg-amber-50 border-amber-200 text-amber-700' },
  payments: { icon: '🏦', label: 'Payments', color: 'bg-green-50 border-green-200 text-green-700' },
  states: { icon: '🗺️', label: 'States', color: 'bg-rose-50 border-rose-200 text-rose-700' },
  districts: { icon: '🏘️', label: 'Districts', color: 'bg-orange-50 border-orange-200 text-orange-700' },
  villages: { icon: '🏡', label: 'Villages', color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
  ministries: { icon: '🏛️', label: 'Ministries', color: 'bg-indigo-50 border-indigo-200 text-indigo-700' },
  categories: { icon: '🏷️', label: 'Categories', color: 'bg-pink-50 border-pink-200 text-pink-700' },
  documents: { icon: '📄', label: 'Documents', color: 'bg-cyan-50 border-cyan-200 text-cyan-700' },
  land_owners: { icon: '👤', label: 'Land Owners', color: 'bg-teal-50 border-teal-200 text-teal-700' },
  rr_families: { icon: '🏘️', label: 'R&R Families', color: 'bg-purple-50 border-purple-200 text-purple-700' },
  roles: { icon: '🔐', label: 'Roles', color: 'bg-slate-50 border-slate-200 text-slate-700' },
};

function formatValue(key: string, value: any): string {
  if (value === null || value === undefined) return '—';
  if (key.includes('date') || key === 'created_at' || key === 'updated_at' || key === 'last_login_at') {
    return value ? new Date(value).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';
  }
  if (key.includes('amount') || key.includes('value') || key.includes('budget') || key === 'total_award' || key === 'solatium' || key === 'market_value' || key === 'additional_compensation' || key === 'monetary_benefit_amount') {
    return typeof value === 'number' ? `₹${value.toLocaleString('en-IN')}` : String(value);
  }
  if (key === 'area_hectares') {
    return typeof value === 'number' ? `${value} ha` : String(value);
  }
  if (key === 'share_percentage') {
    return typeof value === 'number' ? `${value}%` : String(value);
  }
  if (key === 'progress_percentage') {
    return typeof value === 'number' ? `${value}%` : String(value);
  }
  if (typeof value === 'boolean') return value ? '✅ Yes' : '❌ No';
  return String(value);
}

function capitalize(s: string) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function DatasetPage() {
  const [activeTable, setActiveTable] = useState('projects');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const pageSize = 25;

  const { data: summary } = useQuery({
    queryKey: ['dataset-summary'],
    queryFn: async () => {
      const { data } = await api.get('/datasets/summary');
      return data;
    },
  });

  const { data, isLoading } = useQuery({
    queryKey: ['dataset', activeTable, page, search],
    queryFn: async () => {
      const params: Record<string, any> = { table: activeTable, page, page_size: pageSize };
      if (search) params.search = search;
      const { data } = await api.get('/datasets', { params });
      return data;
    },
  });

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize);
  const columns = items.length > 0 ? Object.keys(items[0]) : [];

  const handleTableChange = (table: string) => {
    setActiveTable(table);
    setPage(1);
    setSearch('');
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">📦 Dataset Browser</h1>
        <p className="text-slate-500 text-sm">
          Browse all raw data tables in the NLAMS database
        </p>
      </motion.div>

      {/* Table summary cards */}
      {summary?.tables && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-7 gap-2">
          {Object.entries(summary.tables).map(([tableName, count]) => {
            const meta = TABLE_META[tableName] || { icon: '📋', label: tableName, color: 'bg-slate-50 border-slate-200 text-slate-700' };
            return (
              <button
                key={tableName}
                onClick={() => handleTableChange(tableName)}
                className={`p-3 rounded-xl border-2 text-left transition-all ${
                  activeTable === tableName
                    ? 'ring-2 ring-primary-400 border-primary-400 bg-primary-50 shadow-md'
                    : `${meta.color} hover:shadow-md`
                }`}
              >
                <div className="text-lg">{meta.icon}</div>
                <div className="text-xs font-semibold mt-1 truncate">{meta.label}</div>
                <div className="text-lg font-bold">{count as number}</div>
              </button>
            );
          })}
        </div>
      )}

      {/* Table data */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              {TABLE_META[activeTable]?.icon} {TABLE_META[activeTable]?.label || activeTable}
              <span className="text-sm font-normal text-slate-500 ml-2">({total} rows)</span>
            </CardTitle>
            <div className="flex items-center gap-2">
              <Input
                placeholder="Search..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-64 text-sm"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton h-10 rounded" />
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <div className="text-3xl mb-2">📭</div>
              <p className="text-sm">No data found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="text-left py-2 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap"
                      >
                        {capitalize(col)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {items.map((row: any, idx: number) => (
                    <tr
                      key={row.id || idx}
                      className="border-b border-slate-50 hover:bg-slate-50 transition-colors"
                    >
                      {columns.map((col) => (
                        <td key={col} className="py-2.5 px-3 text-slate-700 whitespace-nowrap max-w-[250px] truncate">
                          {formatValue(col, row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100">
              <span className="text-xs text-slate-500">
                Page {page} of {totalPages} • Showing {items.length} of {total} rows
              </span>
              <div className="flex gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(1)}
                >
                  ««
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  « Prev
                </Button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const start = Math.max(1, Math.min(page - 2, totalPages - 4));
                  const p = start + i;
                  if (p > totalPages) return null;
                  return (
                    <Button
                      key={p}
                      variant={p === page ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPage(p)}
                    >
                      {p}
                    </Button>
                  );
                })}
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                >
                  Next »
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage(totalPages)}
                >
                  »»
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
