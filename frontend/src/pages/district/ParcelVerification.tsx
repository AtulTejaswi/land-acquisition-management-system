import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { formatDate } from '../../lib/utils';

export default function ParcelVerification() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const parcelId = searchParams.get('id');

  const [remarks, setRemarks] = useState('');
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionType, setActionType] = useState<'verified' | 'disputed'>('verified');

  const { data: parcel, isLoading } = useQuery({
    queryKey: ['parcel-detail', parcelId],
    queryFn: async () => {
      const { data } = await api.get(`/parcels/${parcelId}`);
      return data;
    },
    enabled: !!parcelId,
  });

  const updateMutation = useMutation({
    mutationFn: async (status: string) => {
      const { data } = await api.patch(`/parcels/${parcelId}`, {
        verification_status: status,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parcel-detail', parcelId] });
      queryClient.invalidateQueries({ queryKey: ['verification-queue'] });
      setShowActionModal(false);
      setRemarks('');
    },
  });

  if (!parcelId) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-slate-500 mb-4">No parcel selected for verification.</p>
            <Button onClick={() => navigate('/district/verification')}>
              ← Back to Verification Queue
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="skeleton h-24 rounded-xl" />
        ))}
      </div>
    );
  }

  if (!parcel) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-slate-500 mb-4">Parcel not found.</p>
            <Button onClick={() => navigate('/district/verification')}>
              ← Back to Verification Queue
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">📋 Parcel Verification</h1>
            <p className="text-slate-500 text-sm">
              Survey No. {parcel.survey_number} — {parcel.village_name || '—'}
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate('/district/verification')}>
            ← Back to Queue
          </Button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Parcel Details</span>
                <StatusBadge status={parcel.verification_status} />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-500">Survey Number</label>
                  <p className="text-sm font-medium text-slate-900">{parcel.survey_number}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Village</label>
                  <p className="text-sm text-slate-900">{parcel.village_name || '—'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">District</label>
                  <p className="text-sm text-slate-900">{parcel.district_name || '—'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">State</label>
                  <p className="text-sm text-slate-900">{parcel.state_name || '—'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Area</label>
                  <p className="text-sm text-slate-900 tabular-nums">
                    {parcel.area_hectares?.toFixed(4) || '—'} hectares
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Land Type</label>
                  <p className="text-sm text-slate-900 capitalize">
                    {parcel.land_type?.replace('_', ' ') || '—'}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Ownership Status</label>
                  <p className="text-sm text-slate-900 capitalize">
                    {parcel.ownership_status?.replace('_', ' ') || '—'}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Created</label>
                  <p className="text-sm text-slate-900">{formatDate(parcel.created_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Land Owners */}
          <Card>
            <CardHeader>
              <CardTitle>Land Owners ({parcel.owners?.length || 0})</CardTitle>
            </CardHeader>
            <CardContent>
              {parcel.owners?.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-4">No registered owners</p>
              ) : (
                <div className="space-y-3">
                  {parcel.owners?.map((owner: any) => (
                    <div
                      key={owner.id}
                      className="flex items-center justify-between p-3 border border-slate-200 rounded-lg"
                    >
                      <div>
                        <div className="text-sm font-medium text-slate-900">
                          {owner.full_name}
                        </div>
                        <div className="text-xs text-slate-500">
                          Phone: {owner.phone} • Aadhaar: {owner.aadhaar_masked}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-900 tabular-nums">
                          {owner.share_percentage}%
                        </div>
                        <div className="text-xs text-slate-500">IFSC: {owner.ifsc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Action Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Verification Action</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {parcel.verification_status === 'pending' ? (
                <>
                  <p className="text-sm text-slate-600">
                    Review the parcel details and owner information, then verify or dispute this parcel.
                  </p>
                  <div className="flex flex-col gap-2">
                    <Button
                      className="w-full bg-emerald-600 hover:bg-emerald-700"
                      onClick={() => {
                        setActionType('verified');
                        setShowActionModal(true);
                      }}
                    >
                      ✅ Verify Parcel
                    </Button>
                    <Button
                      variant="destructive"
                      className="w-full"
                      onClick={() => {
                        setActionType('disputed');
                        setShowActionModal(true);
                      }}
                    >
                      ❌ Mark as Disputed
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-4">
                  <StatusBadge status={parcel.verification_status} />
                  <p className="text-sm text-slate-500 mt-2">
                    This parcel has already been{' '}
                    {parcel.verification_status === 'verified' ? 'verified' : 'disputed'}.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Project</span>
                <span className="text-slate-900 font-medium text-xs">
                  {parcel.project_id?.slice(0, 8)}...
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Area in acres</span>
                <span className="text-slate-900 tabular-nums">
                  {parcel.area_hectares ? (parcel.area_hectares * 2.47105).toFixed(2) : '—'}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Action Modal */}
      {showActionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-bold text-slate-900 mb-4">
              {actionType === 'verified' ? '✅ Verify Parcel' : '❌ Dispute Parcel'}
            </h3>
            <div className="space-y-3">
              <p className="text-sm text-slate-600">
                Survey No: <strong>{parcel.survey_number}</strong>
              </p>
              <div>
                <label className="text-xs font-medium text-slate-500">Remarks (required)</label>
                <Input
                  placeholder="Enter verification remarks..."
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
                variant={actionType === 'verified' ? 'default' : 'destructive'}
                onClick={() => updateMutation.mutate(actionType)}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Processing...' : actionType === 'verified' ? 'Verify' : 'Dispute'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
