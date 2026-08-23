import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { DataTable, Column } from '../../components/shared/DataTable';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { formatCurrency, formatDate } from '../../lib/utils';

export default function ProjectList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ['projects', page, search, statusFilter],
    queryFn: async () => {
      const params: any = { page, page_size: 20 };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const { data } = await api.get('/projects', { params });
      return data;
    },
  });

  const columns: Column<any>[] = [
    {
      key: 'name', header: 'Project Name', sortable: true,
      render: (item) => <span className="font-medium text-slate-900">{item.name}</span>,
    },
    {
      key: 'status', header: 'Status',
      render: (item) => <StatusBadge status={item.status} />,
    },
    {
      key: 'priority', header: 'Priority',
      render: (item) => <StatusBadge status={item.priority} type="priority" />,
    },
    {
      key: 'current_stage', header: 'Current Stage',
      render: (item) => <span className="text-slate-600">{item.current_stage?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}</span>,
    },
    {
      key: 'estimated_budget', header: 'Budget', sortable: true,
      render: (item) => <span className="tabular-nums">{item.estimated_budget ? formatCurrency(Number(item.estimated_budget)) : '—'}</span>,
    },
    {
      key: 'state_name', header: 'State',
      render: (item) => item.state_name || '—',
    },
    {
      key: 'created_at', header: 'Created', sortable: true,
      render: (item) => formatDate(item.created_at),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
        <p className="text-slate-500 text-sm">Manage and track all land acquisition projects</p>
      </div>

      <div className="flex gap-3 items-center">
        <select
          className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="submitted">Submitted</option>
          <option value="under_review">Under Review</option>
          <option value="approved">Approved</option>
          <option value="active">Active</option>
          <option value="delayed">Delayed</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        searchPlaceholder="Search projects..."
        onSearch={(s) => { setSearch(s); setPage(1); }}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No projects found"
        onRowClick={(item) => navigate(`/admin/projects/${item.id}`)}
      />
    </div>
  );
}
