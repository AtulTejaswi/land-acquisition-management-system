import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DataTable } from './DataTable';

const columns = [
  { key: 'name', header: 'Name' },
  { key: 'status', header: 'Status', sortable: true },
];

const data = [
  { name: 'Project A', status: 'active' },
  { name: 'Project B', status: 'completed' },
];

describe('DataTable', () => {
  it('renders table with data rows', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText('Project A')).toBeInTheDocument();
    expect(screen.getByText('Project B')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('shows empty state when data is empty', () => {
    render(<DataTable columns={columns} data={[]} emptyMessage="Nothing here" />);
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });

  it('shows default empty message', () => {
    render(<DataTable columns={columns} data={[]} />);
    expect(screen.getByText('No data found')).toBeInTheDocument();
  });

  it('shows search input when onSearch is provided', () => {
    const onSearch = vi.fn();
    render(<DataTable columns={columns} data={data} onSearch={onSearch} />);
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  it('does not show search input when onSearch is not provided', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.queryByPlaceholderText('Search...')).not.toBeInTheDocument();
  });

  it('calls onSearch with search term on form submit', () => {
    const onSearch = vi.fn();
    render(<DataTable columns={columns} data={data} onSearch={onSearch} />);
    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.click(screen.getByText('Search'));
    expect(onSearch).toHaveBeenCalledWith('test query');
  });

  it('shows skeleton loading state', () => {
    const { container } = render(<DataTable columns={columns} data={[]} isLoading />);
    const skeletons = container.querySelectorAll('.skeleton');
    expect(skeletons.length).toBe(5);
  });

  it('shows pagination when total > pageSize', () => {
    const onPageChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={data}
        total={50}
        page={1}
        pageSize={20}
        onPageChange={onPageChange}
      />,
    );
    expect(screen.getByText('Showing 1–20 of 50')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('Previous')).toBeInTheDocument();
  });

  it('calls onPageChange when Next is clicked', () => {
    const onPageChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={data}
        total={50}
        page={1}
        pageSize={20}
        onPageChange={onPageChange}
      />,
    );
    fireEvent.click(screen.getByText('Next'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('calls onSort when sortable column header is clicked', () => {
    const onSort = vi.fn();
    render(<DataTable columns={columns} data={data} onSort={onSort} />);
    fireEvent.click(screen.getByText('Status'));
    expect(onSort).toHaveBeenCalledWith('status', 'asc');
  });

  it('calls onRowClick when a row is clicked', () => {
    const onRowClick = vi.fn();
    render(<DataTable columns={columns} data={data} onRowClick={onRowClick} />);
    fireEvent.click(screen.getByText('Project A'));
    expect(onRowClick).toHaveBeenCalledWith(data[0]);
  });

  it('renders custom column render function', () => {
    const customColumns = [
      { key: 'name', header: 'Name', render: (item: any) => <strong>{item.name}</strong> },
    ];
    render(<DataTable columns={customColumns} data={data} />);
    const strong = screen.getByText('Project A');
    expect(strong.tagName).toBe('STRONG');
  });
});
