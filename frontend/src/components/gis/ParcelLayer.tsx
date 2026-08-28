import { useEffect } from 'react';
import maplibregl from 'maplibre-gl';

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

interface ParcelLayerProps {
  map: maplibregl.Map | null;
  geojsonData: any;
  mapLoaded: boolean;
  onSelectParcel: (parcel: any) => void;
  colorBy?: 'verification' | 'ownership';
}

export function ParcelLayer({ map, geojsonData, mapLoaded, onSelectParcel, colorBy = 'verification' }: ParcelLayerProps) {
  useEffect(() => {
    if (!map || !geojsonData || !mapLoaded) return;

    // Remove old layers/sources
    const layerIds = ['parcels-circles', 'parcels-fill', 'parcels-outline'];
    for (const id of layerIds) {
      if (map.getLayer(id)) map.removeLayer(id);
    }
    if (map.getSource('parcels')) map.removeSource('parcels');

    if (!geojsonData.features?.length) return;

    // Check if features are Points or Polygons
    const firstGeom = geojsonData.features[0]?.geometry?.type;
    const isPoint = firstGeom === 'Point';

    map.addSource('parcels', {
      type: 'geojson',
      data: geojsonData,
    });

    const colors = colorBy === 'verification' ? VERIFICATION_COLORS : OWNERSHIP_COLORS;
    const colorField = colorBy === 'verification' ? 'verification_status' : 'ownership_status';

    // Build match expression with only the keys relevant to current colorBy mode
    const matchExpr: (string | number)[] = ['match', ['get', colorField]];
    for (const [key, val] of Object.entries(colors)) {
      matchExpr.push(key, val);
    }
    matchExpr.push('#94A3B8'); // fallback

    if (isPoint) {
      // Circle markers for Point geometry (village-level markers)
      map.addLayer({
        id: 'parcels-circles',
        type: 'circle',
        source: 'parcels',
        paint: {
          'circle-radius': [
            'interpolate', ['linear'], ['coalesce', ['get', 'owner_count'], 1],
            1, 6,
            5, 10,
            10, 14,
          ],
          'circle-color': matchExpr,
          'circle-opacity': 0.75,
          'circle-stroke-width': 1.5,
          'circle-stroke-color': '#ffffff',
        },
      });

      // Click handler
      const handleClick = (e: any) => {
        if (e.features?.length > 0) {
          onSelectParcel(e.features[0].properties);
        }
      };
      const handleEnter = () => { map.getCanvas().style.cursor = 'pointer'; };
      const handleLeave = () => { map.getCanvas().style.cursor = ''; };
      map.on('click', 'parcels-circles', handleClick);
      map.on('mouseenter', 'parcels-circles', handleEnter);
      map.on('mouseleave', 'parcels-circles', handleLeave);

      return () => {
        map.off('click', 'parcels-circles', handleClick);
        map.off('mouseenter', 'parcels-circles', handleEnter);
        map.off('mouseleave', 'parcels-circles', handleLeave);
      };
    } else {
      // Polygon layers (original behavior)
      map.addLayer({
        id: 'parcels-fill',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': matchExpr,
          'fill-opacity': 0.4,
        },
      });

      map.addLayer({
        id: 'parcels-outline',
        type: 'line',
        source: 'parcels',
        paint: {
          'line-color': matchExpr,
          'line-width': 2,
        },
      });

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
    }
  }, [geojsonData, mapLoaded, map, onSelectParcel, colorBy]);

  return null; // Headless component managing map layers
}
