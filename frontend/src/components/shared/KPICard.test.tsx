import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KPICard } from './KPICard';

describe('KPICard', () => {
  it('renders label and value', () => {
    render(<KPICard label="Total Projects" value={42} />);
    expect(screen.getByText('Total Projects')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders string value', () => {
    render(<KPICard label="Status" value="Active" />);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders positive change with up arrow', () => {
    render(<KPICard label="Growth" value={100} change={12} changeLabel="vs last month" />);
    expect(screen.getByText('↑ 12%')).toBeInTheDocument();
    expect(screen.getByText('vs last month')).toBeInTheDocument();
  });

  it('renders negative change with down arrow', () => {
    render(<KPICard label="Revenue" value={50} change={-5} changeLabel="vs last quarter" />);
    expect(screen.getByText('↓ 5%')).toBeInTheDocument();
  });

  it('applies emerald color class for positive change', () => {
    const { container } = render(<KPICard label="Test" value={1} change={10} />);
    const changeEl = container.querySelector('.text-emerald-600');
    expect(changeEl).toBeInTheDocument();
  });

  it('applies red color class for negative change', () => {
    const { container } = render(<KPICard label="Test" value={1} change={-10} />);
    const changeEl = container.querySelector('.text-red-600');
    expect(changeEl).toBeInTheDocument();
  });

  it('does not render change indicator when change is undefined', () => {
    const { container } = render(<KPICard label="Test" value={1} />);
    expect(container.querySelector('.text-emerald-600')).not.toBeInTheDocument();
    expect(container.querySelector('.text-red-600')).not.toBeInTheDocument();
  });

  it('does not render changeLabel when change is undefined', () => {
    render(<KPICard label="Test" value={1} changeLabel="something" />);
    expect(screen.queryByText('something')).not.toBeInTheDocument();
  });
});
