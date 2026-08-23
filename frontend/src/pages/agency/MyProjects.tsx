import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { DataTable, Column } from '../../components/shared/DataTable';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { formatCurrency, formatDate } from '../../lib/utils';

export default function MyProjects() {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ['agency-projects', page],
    queryFn: async () => {
      const { data } = await api.get('/projects', { params: { page, page_size: 20 } });
      return data;
    },
  });

  const columns: Column<any>[] = [
    {
      key: 'name', header: 'Project Name',
      render: (item) => <span className="font-medium text-slate-900">{item.name}</span>,
    },
    { key: 'status', header: 'Status', render: (item) => <StatusBadge status={item.status} /> },
    { key: 'current_stage', header: 'Stage', render: (item) => <span className="text-slate-600">{item.current_stage?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}</span> },
    { key: 'estimated_budget', header: 'Budget', render: (item) => <span className="tabular-nums">{item.estimated_budget ? formatCurrency(Number(item.estimated_budget)) : '—'}</span> },
    { key: 'created_at', header: 'Created', render: (item) => formatDate(item.created_at) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">My Projects</h1>
          <p className="text-slate-500 text-sm">Projects assigned to your agency</p>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        isLoading={isLoading}
        emptyMessage="No projects found"
        onRowClick={(item) => navigate(`/agency/projects/${item.id}`)}
      />
    </div>
  );
}
