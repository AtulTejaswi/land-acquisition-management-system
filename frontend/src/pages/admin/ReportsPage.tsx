import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import api from '../../services/api';

export default function ReportsPage() {
  const [loading, setLoading] = useState(false);
  const [format, setFormat] = useState('csv');

  const downloadReport = async (reportType: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/reports/mis`, {
        params: { format },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `NLAMS_MIS_Report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Reports & MIS Export</h1>
        <p className="text-slate-500 text-sm">Download management information system reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => downloadReport('projects')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">📊</span> Project MIS Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">Complete project listing with status, budget, stage, and progress data.</p>
            <Button variant="outline" className="mt-3" disabled={loading}>
              {loading ? 'Generating...' : `Download ${format.toUpperCase()}`}
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">💰</span> Compensation Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">All compensation assessments, awards, and payment disbursements.</p>
            <Button variant="outline" className="mt-3" disabled>Coming Soon</Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">🗺️</span> GIS Parcel Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">Land parcel inventory with verification status and area details.</p>
            <Button variant="outline" className="mt-3" disabled>Coming Soon</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
