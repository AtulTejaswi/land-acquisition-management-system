import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StageProgress } from './StageProgress';

describe('StageProgress', () => {
  it('renders all four stage labels', () => {
    render(<StageProgress currentStage="identification" />);
    expect(screen.getByText('Identification')).toBeInTheDocument();
    expect(screen.getByText('Verification')).toBeInTheDocument();
    expect(screen.getByText('Benefit Disbursement')).toBeInTheDocument();
    expect(screen.getByText('Resettled')).toBeInTheDocument();
  });

  it('marks completed stages with checkmark', () => {
    const { container } = render(<StageProgress currentStage="benefit_disbursement" />);
    const checkmarks = container.querySelectorAll('.bg-emerald-500');
    // Identification and Verification are completed (idx 0 and 1)
    expect(checkmarks.length).toBeGreaterThanOrEqual(2);
  });

  it('marks current stage with blue', () => {
    const { container } = render(<StageProgress currentStage="verification" />);
    const currentStages = container.querySelectorAll('.bg-blue-500');
    expect(currentStages.length).toBe(1);
  });

  it('marks future stages as not completed', () => {
    const { container } = render(<StageProgress currentStage="identification" />);
    const futureStages = container.querySelectorAll('.border-slate-300');
    expect(futureStages.length).toBeGreaterThanOrEqual(3);
  });

  it('renders with compact mode', () => {
    render(<StageProgress currentStage="verification" compact />);
    expect(screen.getByText('Verification')).toBeInTheDocument();
  });

  it('highlights the last stage correctly when at resettled', () => {
    const { container } = render(<StageProgress currentStage="resettled" />);
    // When currentStage='resettled' (idx=3), stages 0-2 are completed, stage 3 is current
    const completedCircles = container.querySelectorAll('.bg-emerald-500.rounded-full');
    expect(completedCircles.length).toBe(3);
    // The current (resettled) stage is blue
    const currentCircle = container.querySelectorAll('.bg-blue-500.rounded-full');
    expect(currentCircle.length).toBe(1);
  });

  it('renders step numbers for non-completed stages', () => {
    const { container } = render(<StageProgress currentStage="identification" />);
    // Current stage shows "1", future show "2", "3", "4"
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
