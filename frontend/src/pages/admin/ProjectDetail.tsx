import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { StageStepper } from '../../components/project/StageStepper';
import { formatCurrency, formatDate, formatDateTime } from '../../lib/utils';
import { motion } from 'framer-motion';
import { KPICard } from '../../components/shared/KPICard';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: project, isLoading: loadingProject } = useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      const { data } = await api.get(`/projects/${id}`);
      return data;
    },
    enabled: !!id,
  });

  const { data: timeline } = useQuery({
    queryKey: ['project-timeline', id],
    queryFn: async () => {
      const { data } = await api.get(`/projects/${id}/timeline`);
      return data;
    },
    enabled: !!id,
  });

  const { data: delayPrediction } = useQuery({
    queryKey: ['ai-delay', id],
    queryFn: async () => {
      const { data } = await api.get(`/ai/delay-prediction/${id}`);
      return data;
    },
    enabled: !!id,
  });

  const { data: riskScore } = useQuery({
    queryKey: ['ai-risk', id],
    queryFn: async () => {
      const { data } = await api.get(`/ai/risk-score/${id}`);
      return data;
    },
    enabled: !!id,
  });

  const { data: missingDocs } = useQuery({
    queryKey: ['ai-missing-docs', id],
    queryFn: async () => {
      const { data } = await api.get(`/ai/missing-documents/${id}`);
      return data;
    },
    enabled: !!id,
  });

  const { data: possessionStatus } = useQuery({
    queryKey: ['possession-status', id],
    queryFn: async () => {
      const { data } = await api.get(`/possession/project/${id}/status`);
      return data;
    },
    enabled: !!id,
  });

  if (loadingProject) {
    return <div className="space-y-4"><div className="skeleton h-40 rounded-xl" /><div className="skeleton h-60 rounded-xl" /></div>;
  }

  if (!project) return <div className="text-center py-12 text-slate-500">Project not found</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{project.name}</h1>
            <p className="text-slate-500 text-sm mt-1">{project.description}</p>
          </div>
          <div className="flex gap-2">
            <StatusBadge status={project.status} />
            <StatusBadge status={project.priority} type="priority" />
          </div>
        </div>
      </motion.div>

      {/* Stage Stepper */}
      <Card>
        <CardContent className="pt-6">
          <StageStepper currentStage={project.current_stage} />
        </CardContent>
      </Card>

      {/* Project Info + AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Info */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader><CardTitle>Project Details</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-slate-500">Ministry:</span> <span className="font-medium">{project.ministry_name || '—'}</span></div>
                <div><span className="text-slate-500">Category:</span> <span className="font-medium">{project.category_name || '—'}</span></div>
                <div><span className="text-slate-500">State:</span> <span className="font-medium">{project.state_name || '—'}</span></div>
                <div><span className="text-slate-500">District:</span> <span className="font-medium">{project.district_name || '—'}</span></div>
                <div><span className="text-slate-500">Budget:</span> <span className="font-medium tabular-nums">{project.estimated_budget ? formatCurrency(Number(project.estimated_budget)) : '—'}</span></div>
                <div><span className="text-slate-500">Land Required:</span> <span className="font-medium">{project.estimated_land_required_hectares} ha</span></div>
                <div><span className="text-slate-500">Start Date:</span> <span className="font-medium">{formatDate(project.start_date)}</span></div>
                <div><span className="text-slate-500">Target Completion:</span> <span className="font-medium">{formatDate(project.target_completion_date)}</span></div>
              </div>
            </CardContent>
          </Card>

          {/* Audit Timeline */}
          <Card>
            <CardHeader><CardTitle>📋 Full Audit Trail Timeline</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {timeline?.timeline?.length === 0 && (
                  <p className="text-slate-400 text-sm">No audit trail entries yet</p>
                )}
                {timeline?.timeline?.map((entry: any, idx: number) => (
                  <div key={idx} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className={`w-3 h-3 rounded-full ${entry.type === 'milestone' ? 'bg-emerald-500' : 'bg-primary-500'}`} />
                      {idx < (timeline.timeline.length - 1) && <div className="w-0.5 flex-1 bg-slate-200 mt-1" />}
                    </div>
                    <div className="pb-3">
                      <div className="text-sm font-medium text-slate-900">{entry.title || entry.action}</div>
                      <div className="text-xs text-slate-500">{formatDateTime(entry.timestamp)}</div>
                      {entry.remarks && <div className="text-xs text-slate-600 mt-1">{entry.remarks}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights Panel */}
        <div className="space-y-4">
          <Card className="border-blue-200 bg-blue-50/30">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base">🤖 AI Insights</CardTitle>
              <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">Beta</span>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Delay Prediction */}
              {delayPrediction && (
                <div className="p-3 rounded-lg bg-white border border-slate-200">
                  <div className="text-xs font-semibold text-slate-500 mb-1">Delay Prediction</div>
                  <div className="flex items-center gap-2">
                    <span className={`text-lg font-bold ${
                      delayPrediction.color === 'green' ? 'text-emerald-600' :
                      delayPrediction.color === 'orange' ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {delayPrediction.risk_label}
                    </span>
                    {delayPrediction.estimated_delay_days > 0 && (
                      <span className="text-xs text-slate-500">~{delayPrediction.estimated_delay_days} days delay</span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{delayPrediction.reasoning}</p>
                </div>
              )}

              {/* Risk Score */}
              {riskScore && (
                <div className="p-3 rounded-lg bg-white border border-slate-200">
                  <div className="text-xs font-semibold text-slate-500 mb-1">Risk Score</div>
                  <div className="flex items-center gap-2">
                    <span className={`text-2xl font-bold ${
                      riskScore.color === 'green' ? 'text-emerald-600' :
                      riskScore.color === 'orange' ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {riskScore.score}
                    </span>
                    <span className="text-xs text-slate-500">/ 100 — {riskScore.label}</span>
                  </div>
                  <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        riskScore.color === 'green' ? 'bg-emerald-500' :
                        riskScore.color === 'orange' ? 'bg-amber-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${riskScore.score}%` }}
                    />
                  </div>
                  <div className="mt-2 text-xs text-slate-500 space-y-1">
                    <div>Open objections: {riskScore.factors?.open_objections}</div>
                    <div>Disputed parcels: {riskScore.factors?.disputed_parcels}/{riskScore.factors?.total_parcels}</div>
                    <div>Days since update: {riskScore.factors?.days_since_last_update}</div>
                  </div>
                </div>
              )}

              {/* Missing Documents */}
              {missingDocs && (
                <div className="p-3 rounded-lg bg-white border border-slate-200">
                  <div className="text-xs font-semibold text-slate-500 mb-1">Missing Documents</div>
                  <div className="text-sm font-medium">
                    Completeness: <span className={missingDocs.completeness_pct > 50 ? 'text-emerald-600' : 'text-amber-600'}>{missingDocs.completeness_pct}%</span>
                  </div>
                  {missingDocs.missing_documents?.length > 0 ? (
                    <div className="mt-2 space-y-1">
                      {missingDocs.missing_documents.map((doc: string) => (
                        <div key={doc} className="flex items-center gap-1.5 text-xs text-amber-700">
                          <span>⚠️</span> {doc.replace(/_/g, ' ').toUpperCase()}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-emerald-600 mt-1">✅ All required documents uploaded</div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Possession Status */}
          {possessionStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>📋 Possession Status</span>
                  <span className="text-sm font-normal text-slate-500">
                    {possessionStatus.possessed_parcels}/{possessionStatus.total_parcels} parcels
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Completion</span>
                    <span className="tabular-nums">{possessionStatus.completion_percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div
                      className="bg-emerald-500 h-3 rounded-full transition-all"
                      style={{ width: `${possessionStatus.completion_percentage}%` }}
                    />
                  </div>
                </div>
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {possessionStatus.parcels?.map((p: any) => (
                    <div
                      key={p.parcel_id}
                      className={`flex items-center justify-between p-2 rounded-lg border ${
                        p.has_possession ? 'border-emerald-200 bg-emerald-50/50' : 'border-slate-200'
                      }`}
                    >
                      <div>
                        <div className="text-sm font-medium text-slate-900">
                          {p.survey_number}
                        </div>
                        <div className="text-xs text-slate-500">
                          {p.area_hectares?.toFixed(2)} ha
                        </div>
                      </div>
                      <StatusBadge
                        status={p.has_possession ? 'completed' : 'pending'}
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
