import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DocList } from './DocList';

const documents = [
  { id: '1', doc_type: 'dpr', file_name: 'DPR_Report.pdf', file_path: '/uploads/dpr.pdf', file_size: 1048576, version: 1, created_at: '2024-01-15T10:30:00Z' },
  { id: '2', doc_type: 'survey_report', file_name: 'Survey_Notes.docx', file_path: '/uploads/survey.docx', file_size: 512000, version: 2, created_at: '2024-02-20T14:00:00Z' },
  { id: '3', doc_type: 'photo', file_name: 'Site_Photo.jpg', file_path: '/uploads/photo.jpg', file_size: 2048000, version: 1, created_at: '2024-03-10T08:00:00Z' },
];

describe('DocList', () => {
  it('renders document names', () => {
    render(<DocList documents={documents} isLoading={false} />);
    expect(screen.getByText('DPR_Report.pdf')).toBeInTheDocument();
    expect(screen.getByText('Survey_Notes.docx')).toBeInTheDocument();
    expect(screen.getByText('Site_Photo.jpg')).toBeInTheDocument();
  });

  it('renders document type labels', () => {
    const { container } = render(<DocList documents={documents} isLoading={false} />);
    const typeLabels = container.querySelectorAll('.text-xs.text-slate-500');
    // First doc shows 'DPR • v1', second shows 'SURVEY REPORT • v2'
    const allText = Array.from(typeLabels).map(el => el.textContent).join(' ');
    expect(allText).toContain('DPR');
    expect(allText).toContain('SURVEY REPORT');
  });

  it('renders version numbers', () => {
    const { container } = render(<DocList documents={documents} isLoading={false} />);
    const typeLabels = container.querySelectorAll('.text-xs.text-slate-500');
    const allText = Array.from(typeLabels).map(el => el.textContent).join(' ');
    expect(allText).toContain('v1');
    expect(allText).toContain('v2');
  });

  it('renders View links', () => {
    render(<DocList documents={documents} isLoading={false} />);
    const viewLinks = screen.getAllByText('View');
    expect(viewLinks.length).toBe(3);
  });

  it('renders empty state when no documents', () => {
    render(<DocList documents={[]} isLoading={false} />);
    expect(screen.getByText('No documents available')).toBeInTheDocument();
  });

  it('renders custom empty state text', () => {
    render(<DocList documents={[]} isLoading={false} emptyTitle="No files" emptyDescription="Upload something" />);
    expect(screen.getByText('No files')).toBeInTheDocument();
    expect(screen.getByText('Upload something')).toBeInTheDocument();
  });

  it('shows skeleton loading state', () => {
    const { container } = render(<DocList documents={[]} isLoading={true} />);
    const skeletons = container.querySelectorAll('.skeleton');
    expect(skeletons.length).toBe(4);
  });

  it('shows file size when showFileSize is true', () => {
    render(<DocList documents={documents} isLoading={false} showFileSize />);
    expect(screen.getByText('1024 KB')).toBeInTheDocument();
    expect(screen.getByText('500 KB')).toBeInTheDocument();
  });

  it('does not show file size when showFileSize is false', () => {
    render(<DocList documents={documents} isLoading={false} showFileSize={false} />);
    expect(screen.queryByText('1024 KB')).not.toBeInTheDocument();
  });
});
