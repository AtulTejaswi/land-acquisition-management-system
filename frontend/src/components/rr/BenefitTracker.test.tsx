import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BenefitTracker } from './BenefitTracker';

describe('BenefitTracker', () => {
  const defaultProps = {
    displacedStatus: 'completed',
    housingStatus: 'in_progress',
    employmentStatus: 'pending',
  };

  it('renders all benefit labels in grid layout', () => {
    render(<BenefitTracker {...defaultProps} />);
    expect(screen.getByText('Displacement')).toBeInTheDocument();
    expect(screen.getByText('Housing')).toBeInTheDocument();
    expect(screen.getByText('Employment')).toBeInTheDocument();
  });

  it('renders status badges for each benefit', () => {
    render(<BenefitTracker {...defaultProps} />);
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('renders monetary benefit when provided', () => {
    render(<BenefitTracker {...defaultProps} monetaryAmount={500000} />);
    expect(screen.getByText('Monetary Benefit')).toBeInTheDocument();
    expect(screen.getByText('₹5.0L')).toBeInTheDocument();
  });

  it('formats crore amounts correctly', () => {
    render(<BenefitTracker {...defaultProps} monetaryAmount={15000000} />);
    expect(screen.getByText('₹1.5Cr')).toBeInTheDocument();
  });

  it('formats regular amounts correctly', () => {
    render(<BenefitTracker {...defaultProps} monetaryAmount={25000} />);
    expect(screen.getByText('₹25,000')).toBeInTheDocument();
  });

  it('does not render monetary benefit when not provided', () => {
    render(<BenefitTracker {...defaultProps} />);
    expect(screen.queryByText('Monetary Benefit')).not.toBeInTheDocument();
  });

  it('renders in row layout with just badges', () => {
    render(<BenefitTracker {...defaultProps} layout="row" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
    // Labels should not be shown in row layout
    expect(screen.queryByText('Displacement')).not.toBeInTheDocument();
  });
});
