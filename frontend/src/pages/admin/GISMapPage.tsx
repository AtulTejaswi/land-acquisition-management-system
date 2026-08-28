import React, { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { ParcelLayer } from '../../components/gis/ParcelLayer';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const VERIFICATION_COLORS: Record<string, string> = {
  pending: '#94A3B8',
  verified: '#10B981',
  disputed: '#F59E0B',
  acquired: '#3B82F6',
};

const OWNERSHIP_COLORS: Record<string, string> = {
  private: '#8B5CF6',
  govt: '#F97316',
  disputed: '#EF4444',
  common: '#06B6D4',
};

export default function GISMapPage() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<maplibregl.Map | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<any>(null);
  const [colorBy, setColorBy] = useState<'verification' | 'ownership'>('verification');

  const { data: geojsonData } = useQuery({
    queryKey: ['gis-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/gis/parcels/geojson');
      return data;
    },
  });

  useEffect(() => {
    if (!mapContainer.current) return undefined;

    // Center on Khordha, Odisha (where the real data is)
    // Using OpenFreeMap — free vector tiles, no API key, no registration
    const instance = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center: [85.6226, 20.1863], // Khordha, Odisha
      zoom: 11,
    });

    instance.addControl(new maplibregl.NavigationControl(), 'top-right');

    instance.on('load', () => {
      setMap(instance);
    });

    return () => {
      instance.remove();
    };
  }, []);

  const colors = colorBy === 'verification' ? VERIFICATION_COLORS : OWNERSHIP_COLORS;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">GIS Parcel Map</h1>
          <p className="text-slate-500 text-sm">
            Khordha District, Odisha — Village-level parcel locations (approximate markers, not surveyed boundaries)
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Import GeoJSON
          </Button>
          <Button size="sm">+ Draw Parcel</Button>
        </div>
      </div>

      {/* Legend — toggleable between verification and ownership */}
      <div className="flex flex-wrap gap-4 items-center text-xs">
        <div className="flex items-center gap-2 mr-4">
          <button
            onClick={() => setColorBy('verification')}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              colorBy === 'verification' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Verification
          </button>
          <button
            onClick={() => setColorBy('ownership')}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              colorBy === 'ownership' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Ownership
          </button>
        </div>
        {Object.entries(colors).map(([status, color]) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-slate-600 capitalize">{status}</span>
          </div>
        ))}
        <span className="text-slate-400 text-[10px] ml-2">
          ⚠️ Markers are village-level approximations
        </span>
      </div>

      <div className="flex gap-4 h-[calc(100vh-280px)]">
        {/* Map */}
        <div className="flex-1 rounded-xl overflow-hidden border border-slate-200">
          <div ref={mapContainer} className="w-full h-full" />
          <ParcelLayer
            map={map}
            geojsonData={geojsonData}
            mapLoaded={!!map}
            onSelectParcel={setSelectedParcel}
            colorBy={colorBy}
          />
        </div>

        {/* Side drawer */}
        {selectedParcel && (
          <Card className="w-80 h-full overflow-y-auto">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Parcel Details</CardTitle>
                <button
                  onClick={() => setSelectedParcel(null)}
                  className="text-slate-400 hover:text-slate-600"
                  aria-label="Close parcel details"
                >
                  ✕
                </button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <span className="text-slate-500">Survey No:</span>
                <span className="font-medium ml-1">{selectedParcel.survey_number}</span>
              </div>
              {selectedParcel.survey_number_or && (
                <div>
                  <span className="text-slate-500">Survey No (Odia):</span>
                  <span className="font-medium ml-1">{selectedParcel.survey_number_or}</span>
                </div>
              )}
              <div>
                <span className="text-slate-500">Area:</span>
                <span className="font-medium ml-1">{selectedParcel.area_hectares} ha</span>
              </div>
              <div>
                <span className="text-slate-500">Village:</span>
                <span className="font-medium ml-1">
                  {selectedParcel.village_name || '—'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">District:</span>
                <span className="font-medium ml-1">
                  {selectedParcel.district_name || '—'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Land Type:</span>
                <span className="font-medium ml-1 capitalize">
                  {selectedParcel.land_type}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Ownership:</span>
                <span className="font-medium ml-1 capitalize">
                  {selectedParcel.ownership_status}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Status:</span>
                <span className="font-medium ml-1 capitalize">
                  {selectedParcel.verification_status}
                </span>
              </div>
              {selectedParcel.owner_count !== undefined && (
                <div>
                  <span className="text-slate-500">Owners:</span>
                  <span className="font-medium ml-1">
                    {selectedParcel.owner_count}
                    {selectedParcel.owner_count > 1 && (
                      <span className="text-xs text-slate-400 ml-1">(co-owned)</span>
                    )}
                  </span>
                </div>
              )}
              <Button variant="outline" size="sm" className="w-full mt-2">
                View Documents
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
