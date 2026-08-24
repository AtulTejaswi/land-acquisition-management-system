import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a fresh QueryClient for each test to avoid cache leaks
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[];
}

function AllProviders({ children, initialEntries = ['/'] }: { children: React.ReactNode; initialEntries?: string[] }) {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

export function renderWithProviders(ui: ReactElement, options: CustomRenderOptions = {}) {
  const { initialEntries, ...renderOptions } = options;
  return render(ui, {
    wrapper: ({ children }) => <AllProviders initialEntries={initialEntries}>{children}</AllProviders>,
    ...renderOptions,
  });
}

// Mock user data for different roles
export const mockUsers = {
  citizen: {
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
  },
  district_officer: {
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
  },
  field_officer: {
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
  },
};
