import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { HeatmapIndia } from './HeatmapIndia';

const stateProgress = [
  { state_id: '1', state_name: 'Odisha', code: 'OD', total_projects: 249, completed: 249, progress_pct: 100 },
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
    expect(screen.getByText('Odisha')).toBeInTheDocument();
  });

  it('renders project counts', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('249')).toBeInTheDocument();
  });

  it('renders completed counts', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('249 completed')).toBeInTheDocument();
  });

  it('renders progress percentages', () => {
    render(
      <MemoryRouter>
        <HeatmapIndia stateProgress={stateProgress} />
      </MemoryRouter>,
    );
    expect(screen.getByText('100% progress')).toBeInTheDocument();
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
    expect(links.length).toBe(1);
    links.forEach((link) => {
      expect(link).toHaveAttribute('href', '/state/dashboard');
    });
  });
});
