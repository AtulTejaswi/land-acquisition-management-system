import React from 'react';
import { cn } from '@/lib/utils';
import { STAGES, STAGE_LABELS } from '@/lib/utils';

interface StageStepperProps {
  currentStage: string;
  completedStages?: string[];
}

export function StageStepper({ currentStage, completedStages = [] }: StageStepperProps) {
  const currentIdx = STAGES.indexOf(currentStage);

  return (
    <div className="w-full overflow-x-auto pb-2">
      <div className="flex items-center gap-0 min-w-[900px]">
        {STAGES.map((stage, idx) => {
          const isCompleted = idx < currentIdx || completedStages.includes(stage);
          const isCurrent = idx === currentIdx;
          const isPending = idx > currentIdx;

          return (
            <React.Fragment key={stage}>
              <div className="flex flex-col items-center flex-shrink-0" style={{ width: '65px' }}>
                {/* Circle */}
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center border-2 text-xs font-bold transition-all',
                    isCompleted && 'bg-secondary-500 border-secondary-500 text-white',
                    isCurrent && 'bg-primary-500 border-primary-500 text-white pulse-dot shadow-lg shadow-primary-200',
                    isPending && 'bg-white border-slate-300 text-slate-400',
                  )}
                >
                  {isCompleted ? '✓' : idx + 1}
                </div>
                {/* Label */}
                <span
                  className={cn(
                    'mt-1.5 text-[10px] text-center leading-tight max-w-[65px]',
                    isCurrent && 'text-primary-600 font-semibold',
                    isCompleted && 'text-secondary-600',
                    isPending && 'text-slate-400',
                  )}
                >
                  {STAGE_LABELS[stage]}
                </span>
              </div>
              {/* Connector line */}
              {idx < STAGES.length - 1 && (
                <div
                  className={cn(
                    'h-0.5 flex-1 -mt-5',
                    idx < currentIdx ? 'bg-secondary-500' : 'bg-slate-200',
                  )}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
