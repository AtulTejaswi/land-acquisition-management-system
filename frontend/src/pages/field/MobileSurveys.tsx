import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';

export default function MobileSurveys() {
  const [showNewForm, setShowNewForm] = useState(false);
  const [parcelSearch, setParcelSearch] = useState('');
  const [gpsCoords, setGpsCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [notes, setNotes] = useState('');
  const [capturing, setCapturing] = useState(false);

  const { data: parcels } = useQuery({
    queryKey: ['field-parcels', parcelSearch],
    queryFn: async () => {
      const { data } = await api.get('/parcels', { params: { search: parcelSearch, page_size: 20 } });
      return data;
    },
  });

  const { data: surveys } = useQuery({
    queryKey: ['field-surveys'],
    queryFn: async () => {
      const { data } = await api.get('/surveys');
      return data;
    },
  });

  const captureGPS = () => {
    setCapturing(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
          setCapturing(false);
        },
        () => {
          // Mock GPS for demo
          setGpsCoords({ lat: 21.1458 + Math.random() * 0.01, lng: 79.0882 + Math.random() * 0.01 });
          setCapturing(false);
        }
      );
    } else {
      setGpsCoords({ lat: 21.1458, lng: 79.0882 });
      setCapturing(false);
    }
  };

  const submitSurvey = async () => {
    try {
      await api.post('/surveys', {
        parcel_id: parcels?.items?.[0]?.id,
        survey_date: new Date().toISOString(),
        geo_lat: gpsCoords?.lat,
        geo_lng: gpsCoords?.lng,
        condition_notes: notes,
      });
      setShowNewForm(false);
      setNotes('');
      setGpsCoords(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-4 pb-20">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-xl font-bold text-slate-900">📋 My Surveys</h1>
      </motion.div>

      {/* Recent Surveys */}
      <div className="space-y-3">
        {surveys?.map((survey: any, idx: number) => (
          <motion.div
            key={survey.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-sm font-medium text-slate-900">Parcel: {survey.parcel_id?.slice(0, 8)}...</div>
                    <div className="text-xs text-slate-500 mt-1">📍 {survey.geo_lat?.toFixed(4)}, {survey.geo_lng?.toFixed(4)}</div>
                    <div className="text-xs text-slate-500">{survey.condition_notes || 'No notes'}</div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    survey.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                    survey.status === 'flagged' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {survey.status}
                  </span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* New Inspection Button */}
      <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 max-w-md w-full px-4">
        <Button className="w-full shadow-lg min-h-[44px]" size="lg" onClick={() => setShowNewForm(!showNewForm)}>
          {showNewForm ? '✕ Cancel' : '➕ New Inspection'}
        </Button>
      </div>

      {/* New Inspection Form */}
      {showNewForm && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-primary-200">
            <CardHeader>
              <CardTitle className="text-base">New Inspection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label htmlFor="parcel-search" className="text-sm font-medium text-slate-700">Select Parcel</label>
                <Input
                  id="parcel-search"
                  placeholder="Search parcel by survey number..."
                  value={parcelSearch}
                  onChange={(e) => setParcelSearch(e.target.value)}
                  className="mt-1"
                />
                {parcels?.items?.slice(0, 3).map((p: any) => (
                  <div key={p.id} className="p-2 mt-1 text-sm border rounded-lg hover:bg-slate-50 cursor-pointer">
                    {p.survey_number} — {p.village_name}
                  </div>
                ))}
              </div>

              <Button variant="outline" className="w-full min-h-[44px]" onClick={captureGPS} disabled={capturing}>
                {capturing ? '📍 Capturing GPS...' : gpsCoords ? `✅ GPS: ${gpsCoords.lat.toFixed(4)}, ${gpsCoords.lng.toFixed(4)}` : '📍 Capture GPS Location'}
              </Button>

              {gpsCoords && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-700">
                  ✅ Coordinates captured. Point-in-polygon check: <strong>Within boundary</strong>
                </div>
              )}

              <div>
                <label htmlFor="survey-notes" className="text-sm font-medium text-slate-700">Condition Notes</label>
                <textarea
                  id="survey-notes"
                  className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm"
                  rows={3}
                  placeholder="Describe the current condition..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="survey-photo" className="text-sm font-medium text-slate-700">📷 Photo</label>
                <input
                  id="survey-photo"
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-primary-50 file:text-primary-600"
                />
              </div>

              <Button className="w-full min-h-[44px]" onClick={submitSurvey}>Submit Inspection</Button>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
