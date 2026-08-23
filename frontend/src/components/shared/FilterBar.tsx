import React from 'react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Select } from '../ui/select';

export interface FilterConfig {
  key: string;
  label: string;
  type: 'text' | 'select';
  placeholder?: string;
  options?: { label: string; value: string }[];
  value: string;
}

interface FilterBarProps {
  filters: FilterConfig[];
  onFilterChange: (key: string, value: string) => void;
  onReset: () => void;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
  onSortChange?: (field: string) => void;
}

export function FilterBar({ filters, onFilterChange, onReset }: FilterBarProps) {
  const hasActiveFilters = filters.some((f) => f.value && f.value !== '');

  return (
    <div className="flex flex-wrap items-end gap-3 p-4 bg-white border border-slate-200 rounded-xl">
      {filters.map((filter) => (
        <div key={filter.key} className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">{filter.label}</label>
          {filter.type === 'select' ? (
            <Select
              value={filter.value}
              onValueChange={(v) => onFilterChange(filter.key, v)}
            >
              <option value="">All</option>
              {filter.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </Select>
          ) : (
            <Input
              placeholder={filter.placeholder || `Search ${filter.label.toLowerCase()}...`}
              value={filter.value}
              onChange={(e) => onFilterChange(filter.key, e.target.value)}
              className="w-60"
            />
          )}
        </div>
      ))}
      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={onReset}>
          ✕ Clear Filters
        </Button>
      )}
    </div>
  );
}
