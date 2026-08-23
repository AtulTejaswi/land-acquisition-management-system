import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { StageStepper } from '../../components/project/StageStepper';
import { formatCurrency, formatDate, getStatusColor } from '../../lib/utils';

export default function TrackStatus() {
  const { data: parcels, isLoading } = useQuery({
    queryKey: ['citizen-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/parcels', { params: { page_size: 10 } });
      return data;
    },
  });

  const { data: compensations } = useQuery({
    queryKey: ['citizen-compensations'],
    queryFn: async () => {
      const { data } = await api.get('/compensation', { params: { page_size: 10 } });
      return data;
    },
  });

  const { data: payments } = useQuery({
    queryKey: ['citizen-payments'],
    queryFn: async () => {
      const { data } = await api.get('/payments', { params: { page_size: 10 } });
      return data;
    },
  });

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">🔍 Track Your Status</h1>
        <p className="text-slate-500 text-sm">Monitor your land acquisition and compensation status in real-time</p>
      </motion.div>

      {/* Transparency Portal */}
      <Card className="border-emerald-200 bg-emerald-50/30">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-sm text-emerald-700">
            <span>🇮🇳</span>
            <span className="font-medium">Citizen Transparency Portal</span>
            <span className="text-emerald-600">—</span>
            <span>You can track every step of the acquisition process here</span>
          </div>
        </CardContent>
      </Card>

      {/* My Land Parcels */}
      <Card>
        <CardHeader>
          <CardTitle>My Land Parcels</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="skeleton h-20 rounded-lg" />)}</div>
          ) : (
            <div className="space-y-3">
              {parcels?.items?.length === 0 && (
                <p className="text-slate-400 text-center py-6">No parcels linked to your account yet</p>
              )}
              {parcels?.items?.map((parcel: any) => (
                <div key={parcel.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium text-slate-900">Survey No: {parcel.survey_number}</div>
                      <div className="text-sm text-slate-500">{parcel.village_name}, {parcel.district_name}</div>
                      <div className="text-sm text-slate-500">Area: {parcel.area_hectares} hectares • Type: {parcel.land_type}</div>
                    </div>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(parcel.verification_status)}`}>
                      {parcel.verification_status?.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compensation Status */}
      <Card>
        <CardHeader>
          <CardTitle>💰 Compensation Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {compensations?.items?.length === 0 && (
              <p className="text-slate-400 text-center py-6">No compensation records yet</p>
            )}
            {compensations?.items?.map((comp: any) => (
              <div key={comp.id} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-sm text-slate-500">Parcel ID: {comp.parcel_id?.slice(0, 8)}...</div>
                    <div className="text-lg font-bold text-slate-900 tabular-nums">{comp.total_award ? formatCurrency(Number(comp.total_award)) : '—'}</div>
                    <div className="text-xs text-slate-400">Market Value: {comp.market_value ? formatCurrency(Number(comp.market_value)) : '—'} + Solatium: {comp.solatium ? formatCurrency(Number(comp.solatium)) : '—'}</div>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(comp.status)}`}>
                    {comp.status?.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Payment Status */}
      <Card>
        <CardHeader>
          <CardTitle>🏦 Payment Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {payments?.items?.length === 0 && (
              <p className="text-slate-400 text-center py-6">No payment records yet</p>
            )}
            {payments?.items?.map((pay: any) => (
              <div key={pay.id} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-lg font-bold text-slate-900 tabular-nums">{formatCurrency(Number(pay.amount))}</div>
                    <div className="text-xs text-slate-500">PFMS Ref: {pay.pfms_reference || '—'}</div>
                    <div className="text-xs text-slate-500">Bank Verification: {pay.bank_verification_status}</div>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(pay.payment_status)}`}>
                    {pay.payment_status?.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
