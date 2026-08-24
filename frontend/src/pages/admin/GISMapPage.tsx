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

export default function GISMapPage() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<maplibregl.Map | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<any>(null);

  const { data: geojsonData } = useQuery({
    queryKey: ['gis-parcels'],
    queryFn: async () => {
      const { data } = await api.get('/gis/parcels/geojson');
      return data;
    },
  });

  useEffect(() => {
    if (!mapContainer.current) return undefined;

    const instance = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      center: [79.0882, 21.1458],
      zoom: 5,
    });

    instance.addControl(new maplibregl.NavigationControl(), 'top-right');

    instance.on('load', () => {
      setMap(instance);
    });

    return () => {
      instance.remove();
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">GIS Parcel Map</h1>
          <p className="text-slate-500 text-sm">Visualize land parcels on interactive map</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Import GeoJSON
          </Button>
          <Button size="sm">+ Draw Parcel</Button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-4 items-center text-xs">
        {Object.entries(VERIFICATION_COLORS).map(([status, color]) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: color }} />
            <span className="text-slate-600 capitalize">{status}</span>
          </div>
        ))}
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
                <span className="text-slate-500">Status:</span>
                <span className="font-medium ml-1 capitalize">
                  {selectedParcel.verification_status}
                </span>
              </div>
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
