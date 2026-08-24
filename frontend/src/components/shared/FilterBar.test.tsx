import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FilterBar, FilterConfig } from './FilterBar';

const textFilters: FilterConfig[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Type to search...', value: '' },
];

const textFiltersWithValue: FilterConfig[] = [
  { key: 'search', label: 'Search', type: 'text', value: 'hello' },
];

describe('FilterBar', () => {
  it('renders filter labels', () => {
    render(<FilterBar filters={textFilters} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('renders text input with placeholder', () => {
    render(<FilterBar filters={textFilters} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    expect(screen.getByPlaceholderText('Type to search...')).toBeInTheDocument();
  });

  it('uses default placeholder when not provided', () => {
    const filters: FilterConfig[] = [
      { key: 'name', label: 'Name', type: 'text', value: '' },
    ];
    render(<FilterBar filters={filters} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    expect(screen.getByPlaceholderText('Search name...')).toBeInTheDocument();
  });

  it('calls onFilterChange when text input changes', () => {
    const onFilterChange = vi.fn();
    render(<FilterBar filters={textFilters} onFilterChange={onFilterChange} onReset={vi.fn()} />);
    const input = screen.getByPlaceholderText('Type to search...');
    fireEvent.change(input, { target: { value: 'test' } });
    expect(onFilterChange).toHaveBeenCalledWith('search', 'test');
  });

  it('shows Clear Filters button when filters have values', () => {
    render(<FilterBar filters={textFiltersWithValue} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    expect(screen.getByText('✕ Clear Filters')).toBeInTheDocument();
  });

  it('does not show Clear Filters button when no active filters', () => {
    render(<FilterBar filters={textFilters} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    expect(screen.queryByText('✕ Clear Filters')).not.toBeInTheDocument();
  });

  it('calls onReset when Clear Filters is clicked', () => {
    const onReset = vi.fn();
    render(<FilterBar filters={textFiltersWithValue} onFilterChange={vi.fn()} onReset={onReset} />);
    fireEvent.click(screen.getByText('✕ Clear Filters'));
    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it('renders input with current filter value', () => {
    render(<FilterBar filters={textFiltersWithValue} onFilterChange={vi.fn()} onReset={vi.fn()} />);
    // Default placeholder is 'Search search...' (label.toLowerCase())
    const input = screen.getByRole('textbox') as HTMLInputElement;
    expect(input.value).toBe('hello');
  });
});
