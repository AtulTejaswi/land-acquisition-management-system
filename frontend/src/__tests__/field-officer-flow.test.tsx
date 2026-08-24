import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../store/AuthContext';
import MobileHome from '../pages/field/MobileHome';

// Mock the API module
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import api from '@/services/api';

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

describe('Field Officer Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('nlams_access_token', 'mock-token');
    localStorage.setItem('nlams_user', JSON.stringify({
      id: 'fo1',
      full_name: 'Rahul Sharma',
      email: 'rahul.f@nlams.gov.in',
      phone: '9876543212',
      role_name: 'field_officer',
      state_id: 's1',
      state_name: 'Maharashtra',
      district_id: 'd1',
      district_name: 'Nagpur',
      agency_name: null,
      is_active: true,
    }));

    // Mock API responses
    (api.get as any).mockImplementation(() => {
      return Promise.resolve({ data: { items: [] } });
    });

    // Set mobile viewport
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 375 });
    Object.defineProperty(window, 'innerHeight', { writable: true, configurable: true, value: 667 });
  });

  it('renders MobileHome page for field officer', () => {
    renderWithAuth(
      <Routes>
        <Route path="/field/home" element={<MobileHome />} />
      </Routes>,
      ['/field/home'],
    );

    // MobileHome renders the field officer's name
    expect(screen.getByText(/Rahul/)).toBeInTheDocument();
  });

  it('renders navigation links on mobile', () => {
    renderWithAuth(
      <Routes>
        <Route path="/field/home" element={<MobileHome />} />
      </Routes>,
      ['/field/home'],
    );

    const navItems = screen.getAllByRole('link');
    expect(navItems.length).toBeGreaterThan(0);
  });
});
