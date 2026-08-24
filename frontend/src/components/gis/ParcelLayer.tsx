import { useEffect } from 'react';
import maplibregl from 'maplibre-gl';

const VERIFICATION_COLORS: Record<string, string> = {
  pending: '#94A3B8',
  verified: '#10B981',
  disputed: '#F59E0B',
  acquired: '#3B82F6',
};

interface ParcelLayerProps {
  map: maplibregl.Map | null;
  geojsonData: any;
  mapLoaded: boolean;
  onSelectParcel: (parcel: any) => void;
}

export function ParcelLayer({ map, geojsonData, mapLoaded, onSelectParcel }: ParcelLayerProps) {
  useEffect(() => {
    if (!map || !geojsonData || !mapLoaded) return;

    // Remove old layers
    if (map.getLayer('parcels-fill')) map.removeLayer('parcels-fill');
    if (map.getLayer('parcels-outline')) map.removeLayer('parcels-outline');
    if (map.getSource('parcels')) map.removeSource('parcels');

    if (geojsonData.features?.length === 0) return;

    map.addSource('parcels', {
      type: 'geojson',
      data: geojsonData,
    });

    // Fill layer colored by verification_status
    map.addLayer({
      id: 'parcels-fill',
      type: 'fill',
      source: 'parcels',
      paint: {
        'fill-color': [
          'match',
          ['get', 'verification_status'],
          'pending', VERIFICATION_COLORS.pending,
          'verified', VERIFICATION_COLORS.verified,
          'disputed', VERIFICATION_COLORS.disputed,
          'acquired', VERIFICATION_COLORS.acquired,
          '#94A3B8',
        ],
        'fill-opacity': 0.4,
      },
    });

    // Outline layer
    map.addLayer({
      id: 'parcels-outline',
      type: 'line',
      source: 'parcels',
      paint: {
        'line-color': [
          'match',
          ['get', 'verification_status'],
          'pending', VERIFICATION_COLORS.pending,
          'verified', VERIFICATION_COLORS.verified,
          'disputed', VERIFICATION_COLORS.disputed,
          'acquired', VERIFICATION_COLORS.acquired,
          '#94A3B8',
        ],
        'line-width': 2,
      },
    });

    // Click handler
    const handleClick = (e: any) => {
      if (e.features?.length > 0) {
        onSelectParcel(e.features[0].properties);
      }
    };
    map.on('click', 'parcels-fill', handleClick);

    // Fit bounds to features
    if (geojsonData.features.length > 0) {
      const coords: [number, number][] = [];
      for (const f of geojsonData.features) {
        if (f.geometry?.coordinates) {
          const ring: number[][] = f.geometry.type === 'Polygon' ? f.geometry.coordinates[0] : [];
          for (const c of ring) {
            coords.push([c[0], c[1]]);
          }
        }
      }
      if (coords.length > 0) {
        const first = coords[0];
        const bounds = coords.reduce(
          (b, c) => b.extend(c as [number, number]),
          new maplibregl.LngLatBounds(first as [number, number], first as [number, number]),
        );
        map.fitBounds(bounds, { padding: 50 });
      }
    }

    return () => {
      map.off('click', 'parcels-fill', handleClick);
    };
  }, [geojsonData, mapLoaded, map, onSelectParcel]);

  return null; // This is a headless component that only manages map layers
}
