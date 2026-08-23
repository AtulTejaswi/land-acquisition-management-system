import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { DataTable, Column } from '../../components/shared/DataTable';
import { Badge } from '../../components/ui/badge';

export default function UserManagement() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['users', page, search, roleFilter],
    queryFn: async () => {
      const params: any = { page, page_size: 50 };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      const { data } = await api.get('/users', { params });
      return data;
    },
  });

  const roleBadges: Record<string, string> = {
    super_admin: 'danger',
    state_authority: 'warning',
    district_officer: 'secondary',
    agency: 'default',
    field_officer: 'success',
    citizen: 'outline',
  };

  const columns: Column<any>[] = [
    {
      key: 'full_name', header: 'Name',
      render: (item) => <span className="font-medium text-slate-900">{item.full_name}</span>,
    },
    { key: 'email', header: 'Email' },
    { key: 'phone', header: 'Phone' },
    {
      key: 'role_name', header: 'Role',
      render: (item) => <Badge variant={roleBadges[item.role_name] as any || 'default'}>{item.role_name?.replace(/_/g, ' ').toUpperCase()}</Badge>,
    },
    {
      key: 'is_active', header: 'Status',
      render: (item) => (
        <span className={`text-xs font-medium ${item.is_active ? 'text-emerald-600' : 'text-red-600'}`}>
          {item.is_active ? '● Active' : '● Inactive'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
        <p className="text-slate-500 text-sm">Manage platform users and roles</p>
      </div>

      <div className="flex gap-3">
        <select
          className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm"
          value={roleFilter}
          onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Roles</option>
          <option value="super_admin">Super Admin</option>
          <option value="state_authority">State Authority</option>
          <option value="district_officer">District Officer</option>
          <option value="agency">Agency</option>
          <option value="field_officer">Field Officer</option>
          <option value="citizen">Citizen</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={Array.isArray(data) ? data : []}
        total={Array.isArray(data) ? data.length : 0}
        page={page}
        pageSize={50}
        searchPlaceholder="Search users..."
        onSearch={(s) => { setSearch(s); setPage(1); }}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No users found"
      />
    </div>
  );
}
