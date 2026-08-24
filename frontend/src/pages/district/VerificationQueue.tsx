import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { DataTable, Column } from '../../components/shared/DataTable';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { KPICard } from '../../components/shared/KPICard';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Select } from '../../components/ui/select';
import { formatCurrency } from '../../lib/utils';

interface Parcel {
  id: string;
  project_id: string;
  survey_number: string;
  village_id: string;
  district_id: string;
  state_id: string;
  area_hectares: number | null;
  land_type: string;
  ownership_status: string;
  verification_status: string;
  village_name: string | null;
  district_name: string | null;
  state_name: string | null;
  owners: any[];
  created_at: string;
  updated_at: string;
}

const LAND_TYPE_OPTIONS = [
  { label: 'Agricultural', value: 'agricultural' },
  { label: 'Residential', value: 'residential' },
  { label: 'Commercial', value: 'commercial' },
  { label: 'Forest', value: 'forest' },
  { label: 'Govt', value: 'govt' },
  { label: 'Other', value: 'other' },
];

const STATUS_OPTIONS = [
  { label: 'Pending', value: 'pending' },
  { label: 'Verified', value: 'verified' },
  { label: 'Disputed', value: 'disputed' },
  { label: 'Acquired', value: 'acquired' },
];

export default function VerificationQueue() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [landTypeFilter, setLandTypeFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['verification-queue', page, search, statusFilter, landTypeFilter],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: 20 };
      if (search) params.search = search;
      if (statusFilter) params.verification_status = statusFilter;
      if (landTypeFilter) params.land_type = landTypeFilter;
      const { data } = await api.get('/parcels', { params });
      return data;
    },
  });

  const parcels = data?.items || [];
  const pendingCount = parcels.filter((p: Parcel) => p.verification_status === 'pending').length;
  const verifiedCount = parcels.filter((p: Parcel) => p.verification_status === 'verified').length;
  const disputedCount = parcels.filter((p: Parcel) => p.verification_status === 'disputed').length;
  const totalArea = parcels.reduce((sum: number, p: Parcel) => sum + (p.area_hectares || 0), 0);

  const columns: Column<Parcel>[] = [
    {
      key: 'survey_number',
      header: 'Survey No.',
      render: (item) => (
        <div className="font-medium text-slate-900">{item.survey_number}</div>
      ),
      sortable: true,
    },
    {
      key: 'village_name',
      header: 'Village',
      render: (item) => (
        <div>
          <div className="text-sm text-slate-900">{item.village_name || '—'}</div>
          <div className="text-xs text-slate-500">{item.district_name}</div>
        </div>
      ),
    },
    {
      key: 'area_hectares',
      header: 'Area (ha)',
      render: (item) => (
        <span className="tabular-nums">{item.area_hectares?.toFixed(2) || '—'}</span>
      ),
      sortable: true,
    },
    {
      key: 'land_type',
      header: 'Land Type',
      render: (item) => (
        <span className="text-sm capitalize">{item.land_type?.replace('_', ' ') || '—'}</span>
      ),
    },
    {
      key: 'owners',
      header: 'Owner',
      render: (item) => (
        <span className="text-sm">{item.owners?.[0]?.full_name || '—'}</span>
      ),
    },
    {
      key: 'verification_status',
      header: 'Status',
      render: (item) => <StatusBadge status={item.verification_status} />,
    },
    {
      key: 'actions',
      header: '',
      render: (item) => (
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/district/parcels?id=${item.id}`);
          }}
        >
          Review →
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">✅ Verification Queue</h1>
        <p className="text-slate-500 text-sm">
          Review and verify land parcels pending verification in your district
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard label="Pending Review" value={pendingCount} icon="📝" index={0} />
        <KPICard label="Verified" value={verifiedCount} icon="✅" index={1} />
        <KPICard label="Disputed" value={disputedCount} icon="⚠️" index={2} />
        <KPICard label="Total Area" value={`${totalArea.toFixed(1)} ha`} icon="🗺️" index={3} />
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Verification Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Land Type</label>
              <Select value={landTypeFilter} onValueChange={setLandTypeFilter}>
                <option value="">All Types</option>
                {LAND_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex-1" />
            <span className="text-sm text-slate-500">{data?.total || 0} parcels</span>
          </div>
        </CardContent>
      </Card>

      <DataTable
        columns={columns}
        data={parcels}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        searchPlaceholder="Search by survey number..."
        onSearch={(term) => {
          setSearch(term);
          setPage(1);
        }}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No parcels found for verification"
        onRowClick={(item) => navigate(`/district/parcels?id=${item.id}`)}
      />
    </div>
  );
}
