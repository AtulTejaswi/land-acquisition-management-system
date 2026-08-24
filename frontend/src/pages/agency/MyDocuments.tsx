import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { DocList } from '../../components/documents/DocList';

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
        <p className="text-slate-500 text-sm">Manage documents for your assigned projects</p>
      </motion.div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Uploaded Documents</CardTitle>
            <Button size="sm">📤 Upload Document</Button>
          </div>
        </CardHeader>
        <CardContent>
          <DocList
            documents={documents?.items || []}
            isLoading={isLoading}
            emptyTitle="No documents uploaded"
            emptyDescription="Upload DPR reports, notifications, survey documents and more."
            showFileSize
          />
        </CardContent>
      </Card>
    </div>
  );
}
