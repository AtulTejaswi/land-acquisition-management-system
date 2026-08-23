import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  if (amount >= 1e7) return `₹${(amount / 1e7).toFixed(1)}Cr`;
  if (amount >= 1e5) return `₹${(amount / 1e5).toFixed(1)}L`;
  return `₹${amount.toLocaleString('en-IN')}`;
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

export function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-IN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'bg-slate-100 text-slate-700',
    submitted: 'bg-blue-100 text-blue-700',
    under_review: 'bg-amber-100 text-amber-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-red-100 text-red-700',
    active: 'bg-blue-100 text-blue-700',
    delayed: 'bg-orange-100 text-orange-700',
    completed: 'bg-emerald-100 text-emerald-700',
    pending: 'bg-slate-100 text-slate-600',
    in_progress: 'bg-blue-100 text-blue-700',
    verified: 'bg-emerald-100 text-emerald-700',
    disputed: 'bg-orange-100 text-orange-700',
    acquired: 'bg-indigo-100 text-indigo-700',
    disbursed: 'bg-emerald-100 text-emerald-700',
    processing: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700',
    filed: 'bg-amber-100 text-amber-700',
    resolved: 'bg-emerald-100 text-emerald-700',
  };
  return colors[status] || 'bg-slate-100 text-slate-600';
}

export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    low: 'bg-slate-100 text-slate-600',
    medium: 'bg-blue-100 text-blue-700',
    high: 'bg-amber-100 text-amber-700',
    critical: 'bg-red-100 text-red-700',
  };
  return colors[priority] || 'bg-slate-100 text-slate-600';
}

export const STAGES = [
  'project_proposal', 'dpr_upload', 'land_requirement', 'state_review',
  'district_verification', 'gis_mapping', 'legal_notification',
  'objection_handling', 'compensation_assessment', 'award_declaration',
  'payment_disbursement', 'physical_possession', 'rehabilitation_resettlement',
  'project_completion',
];

export const STAGE_LABELS: Record<string, string> = {
  project_proposal: 'Project Proposal',
  dpr_upload: 'DPR Upload',
  land_requirement: 'Land Requirement',
  state_review: 'State Review',
  district_verification: 'District Verification',
  gis_mapping: 'GIS Mapping',
  legal_notification: 'Legal Notification',
  objection_handling: 'Objection Handling',
  compensation_assessment: 'Compensation Assessment',
  award_declaration: 'Award Declaration',
  payment_disbursement: 'Payment Disbursement',
  physical_possession: 'Physical Possession',
  rehabilitation_resettlement: 'R&R',
  project_completion: 'Project Completion',
};
