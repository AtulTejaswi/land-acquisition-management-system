import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../store/AuthContext';
import TrackStatus from '../pages/citizen/TrackStatus';

// Mock react-i18next to return translation keys as values
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en', changeLanguage: vi.fn() },
  }),
  Trans: ({ children }: any) => children,
}));

// Mock the API module - use absolute path to match both test and component imports
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock the auth service so getMe returns the cached user
vi.mock('@/services/auth', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    getMe: vi.fn(),
    forgotPassword: vi.fn(),
  },
}));

import api from '@/services/api';
import { authService } from '@/services/auth';

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
    const mockUser = {
      id: 'c1',
      full_name: 'Ganesh Pattnaik',
      email: 'ganesh@email.com',
      phone: '9876543210',
      role_name: 'citizen',
      state_id: 's1',
      state_name: 'Odisha',
      district_id: 'd1',
      district_name: 'Khordha',
      agency_name: null,
      is_active: true,
    };
    localStorage.setItem('nlams_user', JSON.stringify(mockUser));
    (authService.getMe as any).mockResolvedValue(mockUser);

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

    expect(screen.getByText(/citizen\.trackStatus\.title/)).toBeInTheDocument();
    expect(screen.getAllByText(/citizen\.trackStatus\.portal/).length).toBeGreaterThanOrEqual(1);
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
      expect(screen.getByText('citizen.trackStatus.noParcels')).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});
