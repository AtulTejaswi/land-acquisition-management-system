import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useAuth } from '../../store/AuthContext';
import api from '../../services/api';
import { DataTable, Column } from '../../components/shared/DataTable';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { KPICard } from '../../components/shared/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { EmptyState } from '../../components/shared/EmptyState';
import { formatCurrency, formatDate } from '../../lib/utils';

interface CompensationItem {
  id: string;
  parcel_id: string;
  market_value: number | null;
  solatium: number | null;
  additional_compensation: number | null;
  total_award: number | null;
  assessed_by: string | null;
  assessment_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

const STATUS_OPTIONS = [
  { label: 'Draft', value: 'draft' },
  { label: 'Assessed', value: 'assessed' },
  { label: 'Approved', value: 'approved' },
  { label: 'Disputed', value: 'disputed' },
];

export default function CompensationDesk() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedComp, setSelectedComp] = useState<CompensationItem | null>(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionType, setActionType] = useState<'approve' | 'dispute'>('approve');
  const [remarks, setRemarks] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['compensation-desk', page, search, statusFilter],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: 20 };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const { data } = await api.get('/compensation', { params });
      return data;
    },
  });

  // Fetch parcels for enriched info
  const { data: parcelsData } = useQuery({
    queryKey: ['compensation-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/parcels', { params: { page_size: 100 } });
      return data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const { data } = await api.patch(`/compensation/${id}`, { status });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compensation-desk'] });
      setShowActionModal(false);
      setSelectedComp(null);
      setRemarks('');
    },
  });

  // Create payment mutation
  const createPaymentMutation = useMutation({
    mutationFn: async (comp: CompensationItem) => {
      // Create payment for the first owner of the parcel
      const parcelResp = await api.get(`/parcels/${comp.parcel_id}`);
      const owners = parcelResp.data.owners || [];
      if (owners.length > 0) {
        await api.post('/payments', {
          compensation_id: comp.id,
          land_owner_id: owners[0].id,
          amount: comp.total_award || 0,
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compensation-desk'] });
    },
  });

  const handleAction = () => {
    if (!selectedComp) return;
    if (actionType === 'approve') {
      updateMutation.mutate({ id: selectedComp.id, status: 'approved' });
    } else {
      updateMutation.mutate({ id: selectedComp.id, status: 'disputed' });
    }
  };

  const openActionModal = (comp: CompensationItem, type: 'approve' | 'dispute') => {
    setSelectedComp(comp);
    setActionType(type);
    setShowActionModal(true);
  };

  // Build parcel lookup for enriched display
  const parcelMap: Record<string, any> = {};
  if (parcelsData?.items) {
    for (const p of parcelsData.items) {
      parcelMap[p.id] = p;
    }
  }

  const columns: Column<CompensationItem>[] = [
    {
      key: 'parcel_id',
      header: 'Parcel / Survey',
      render: (item) => {
        const parcel = parcelMap[item.parcel_id];
        return (
          <div>
            <div className="text-sm font-medium text-slate-900">
              {parcel?.survey_number || '—'}
            </div>
            <div className="text-xs text-slate-500">
              {parcel?.village_name || '—'}
            </div>
          </div>
        );
      },
      sortable: true,
    },
    {
      key: 'market_value',
      header: 'Market Value',
      render: (item) => (
        <span className="tabular-nums">{formatCurrency(item.market_value || 0)}</span>
      ),
      sortable: true,
    },
    {
      key: 'total_award',
      header: 'Total Award',
      render: (item) => (
        <span className="tabular-nums font-semibold text-emerald-700">
          {formatCurrency(item.total_award || 0)}
        </span>
      ),
      sortable: true,
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <StatusBadge status={item.status} />,
    },
    {
      key: 'assessment_date',
      header: 'Assessed',
      render: (item) => formatDate(item.assessment_date),
    },
    {
      key: 'actions',
      header: '',
      render: (item) => (
        <div className="flex gap-1">
          {item.status === 'assessed' && (
            <>
              <Button
                variant="outline"
                size="sm"
                className="text-emerald-600 border-emerald-300 hover:bg-emerald-50"
                onClick={(e) => {
                  e.stopPropagation();
                  openActionModal(item, 'approve');
                }}
              >
                ✅ Approve
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-red-600 border-red-300 hover:bg-red-50"
                onClick={(e) => {
                  e.stopPropagation();
                  openActionModal(item, 'dispute');
                }}
              >
                ❌ Dispute
              </Button>
            </>
          )}
          {item.status === 'approved' && (
            <Button
              variant="outline"
              size="sm"
              className="text-blue-600 border-blue-300 hover:bg-blue-50"
              onClick={(e) => {
                e.stopPropagation();
                createPaymentMutation.mutate(item);
              }}
            >
              💰 Disburse
            </Button>
          )}
        </div>
      ),
    },
  ];

  // KPI summary
  const compensations = data?.items || [];
  const totalAward = compensations.reduce((sum: number, c: CompensationItem) => sum + (c.total_award || 0), 0);
  const pendingCount = compensations.filter((c: CompensationItem) => c.status === 'assessed').length;
  const approvedCount = compensations.filter((c: CompensationItem) => c.status === 'approved').length;
  const disputedCount = compensations.filter((c: CompensationItem) => c.status === 'disputed').length;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">💰 Compensation Desk</h1>
        <p className="text-slate-500 text-sm">
          Assess, approve, and disburse compensation for land acquisition
        </p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard label="Pending Assessment" value={pendingCount} icon="📝" index={0} />
        <KPICard label="Approved" value={approvedCount} icon="✅" index={1} />
        <KPICard label="Disputed" value={disputedCount} icon="⚠️" index={2} />
        <KPICard label="Total Award Value" value={formatCurrency(totalAward)} icon="💰" index={3} />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex-1" />
            <span className="text-sm text-slate-500">
              {data?.total || 0} compensation records
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <DataTable
        columns={columns}
        data={compensations}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        searchPlaceholder="Search by parcel ID..."
        onSearch={(term) => {
          setSearch(term);
          setPage(1);
        }}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No compensation records found"
        onRowClick={(item) => setSelectedComp(item)}
      />

      {/* Action Modal */}
      {showActionModal && selectedComp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-bold text-slate-900 mb-4">
              {actionType === 'approve' ? '✅ Approve Compensation' : '❌ Dispute Compensation'}
            </h3>
            <div className="space-y-3">
              <div className="text-sm text-slate-600">
                <strong>Total Award:</strong>{' '}
                <span className="tabular-nums">{formatCurrency(selectedComp.total_award || 0)}</span>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Remarks</label>
                <Input
                  placeholder="Enter remarks..."
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setShowActionModal(false)}>
                Cancel
              </Button>
              <Button
                variant={actionType === 'approve' ? 'default' : 'destructive'}
                onClick={handleAction}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Processing...' : actionType === 'approve' ? 'Approve' : 'Dispute'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Detail Sidebar */}
      {selectedComp && !showActionModal && (
        <div className="fixed inset-y-0 right-0 z-50 w-96 bg-white border-l border-slate-200 shadow-2xl overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900">Compensation Details</h3>
              <button
                onClick={() => setSelectedComp(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-500">Parcel</label>
                <p className="text-sm text-slate-900">
                  {parcelMap[selectedComp.parcel_id]?.survey_number || '—'}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Market Value</label>
                <p className="text-sm text-slate-900 tabular-nums">
                  {formatCurrency(selectedComp.market_value || 0)}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Solatium (100%)</label>
                <p className="text-sm text-slate-900 tabular-nums">
                  {formatCurrency(selectedComp.solatium || 0)}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Additional Compensation</label>
                <p className="text-sm text-slate-900 tabular-nums">
                  {formatCurrency(selectedComp.additional_compensation || 0)}
                </p>
              </div>
              <div className="border-t pt-3">
                <label className="text-xs font-medium text-slate-500">Total Award</label>
                <p className="text-lg font-bold text-emerald-700 tabular-nums">
                  {formatCurrency(selectedComp.total_award || 0)}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Status</label>
                <div className="mt-1">
                  <StatusBadge status={selectedComp.status} />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Assessment Date</label>
                <p className="text-sm text-slate-900">
                  {formatDate(selectedComp.assessment_date)}
                </p>
              </div>
              {selectedComp.status === 'assessed' && (
                <div className="flex gap-2 pt-4">
                  <Button
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => openActionModal(selectedComp, 'approve')}
                  >
                    ✅ Approve
                  </Button>
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={() => openActionModal(selectedComp, 'dispute')}
                  >
                    ❌ Dispute
                  </Button>
                </div>
              )}
              {selectedComp.status === 'approved' && (
                <Button
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  onClick={() => createPaymentMutation.mutate(selectedComp)}
                >
                  💰 Disburse Payment
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
