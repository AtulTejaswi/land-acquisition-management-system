import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { HeatmapIndia } from './HeatmapIndia';

const stateProgress = [
  { state_id: '1', state_name: 'Maharashtra', code: 'MH', total_projects: 25, completed: 10, progress_pct: 40 },
  { state_id: '2', state_name: 'Gujarat', code: 'GJ', total_projects: 15, completed: 8, progress_pct: 53 },
  { state_id: '3', state_name: 'Karnataka', code: 'KA', total_projects: 10, completed: 2, progress_pct: 20 },
];

describe('HeatmapIndia', () => {
  it('renders section title', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText(/India Heatmap/)).toBeInTheDocument();
  });

  it('renders state cards with names', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('Maharashtra')).toBeInTheDocument();
    expect(screen.getByText('Gujarat')).toBeInTheDocument();
    expect(screen.getByText('Karnataka')).toBeInTheDocument();
  });

  it('renders project counts', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('renders completed counts', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('10 completed')).toBeInTheDocument();
    expect(screen.getByText('8 completed')).toBeInTheDocument();
  });

  it('renders progress percentages', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('40% progress')).toBeInTheDocument();
    expect(screen.getByText('53% progress')).toBeInTheDocument();
  });

  it('renders Beta label', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
  });

  it('renders links to state dashboard', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    const links = screen.getAllByRole('link');
    expect(links.length).toBe(3);
    links.forEach((link) => {
      expect(link).toHaveAttribute('href', '/state/dashboard');
    });
  });
});
