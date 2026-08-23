import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { Project, PaginatedResponse } from '../types';

interface ProjectFilters {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  priority?: string;
  state_id?: string;
  district_id?: string;
  category?: string;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export function useProjects(filters: ProjectFilters = {}) {
  return useQuery<PaginatedResponse<Project>>({
    queryKey: ['projects', filters],
    queryFn: async () => {
      const params: Record<string, any> = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') params[k] = v;
      });
      const { data } = await api.get('/projects', { params });
      return data;
    },
  });
}

export function useProject(id: string | undefined) {
  return useQuery<Project>({
    queryKey: ['project', id],
    queryFn: async () => {
      const { data } = await api.get(`/projects/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Project>) => {
      const { data: result } = await api.post('/projects', data);
      return result;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });
}

export function useUpdateProject() {
  const qc = useQueryClient();
  return useMutation<
    any,
    { id: string; data: Partial<Project> },
    any
  >({
    mutationFn: async ({ id, data }) => {
      const { data: result } = await api.patch(`/projects/${id}`, data);
      return result;
    },
    onSuccess: (_: any, vars: { id: string }) => {
      qc.invalidateQueries({ queryKey: ['projects'] });
      qc.invalidateQueries({ queryKey: ['project', vars.id] });
    },
  });
}
