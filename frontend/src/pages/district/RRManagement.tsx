import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
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

interface RRFamily {
  id: string;
  project_id: string;
  family_head_name: string;
  family_id_number: string | null;
  member_count: number | null;
  displaced_status: string;
  housing_benefit_status: string;
  employment_benefit_status: string;
  monetary_benefit_amount: number | null;
  current_stage: string;
  progress_percentage: number | null;
  created_at: string;
  updated_at: string;
}

const DISPLACED_OPTIONS = [
  { label: 'Fully Displaced', value: 'fully' },
  { label: 'Partially Displaced', value: 'partially' },
  { label: 'Not Displaced', value: 'not_displaced' },
];

const STAGE_OPTIONS = [
  { label: 'Identification', value: 'identification' },
  { label: 'Verification', value: 'verification' },
  { label: 'Benefit Disbursement', value: 'benefit_disbursement' },
  { label: 'Resettled', value: 'resettled' },
];

export default function RRManagement() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [displacedFilter, setDisplacedFilter] = useState('');
  const [selectedFamily, setSelectedFamily] = useState<RRFamily | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['rr-families', page, search, stageFilter, displacedFilter],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: 20 };
      if (stageFilter) params.current_stage = stageFilter;
      if (displacedFilter) params.displaced_status = displacedFilter;
      const { data } = await api.get('/rr/families', { params });
      return data;
    },
  });

  const { data: summaryData } = useQuery({
    queryKey: ['rr-summary'],
    queryFn: async () => {
      const { data } = await api.get('/rr/summary');
      return data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: Partial<RRFamily> }) => {
      const { data } = await api.patch(`/rr/families/${id}`, updates);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rr-families'] });
      queryClient.invalidateQueries({ queryKey: ['rr-summary'] });
      setShowEditModal(false);
      setSelectedFamily(null);
    },
  });

  const families = data?.items || [];
  const summary = summaryData || [];

  // KPIs from summary
  const totalFamilies = summary.reduce((s: number, r: any) => s + r.total_families, 0);
  const resettledCount = summary.reduce((s: number, r: any) => s + r.resettled, 0);
  const housingProvided = summary.reduce((s: number, r: any) => s + r.housing_provided, 0);
  const avgProgress = summary.length
    ? Math.round(summary.reduce((s: number, r: any) => s + r.avg_progress, 0) / summary.length)
    : 0;

  const columns: Column<RRFamily>[] = [
    {
      key: 'family_head_name',
      header: 'Family Head',
      render: (item) => (
        <div>
          <div className="text-sm font-medium text-slate-900">{item.family_head_name}</div>
          <div className="text-xs text-slate-500">{item.family_id_number || '—'}</div>
        </div>
      ),
      sortable: true,
    },
    {
      key: 'member_count',
      header: 'Members',
      render: (item) => <span className="tabular-nums">{item.member_count || '—'}</span>,
    },
    {
      key: 'displaced_status',
      header: 'Displacement',
      render: (item) => <StatusBadge status={item.displaced_status} />,
    },
    {
      key: 'current_stage',
      header: 'Stage',
      render: (item) => <StatusBadge status={item.current_stage} />,
    },
    {
      key: 'housing_benefit_status',
      header: 'Housing',
      render: (item) => <StatusBadge status={item.housing_benefit_status} />,
    },
    {
      key: 'employment_benefit_status',
      header: 'Employment',
      render: (item) => <StatusBadge status={item.employment_benefit_status} />,
    },
    {
      key: 'monetary_benefit_amount',
      header: 'Benefit Amount',
      render: (item) => (
        <span className="tabular-nums">{formatCurrency(item.monetary_benefit_amount || 0)}</span>
      ),
    },
    {
      key: 'progress_percentage',
      header: 'Progress',
      render: (item) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-slate-200 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full"
              style={{ width: `${item.progress_percentage || 0}%` }}
            />
          </div>
          <span className="text-xs tabular-nums text-slate-500">{item.progress_percentage || 0}%</span>
        </div>
      ),
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
            setSelectedFamily(item);
            setShowEditModal(true);
          }}
        >
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">🏘️ R&R Management</h1>
        <p className="text-slate-500 text-sm">
          Manage rehabilitation and resettlement for displaced families
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard label="Total Families" value={totalFamilies} icon="👨‍👩‍👧‍👦" index={0} />
        <KPICard label="Resettled" value={resettledCount} icon="🏠" index={1} />
        <KPICard label="Housing Provided" value={housingProvided} icon="🏡" index={2} />
        <KPICard label="Avg Progress" value={`${avgProgress}%`} icon="📊" index={3} />
      </div>

      {/* Project Summary Cards */}
      {summary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Project-wise R&R Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {summary.map((s: any) => (
                <div
                  key={s.project_id}
                  className="p-3 border border-slate-200 rounded-lg hover:shadow-sm"
                >
                  <div className="text-sm font-medium text-slate-900 mb-2">{s.project_name}</div>
                  <div className="grid grid-cols-2 gap-1 text-xs text-slate-600">
                    <span>Families: {s.total_families}</span>
                    <span>Fully displaced: {s.fully_displaced}</span>
                    <span>Housing: {s.housing_provided}</span>
                    <span>Employment: {s.employment_provided}</span>
                    <span>Resettled: {s.resettled}</span>
                    <span>Avg progress: {s.avg_progress}%</span>
                  </div>
                  <div className="mt-2 w-full bg-slate-200 rounded-full h-1.5">
                    <div
                      className="bg-emerald-500 h-1.5 rounded-full"
                      style={{ width: `${s.avg_progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Stage</label>
              <Select value={stageFilter} onValueChange={setStageFilter}>
                <option value="">All Stages</option>
                {STAGE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Displacement</label>
              <Select value={displacedFilter} onValueChange={setDisplacedFilter}>
                <option value="">All</option>
                {DISPLACED_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex-1" />
            <span className="text-sm text-slate-500">{data?.total || 0} families</span>
          </div>
        </CardContent>
      </Card>

      <DataTable
        columns={columns}
        data={families}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        searchPlaceholder="Search by family name..."
        onSearch={(term) => {
          setSearch(term);
          setPage(1);
        }}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No R&R families found"
        onRowClick={(item) => {
          setSelectedFamily(item);
          setShowEditModal(true);
        }}
      />

      {/* Edit Modal */}
      {showEditModal && selectedFamily && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto"
          >
            <h3 className="text-lg font-bold text-slate-900 mb-4">Edit R&R Family</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-500">Family Head Name</label>
                <Input
                  value={selectedFamily.family_head_name}
                  onChange={(e) =>
                    setSelectedFamily({ ...selectedFamily, family_head_name: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-500">Member Count</label>
                  <Input
                    type="number"
                    value={selectedFamily.member_count || ''}
                    onChange={(e) =>
                      setSelectedFamily({
                        ...selectedFamily,
                        member_count: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Progress %</label>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={selectedFamily.progress_percentage || 0}
                    onChange={(e) =>
                      setSelectedFamily({
                        ...selectedFamily,
                        progress_percentage: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Displaced Status</label>
                <Select
                  value={selectedFamily.displaced_status}
                  onValueChange={(v) =>
                    setSelectedFamily({ ...selectedFamily, displaced_status: v })
                  }
                >
                  {DISPLACED_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Current Stage</label>
                <Select
                  value={selectedFamily.current_stage}
                  onValueChange={(v) =>
                    setSelectedFamily({ ...selectedFamily, current_stage: v })
                  }
                >
                  {STAGE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-500">Housing Benefit</label>
                  <Select
                    value={selectedFamily.housing_benefit_status}
                    onValueChange={(v) =>
                      setSelectedFamily({ ...selectedFamily, housing_benefit_status: v })
                    }
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="provided">Provided</option>
                  </Select>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Employment Benefit</label>
                  <Select
                    value={selectedFamily.employment_benefit_status}
                    onValueChange={(v) =>
                      setSelectedFamily({ ...selectedFamily, employment_benefit_status: v })
                    }
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="provided">Provided</option>
                  </Select>
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Monetary Benefit (₹)</label>
                <Input
                  type="number"
                  value={selectedFamily.monetary_benefit_amount || ''}
                  onChange={(e) =>
                    setSelectedFamily({
                      ...selectedFamily,
                      monetary_benefit_amount: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
              <Button
                onClick={() =>
                  updateMutation.mutate({
                    id: selectedFamily.id,
                    updates: {
                      family_head_name: selectedFamily.family_head_name,
                      member_count: selectedFamily.member_count,
                      displaced_status: selectedFamily.displaced_status,
                      current_stage: selectedFamily.current_stage,
                      housing_benefit_status: selectedFamily.housing_benefit_status,
                      employment_benefit_status: selectedFamily.employment_benefit_status,
                      monetary_benefit_amount: selectedFamily.monetary_benefit_amount,
                      progress_percentage: selectedFamily.progress_percentage,
                    },
                  })
                }
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
