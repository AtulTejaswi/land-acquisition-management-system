import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Input } from '../ui/input';
import { Button } from '../ui/button';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  total?: number;
  page?: number;
  pageSize?: number;
  searchPlaceholder?: string;
  onSearch?: (term: string) => void;
  onPageChange?: (page: number) => void;
  onSort?: (key: string, dir: 'asc' | 'desc') => void;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
  actions?: (item: T) => React.ReactNode;
}

export function DataTable<T extends Record<string, any>>({
  columns, data, total = 0, page = 1, pageSize = 20,
  searchPlaceholder = 'Search...', onSearch, onPageChange, onSort,
  isLoading, emptyMessage = 'No data found', onRowClick, actions,
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const totalPages = Math.ceil(total / pageSize);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(searchTerm);
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton h-14 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {onSearch && (
        <form onSubmit={handleSearch} className="flex gap-2">
          <Input
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
          <Button type="submit" variant="outline" size="sm">Search</Button>
        </form>
      )}
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={cn(
                      'px-4 py-3 text-left font-medium text-slate-600',
                      col.sortable && 'cursor-pointer hover:text-slate-900 select-none',
                      col.className,
                    )}
                    onClick={() => col.sortable && onSort?.(col.key, 'asc')}
                  >
                    <div className="flex items-center gap-1">
                      {col.header}
                      {col.sortable && <span className="text-slate-400">↕</span>}
                    </div>
                  </th>
                ))}
                {actions && <th className="px-4 py-3 text-right font-medium text-slate-600">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {data.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + (actions ? 1 : 0)} className="px-4 py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-2">
                      <svg className="h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                      <span>{emptyMessage}</span>
                    </div>
                  </td>
                </tr>
              ) : (
                data.map((item, idx) => (
                  <tr
                    key={idx}
                    className={cn(
                      'border-b border-slate-100 hover:bg-slate-50 transition-colors',
                      onRowClick && 'cursor-pointer',
                    )}
                    onClick={() => onRowClick?.(item)}
                  >
                    {columns.map((col) => (
                      <td key={col.key} className={cn('px-4 py-3', col.className)}>
                        {col.render ? col.render(item) : item[col.key]}
                      </td>
                    ))}
                    {actions && (
                      <td className="px-4 py-3 text-right">{actions(item)}</td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">
            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
          </span>
          <div className="flex gap-1">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPageChange?.(page - 1)}>
              Previous
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => onPageChange?.(page + 1)}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
