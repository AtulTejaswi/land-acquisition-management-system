import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders status text correctly', () => {
    render(<StatusBadge status="active" />);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders status with underscores converted to spaces', () => {
    render(<StatusBadge status="under_review" />);
    expect(screen.getByText('Under Review')).toBeInTheDocument();
  });

  it('renders pending status', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('renders completed status', () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('renders rejected status', () => {
    render(<StatusBadge status="rejected" />);
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('renders verified status', () => {
    render(<StatusBadge status="verified" />);
    expect(screen.getByText('Verified')).toBeInTheDocument();
  });

  it('renders disputed status', () => {
    render(<StatusBadge status="disputed" />);
    expect(screen.getByText('Disputed')).toBeInTheDocument();
  });

  it('renders priority colors for low', () => {
    render(<StatusBadge status="low" type="priority" />);
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  it('renders priority colors for critical', () => {
    render(<StatusBadge status="critical" type="priority" />);
    expect(screen.getByText('Critical')).toBeInTheDocument();
  });

  it('applies status color classes', () => {
    const { container } = render(<StatusBadge status="active" />);
    const badge = container.querySelector('span');
    expect(badge?.className).toContain('bg-blue-100');
    expect(badge?.className).toContain('text-blue-700');
  });

  it('applies priority color classes', () => {
    const { container } = render(<StatusBadge status="high" type="priority" />);
    const badge = container.querySelector('span');
    expect(badge?.className).toContain('bg-amber-100');
    expect(badge?.className).toContain('text-amber-700');
  });

  it('has rounded-full class for badge styling', () => {
    const { container } = render(<StatusBadge status="draft" />);
    const badge = container.querySelector('span');
    expect(badge?.className).toContain('rounded-full');
  });
});
