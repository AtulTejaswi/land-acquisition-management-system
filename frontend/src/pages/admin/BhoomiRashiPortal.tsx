import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export default function BhoomiRashiPortal() {
  const queryClient = useQueryClient();
  const [selectedVillage, setSelectedVillage] = useState<string>('');
  const [selectedNature, setSelectedNature] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [selectedParcelIds, setSelectedParcelIds] = useState<string[]>([]);
  const [activeParcelDetails, setActiveParcelDetails] = useState<any | null>(null);
  const [showPromoteModal, setShowPromoteModal] = useState<boolean>(false);
  const [targetProjectId, setTargetProjectId] = useState<string>('');
  const [promoteStatusMsg, setPromoteStatusMsg] = useState<string | null>(null);

  // 1. Fetch Staging Summary
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['staging-summary'],
    queryFn: async () => {
      const { data } = await api.get('/ml/staging/summary');
      return data;
    },
  });

  // 2. Fetch Staging Parcels
  const { data: parcelsData, isLoading: parcelsLoading } = useQuery({
    queryKey: ['staging-parcels', page, selectedVillage, selectedNature, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '15',
      });
      if (selectedVillage) params.append('village', selectedVillage);
      if (selectedNature) params.append('land_nature', selectedNature);
      if (searchQuery) params.append('search', searchQuery);
      const { data } = await api.get(`/ml/staging/parcels?${params.toString()}`);
      return data;
    },
  });

  // 3. Fetch Active Projects for Promotion Dropdown
  const { data: projects } = useQuery({
    queryKey: ['projects-list'],
    queryFn: async () => {
      const { data } = await api.get('/projects');
      return data.items || data;
    },
  });

  // 4. Ingest Trigger Mutation
  const ingestMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/ml/ingest', {});
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staging-summary'] });
      queryClient.invalidateQueries({ queryKey: ['staging-parcels'] });
      alert(`✅ Bhoomi Rashi Ingestion Successful!\nLoaded ${data.land_rows_loaded} parcels and ${data.party_rows_loaded} owners from ${data.source_file}`);
    },
    onError: (err: any) => {
      alert(`❌ Ingestion failed: ${err.response?.data?.detail || err.message}`);
    },
  });

  // 5. Promote Mutation
  const promoteMutation = useMutation({
    mutationFn: async (payload: { project_id: string; staging_parcel_ids?: string[] }) => {
      const { data } = await api.post('/ml/staging/promote', payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staging-summary'] });
      queryClient.invalidateQueries({ queryKey: ['staging-parcels'] });
      queryClient.invalidateQueries({ queryKey: ['projects-list'] });
      setPromoteStatusMsg(`🎉 ${data.message}`);
      setTimeout(() => {
        setShowPromoteModal(false);
        setPromoteStatusMsg(null);
        setSelectedParcelIds([]);
      }, 2500);
    },
    onError: (err: any) => {
      alert(`❌ Promotion failed: ${err.response?.data?.detail || err.message}`);
    },
  });

  // 6. View Parties Query
  const { data: partiesData, isLoading: partiesLoading } = useQuery({
    queryKey: ['staging-parties', activeParcelDetails?.id],
    queryFn: async () => {
      if (!activeParcelDetails?.id) return [];
      const { data } = await api.get(`/ml/staging/parcels/${activeParcelDetails.id}/parties`);
      return data;
    },
    enabled: !!activeParcelDetails?.id,
  });

  const toggleSelectAll = () => {
    if (selectedParcelIds.length === parcelsData?.items?.length) {
      setSelectedParcelIds([]);
    } else {
      setSelectedParcelIds(parcelsData?.items?.map((p: any) => p.id) || []);
    }
  };

  const toggleSelect = (id: string) => {
    if (selectedParcelIds.includes(id)) {
      setSelectedParcelIds(selectedParcelIds.filter((item) => item !== id));
    } else {
      setSelectedParcelIds([...selectedParcelIds, id]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Indian Government Styling */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
          <div className="absolute right-0 top-0 w-96 h-full bg-gradient-to-l from-amber-500/10 to-transparent pointer-events-none" />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  MoRTH • Bhoomi Rashi Integration
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Gazette S.O. 1988E
                </span>
              </div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
                🏛️ Bhoomi Rashi Data Center & Staging Hub
              </h1>
              <p className="text-slate-300 text-sm mt-1 max-w-2xl">
                Official Ministry gazette land schedule parser, multilingual survey transliteration,
                and AI-assisted staging pipeline for national highway land acquisition.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="outline"
                className="bg-white/10 text-white border-white/20 hover:bg-white/20"
                onClick={() => ingestMutation.mutate()}
                disabled={ingestMutation.isPending}
              >
                {ingestMutation.isPending ? '⏳ Ingesting...' : '🔄 Reload Datasheet'}
              </Button>
              <Button
                className="bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold shadow-lg shadow-amber-500/20"
                onClick={() => setShowPromoteModal(true)}
                disabled={!summary?.total_parcels}
              >
                🚀 Promote to Project ({selectedParcelIds.length > 0 ? selectedParcelIds.length : 'All'})
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-primary-500 shadow-sm">
          <CardContent className="p-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Parsed Land Parcels</p>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">
                  {summaryLoading ? '...' : summary?.total_parcels || 0}
                </h3>
                <p className="text-xs text-emerald-600 mt-1 font-medium">Khordha District, Odisha</p>
              </div>
              <span className="p-2.5 bg-primary-50 text-primary-600 rounded-xl text-xl">🗺️</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500 shadow-sm">
          <CardContent className="p-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Identified Land Owners</p>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">
                  {summaryLoading ? '...' : summary?.total_parties || 0}
                </h3>
                <p className="text-xs text-slate-500 mt-1">Bilingual Name & Address Index</p>
              </div>
              <span className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl text-xl">👥</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500 shadow-sm">
          <CardContent className="p-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Land Nature Split</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-lg font-bold text-slate-900">{summary?.private_parcels || 0} Pvt</span>
                  <span className="text-xs text-slate-400">/</span>
                  <span className="text-base font-bold text-blue-600">{summary?.government_parcels || 0} Govt</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">AI Screening Ground Truth</p>
              </div>
              <span className="p-2.5 bg-blue-50 text-blue-600 rounded-xl text-xl">⚖️</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500 shadow-sm">
          <CardContent className="p-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Area in Schedule</p>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">
                  {summaryLoading ? '...' : summary?.total_area_hectares?.toFixed(2) || '0.00'} <span className="text-sm font-normal text-slate-500">Ha</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">~{(summary?.total_area_hectares ? summary.total_area_hectares * 2.471 : 0).toFixed(1)} Acres</p>
              </div>
              <span className="p-2.5 bg-amber-50 text-amber-600 rounded-xl text-xl">📐</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Table Section */}
      <Card className="shadow-sm border-slate-200">
        <CardHeader className="border-b border-slate-100 pb-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-lg font-bold text-slate-900">
                📋 Bhoomi Rashi Staging Schedule ({parcelsData?.total || 0} Records)
              </CardTitle>
              <CardDescription>
                Raw gazette records with normalized English & Devanagari numerals
              </CardDescription>
            </div>

            {/* Filter Bar */}
            <div className="flex flex-wrap items-center gap-2">
              <Input
                placeholder="Search survey no, village..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="w-48 h-9 text-xs"
              />
              <select
                value={selectedVillage}
                onChange={(e) => {
                  setSelectedVillage(e.target.value);
                  setPage(1);
                }}
                className="h-9 px-3 text-xs rounded-md border border-slate-200 bg-white text-slate-700 font-medium"
              >
                <option value="">All Villages</option>
                {summary?.villages?.map((v: string) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>

              <select
                value={selectedNature}
                onChange={(e) => {
                  setSelectedNature(e.target.value);
                  setPage(1);
                }}
                className="h-9 px-3 text-xs rounded-md border border-slate-200 bg-white text-slate-700 font-medium"
              >
                <option value="">All Land Natures</option>
                <option value="private">Private</option>
                <option value="government">Government</option>
              </select>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="p-3 w-10 text-center">
                    <input
                      type="checkbox"
                      checked={
                        parcelsData?.items?.length > 0 &&
                        selectedParcelIds.length === parcelsData?.items?.length
                      }
                      onChange={toggleSelectAll}
                      className="rounded border-slate-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                    />
                  </th>
                  <th className="p-3">S.No</th>
                  <th className="p-3">Survey Number</th>
                  <th className="p-3">Village / Sub-District</th>
                  <th className="p-3">Area (Hectares)</th>
                  <th className="p-3">Land Type</th>
                  <th className="p-3">Land Nature</th>
                  <th className="p-3">Owners</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {parcelsLoading ? (
                  [...Array(5)].map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td colSpan={9} className="p-4 bg-slate-50/50">
                        <div className="h-4 bg-slate-200 rounded w-full" />
                      </td>
                    </tr>
                  ))
                ) : parcelsData?.items?.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-slate-500">
                      No staging records found matching your filters.
                    </td>
                  </tr>
                ) : (
                  parcelsData?.items?.map((item: any) => {
                    const isSelected = selectedParcelIds.includes(item.id);
                    return (
                      <tr
                        key={item.id}
                        className={`hover:bg-slate-50/80 transition-colors ${
                          isSelected ? 'bg-primary-50/40' : ''
                        }`}
                      >
                        <td className="p-3 text-center">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelect(item.id)}
                            className="rounded border-slate-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                          />
                        </td>
                        <td className="p-3 font-semibold text-slate-900">{item.source_sno}</td>
                        <td className="p-3">
                          <div className="font-bold text-slate-900 whitespace-pre-line">
                            {item.raw_survey_number}
                          </div>
                          {item.survey_number_norm && (
                            <span className="text-[10px] text-slate-500 font-mono">
                              Norm: {item.survey_number_norm}
                            </span>
                          )}
                        </td>
                        <td className="p-3">
                          <div className="font-medium text-slate-900">{item.raw_village}</div>
                          <div className="text-[10px] text-slate-500">
                            {item.raw_sub_district}, {item.raw_district}
                          </div>
                        </td>
                        <td className="p-3 font-mono font-medium">
                          {item.area_hectares?.toFixed(4) || item.raw_area} Ha
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700 capitalize">
                            {item.land_type_mapped || item.raw_land_type}
                          </span>
                        </td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                              item.land_nature_label === 'government'
                                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                                : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                            }`}
                          >
                            {item.land_nature_label === 'government' ? '🏛️ Govt' : '👤 Private'}
                          </span>
                        </td>
                        <td className="p-3">
                          <Badge variant="outline" className="text-[11px]">
                            👥 {item.party_count} Owners
                          </Badge>
                        </td>
                        <td className="p-3 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs text-primary-600 hover:text-primary-700 hover:bg-primary-50"
                            onClick={() => setActiveParcelDetails(item)}
                          >
                            View Parties →
                          </Button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-100 flex items-center justify-between">
            <p className="text-xs text-slate-500">
              Showing page <strong>{page}</strong> of{' '}
              <strong>{Math.ceil((parcelsData?.total || 1) / 15)}</strong> ({parcelsData?.total || 0} total)
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                disabled={page >= Math.ceil((parcelsData?.total || 1) / 15)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Side Modal: Land Parties Inspector */}
      {activeParcelDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 max-h-[85vh] flex flex-col"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  👥 Land Owners & Interested Parties
                </h3>
                <p className="text-xs text-slate-500">
                  Survey No: <strong>{activeParcelDetails.raw_survey_number}</strong> • Village:{' '}
                  <strong>{activeParcelDetails.raw_village}</strong>
                </p>
              </div>
              <button
                onClick={() => setActiveParcelDetails(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {partiesLoading ? (
                <p className="text-center py-6 text-slate-500">Loading parties...</p>
              ) : partiesData?.length === 0 ? (
                <p className="text-center py-6 text-slate-500">No parties registered for this survey number.</p>
              ) : (
                partiesData?.map((party: any) => (
                  <div
                    key={party.id}
                    className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-semibold text-slate-900 text-sm whitespace-pre-line">
                          {party.raw_name}
                        </div>
                        <div className="text-xs text-slate-600 mt-1 whitespace-pre-line">
                          📍 {party.raw_address}
                        </div>
                      </div>
                      <Badge variant="outline" className="capitalize bg-white">
                        {party.party_type || party.raw_type || 'Owner'}
                      </Badge>
                    </div>
                    {party.area_hectares && (
                      <div className="text-xs text-slate-500 font-mono pt-1 border-t border-slate-200/60">
                        Indicated Share: {party.area_hectares} Ha
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <Button onClick={() => setActiveParcelDetails(null)}>Close</Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Promotion Modal */}
      {showPromoteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4"
          >
            <div className="border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900">
                🚀 Promote Staging Parcels to Active Project
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Converts validated Bhoomi Rashi staging records into transactional land parcels and
                initiates the acquisition workflow.
              </p>
            </div>

            {promoteStatusMsg ? (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium text-center">
                {promoteStatusMsg}
              </div>
            ) : (
              <>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700">Select Target Project</label>
                  <select
                    value={targetProjectId}
                    onChange={(e) => setTargetProjectId(e.target.value)}
                    className="w-full h-10 px-3 text-sm rounded-lg border border-slate-200 bg-white text-slate-800"
                  >
                    <option value="">-- Choose Target Project --</option>
                    {projects?.map((proj: any) => (
                      <option key={proj.id} value={proj.id}>
                        {proj.name} ({proj.current_stage || 'Proposal'})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg text-xs text-slate-600 space-y-1">
                  <div>
                    <strong>Records to promote:</strong>{' '}
                    {selectedParcelIds.length > 0
                      ? `${selectedParcelIds.length} selected parcels`
                      : `All ${summary?.total_parcels || 250} parcels in staging schedule`}
                  </div>
                  <div>
                    <strong>Target District:</strong> Khordha / Project District
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowPromoteModal(false)}
                    disabled={promoteMutation.isPending}
                  >
                    Cancel
                  </Button>
                  <Button
                    className="bg-primary-600 hover:bg-primary-700"
                    disabled={!targetProjectId || promoteMutation.isPending}
                    onClick={() =>
                      promoteMutation.mutate({
                        project_id: targetProjectId,
                        staging_parcel_ids:
                          selectedParcelIds.length > 0 ? selectedParcelIds : undefined,
                      })
                    }
                  >
                    {promoteMutation.isPending ? 'Promoting...' : 'Confirm Promotion'}
                  </Button>
                </div>
              </>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
}
