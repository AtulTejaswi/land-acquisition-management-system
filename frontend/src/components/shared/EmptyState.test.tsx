import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { EmptyState } from './EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No results" />);
    expect(screen.getByText('No results')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<EmptyState title="No results" description="Try adjusting your filters" />);
    expect(screen.getByText('Try adjusting your filters')).toBeInTheDocument();
  });

  it('does not render description when not provided', () => {
    render(<EmptyState title="No results" />);
    expect(screen.queryByText(/Try adjusting/)).not.toBeInTheDocument();
  });

  it('renders custom icon', () => {
    render(<EmptyState title="Empty" icon="📭" />);
    expect(screen.getByText('📭')).toBeInTheDocument();
  });

  it('renders default icon when not provided', () => {
    const { container } = render(<EmptyState title="Empty" />);
    // Default icon is 📭
    expect(container.textContent).toContain('📭');
  });

  it('renders action when provided', () => {
    render(<EmptyState title="Empty" action={<button>Create New</button>} />);
    expect(screen.getByText('Create New')).toBeInTheDocument();
  });

  it('does not render action when not provided', () => {
    const { container } = render(<EmptyState title="Empty" />);
    expect(container.querySelector('button')).not.toBeInTheDocument();
  });
});
