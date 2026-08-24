import React from 'react';
import { Button } from '../ui/button';
import { EmptyState } from '../shared/EmptyState';
import { formatDate } from '../../lib/utils';

const DOC_TYPE_ICONS: Record<string, string> = {
  dpr: '📄',
  survey_report: '📋',
  notification: '📬',
  award: '🏆',
  geojson: '🗺️',
  photo: '📷',
  other: '📎',
};

interface Document {
  id: string;
  doc_type: string;
  file_name: string;
  file_path: string;
  file_size: number;
  version: number;
  created_at: string;
}

interface DocListProps {
  documents: Document[];
  isLoading: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  showFileSize?: boolean;
}

export function DocList({
  documents,
  isLoading,
  emptyTitle = 'No documents available',
  emptyDescription = 'Documents will appear here once uploaded.',
  showFileSize = false,
}: DocListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="skeleton h-16 rounded-lg" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <EmptyState icon="📄" title={emptyTitle} description={emptyDescription} />
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">{DOC_TYPE_ICONS[doc.doc_type] || '📎'}</span>
            <div>
              <div className="text-sm font-medium text-slate-900">{doc.file_name}</div>
              <div className="text-xs text-slate-500">
                {doc.doc_type?.replace(/_/g, ' ').toUpperCase()} • v{doc.version} •{' '}
                {formatDate(doc.created_at)}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showFileSize && doc.file_size && (
              <span className="text-xs text-slate-400 tabular-nums">
                {(doc.file_size / 1024).toFixed(0)} KB
              </span>
            )}
            <Button variant="outline" size="sm" asChild>
              <a href={doc.file_path} target="_blank" rel="noopener noreferrer">
                View
              </a>
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
