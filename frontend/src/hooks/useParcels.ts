import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { LandParcel, PaginatedResponse, GeoJSONFeatureCollection } from '../types';

interface ParcelFilters {
  page?: number;
  page_size?: number;
  search?: string;
  project_id?: string;
  village_id?: string;
  district_id?: string;
  state_id?: string;
  land_type?: string;
  verification_status?: string;
  bbox?: string;
}

export function useParcels(filters: ParcelFilters = {}) {
  return useQuery<PaginatedResponse<LandParcel>>({
    queryKey: ['parcels', filters],
    queryFn: async () => {
      const params: Record<string, any> = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') params[k] = v;
      });
      const { data } = await api.get('/parcels', { params });
      return data;
    },
  });
}

export function useParcelGeoJSON(filters?: { project_id?: string; district_id?: string; state_id?: string }) {
  return useQuery<GeoJSONFeatureCollection>({
    queryKey: ['gis-parcels', filters],
    queryFn: async () => {
      const params: Record<string, any> = {};
      if (filters) {
        Object.entries(filters).forEach(([k, v]) => {
          if (v) params[k] = v;
        });
      }
      const { data } = await api.get('/gis/parcels/geojson', { params });
      return data;
    },
  });
}

export function useCreateParcel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: any) => {
      const { data: result } = await api.post('/parcels', data);
      return result;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['parcels'] }),
  });
}
