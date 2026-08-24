import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../store/AuthContext';
import DistrictDashboard from '../pages/district/DistrictDashboard';
import CompensationDesk from '../pages/district/CompensationDesk';

// Mock the API module
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import api from '@/services/api';

const mockDashboardData = {
  kpis: [
    { label: 'Total Projects', value: 12, change: 5, change_label: 'vs last month' },
    { label: 'Active Projects', value: 8, change: 2, change_label: 'vs last month' },
  ],
  projects: [
    { id: 'proj1', name: 'NH-44 Expansion', status: 'active', district_name: 'Nagpur' },
  ],
  pending_verifications: 5,
  pending_compensations: 3,
};

const mockCompensationData = {
  items: [
    {
      id: 'comp1',
      parcel_id: 'p1',
      total_award: 500000,
      status: 'assessed',
      parcel: { survey_number: '100/A', village_name: 'Wardha' },
    },
  ],
};

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
}

function renderWithAuth(ui: React.ReactElement, initialEntries: string[]) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={initialEntries}>
          {ui}
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  );
}

describe('District Officer Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('nlams_access_token', 'mock-token');
    localStorage.setItem('nlams_user', JSON.stringify({
      id: 'do1',
      full_name: 'Suresh Patil',
      email: 'suresh@nagpur.gov.in',
      phone: '9876543211',
      role_name: 'district_officer',
      state_id: 's1',
      state_name: 'Maharashtra',
      district_id: 'd1',
      district_name: 'Nagpur',
      agency_name: null,
      is_active: true,
    }));

    (api.get as any).mockImplementation((url: string) => {
      if (url.includes('/dashboard/district')) return Promise.resolve({ data: mockDashboardData });
      if (url.includes('/compensation')) return Promise.resolve({ data: mockCompensationData });
      return Promise.resolve({ data: { items: [], kpis: [] } });
    });
  });

  it('renders DistrictDashboard with heading', async () => {
    renderWithAuth(
      <Routes>
        <Route path="/district/dashboard" element={<DistrictDashboard />} />
      </Routes>,
      ['/district/dashboard'],
    );

    await waitFor(() => {
      expect(screen.getByText('Total Projects')).toBeInTheDocument();
    }, { timeout: 5000 });

    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('renders CompensationDesk page', async () => {
    renderWithAuth(
      <Routes>
        <Route path="/district/compensation" element={<CompensationDesk />} />
      </Routes>,
      ['/district/compensation'],
    );

    await waitFor(() => {
      expect(screen.getByText(/Compensation/)).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});
