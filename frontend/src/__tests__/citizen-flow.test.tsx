import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../store/AuthContext';
import TrackStatus from '../pages/citizen/TrackStatus';

// Mock the API module - use absolute path to match both test and component imports
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import api from '@/services/api';

const mockParcels = {
  items: [
    {
      id: 'p1',
      survey_number: '100/A',
      village_name: 'Wardha',
      district_name: 'Nagpur',
      area_hectares: 2.5,
      land_type: 'agricultural',
      verification_status: 'verified',
    },
    {
      id: 'p2',
      survey_number: '200/B',
      village_name: 'Amravati',
      district_name: 'Nagpur',
      area_hectares: 1.2,
      land_type: 'residential',
      verification_status: 'pending',
    },
  ],
};

const mockCompensations = {
  items: [
    {
      id: 'comp1',
      parcel_id: 'p1-uuid-here',
      total_award: 500000,
      market_value: 400000,
      solatium: 100000,
      status: 'approved',
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

describe('Citizen Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Set up logged-in citizen in localStorage
    localStorage.setItem('nlams_access_token', 'mock-token');
    localStorage.setItem('nlams_user', JSON.stringify({
      id: 'c1',
      full_name: 'Ganesh Kumar',
      email: 'ganesh@email.com',
      phone: '9876543210',
      role_name: 'citizen',
      state_id: 's1',
      state_name: 'Maharashtra',
      district_id: 'd1',
      district_name: 'Nagpur',
      agency_name: null,
      is_active: true,
    }));

    // Mock all three API calls that TrackStatus makes
    (api.get as any).mockImplementation((url: string) => {
      if (url === '/parcels') return Promise.resolve({ data: mockParcels });
      if (url === '/compensation') return Promise.resolve({ data: mockCompensations });
      if (url === '/payments') return Promise.resolve({ data: { items: [] } });
      return Promise.resolve({ data: { items: [] } });
    });
  });

  it('renders TrackStatus page heading', async () => {
    renderWithAuth(
      <Routes>
        <Route path="/citizen/track" element={<TrackStatus />} />
      </Routes>,
      ['/citizen/track'],
    );

    expect(screen.getByText(/Track Your Status/)).toBeInTheDocument();
    expect(screen.getByText(/Citizen Transparency Portal/)).toBeInTheDocument();
  });

  it('renders parcel data after loading', async () => {
    renderWithAuth(
      <Routes>
        <Route path="/citizen/track" element={<TrackStatus />} />
      </Routes>,
      ['/citizen/track'],
    );

    await waitFor(() => {
      expect(screen.getByText(/100\/A/)).toBeInTheDocument();
    }, { timeout: 5000 });

    expect(screen.getByText(/Wardha/)).toBeInTheDocument();
    expect(screen.getByText(/Amravati/)).toBeInTheDocument();
  });

  it('shows empty state when no parcels', async () => {
    (api.get as any).mockImplementation((url: string) => {
      if (url === '/parcels') return Promise.resolve({ data: { items: [] } });
      if (url === '/compensation') return Promise.resolve({ data: { items: [] } });
      if (url === '/payments') return Promise.resolve({ data: { items: [] } });
      return Promise.resolve({ data: { items: [] } });
    });

    renderWithAuth(
      <Routes>
        <Route path="/citizen/track" element={<TrackStatus />} />
      </Routes>,
      ['/citizen/track'],
    );

    await waitFor(() => {
      expect(screen.getByText('No parcels linked to your account yet')).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});
