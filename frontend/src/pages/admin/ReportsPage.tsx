import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import api from '../../services/api';

type ReportType = 'projects' | 'compensation' | 'gis-parcels';

const REPORT_CONFIG: Record<ReportType, { icon: string; title: string; description: string; filename: string }> = {
  projects: {
    icon: '📊',
    title: 'Project MIS Report',
    description: 'Complete project listing with status, budget, stage, and progress data.',
    filename: 'NLAMS_Project_MIS_Report',
  },
  compensation: {
    icon: '💰',
    title: 'Compensation Report',
    description: 'All compensation assessments, awards, and payment disbursements.',
    filename: 'NLAMS_Compensation_Report',
  },
  'gis-parcels': {
    icon: '🗺️',
    title: 'GIS Parcel Report',
    description: 'Land parcel inventory with verification status and area details.',
    filename: 'NLAMS_GIS_Parcels_Report',
  },
};

export default function ReportsPage() {
  const [loading, setLoading] = useState<ReportType | null>(null);
  const [format, setFormat] = useState('csv');

  const downloadReport = async (reportType: ReportType) => {
    setLoading(reportType);
    try {
      const response = await api.get(`/reports/${reportType}`, {
        params: { format },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${REPORT_CONFIG[reportType].filename}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Reports & MIS Export</h1>
        <p className="text-slate-500 text-sm">Download management information system reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(Object.keys(REPORT_CONFIG) as ReportType[]).map((reportType) => {
          const config = REPORT_CONFIG[reportType];
          const isLoading = loading === reportType;
          return (
            <Card
              key={reportType}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => !loading && downloadReport(reportType)}
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">{config.icon}</span> {config.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">{config.description}</p>
                <Button variant="outline" className="mt-3" disabled={!!loading}>
                  {isLoading ? 'Generating...' : `Download ${format.toUpperCase()}`}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
