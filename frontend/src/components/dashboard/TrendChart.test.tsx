import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TrendChart } from './TrendChart';

// Mock recharts ResponsiveContainer to avoid layout issues in tests
vi.mock('recharts', async () => {
  const actual = await vi.importActual('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  };
});

const statusData = [
  { name: 'Active', value: 12 },
  { name: 'Completed', value: 8 },
  { name: 'Pending', value: 5 },
];

const priorityData = [
  { name: 'High', value: 3 },
  { name: 'Medium', value: 7 },
  { name: 'Low', value: 15 },
];

describe('TrendChart', () => {
  it('renders both chart sections', () => {
    render(<TrendChart statusData={statusData} priorityData={priorityData} />);
    expect(screen.getByText('Projects by Status')).toBeInTheDocument();
    expect(screen.getByText('Projects by Priority')).toBeInTheDocument();
  });

  it('renders without crashing with empty data', () => {
    render(<TrendChart statusData={[]} priorityData={[]} />);
    expect(screen.getByText('Projects by Status')).toBeInTheDocument();
    expect(screen.getByText('Projects by Priority')).toBeInTheDocument();
  });

  it('renders responsive containers', () => {
    const { container } = render(<TrendChart statusData={statusData} priorityData={priorityData} />);
    const containers = container.querySelectorAll('[data-testid="responsive-container"]');
    expect(containers.length).toBe(2);
  });
});
