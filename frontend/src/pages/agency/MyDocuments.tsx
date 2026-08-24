import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { EmptyState } from '../../components/shared/EmptyState';
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

export default function MyDocuments() {
  const { data: documents, isLoading } = useQuery({
    queryKey: ['agency-documents'],
    queryFn: async () => {
      const { data } = await api.get('/documents', { params: { page_size: 50 } });
      return data;
    },
  });

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">📄 Agency Documents</h1>
        <p className="text-slate-500 text-sm">
          Manage documents for your assigned projects
        </p>
      </motion.div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Uploaded Documents</CardTitle>
            <Button size="sm">📤 Upload Document</Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="skeleton h-16 rounded-lg" />
              ))}
            </div>
          ) : documents?.items?.length === 0 ? (
            <EmptyState
              icon="📄"
              title="No documents uploaded"
              description="Upload DPR reports, notifications, survey documents and more."
            />
          ) : (
            <div className="space-y-2">
              {documents?.items?.map((doc: any) => (
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
                    <span className="text-xs text-slate-400 tabular-nums">
                      {(doc.file_size / 1024).toFixed(0)} KB
                    </span>
                    <Button variant="outline" size="sm" asChild>
                      <a href={doc.file_path} target="_blank" rel="noopener noreferrer">
                        View
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
