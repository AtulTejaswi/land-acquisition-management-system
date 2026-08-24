import React from 'react';

const STAGE_ORDER = ['identification', 'verification', 'benefit_disbursement', 'resettled'];

const STAGE_LABELS: Record<string, string> = {
  identification: 'Identification',
  verification: 'Verification',
  benefit_disbursement: 'Benefit Disbursement',
  resettled: 'Resettled',
};

interface StageProgressProps {
  currentStage: string;
  compact?: boolean;
}

export function StageProgress({ currentStage, compact = false }: StageProgressProps) {
  const currentIdx = STAGE_ORDER.indexOf(currentStage);
  const width = compact ? 100 : 120;

  return (
    <div className="flex items-center gap-0">
      {STAGE_ORDER.map((stage, idx) => {
        const isCompleted = idx < currentIdx;
        const isCurrent = idx === currentIdx;
        return (
          <React.Fragment key={stage}>
            <div
              className="flex flex-col items-center flex-shrink-0"
              style={{ width: `${width}px` }}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-xs font-bold ${
                  isCompleted
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : isCurrent
                      ? 'bg-blue-500 border-blue-500 text-white pulse-dot'
                      : 'bg-white border-slate-300 text-slate-400'
                }`}
              >
                {isCompleted ? '✓' : idx + 1}
              </div>
              <span
                className={`mt-1.5 text-[10px] text-center leading-tight ${
                  isCurrent
                    ? 'text-blue-600 font-semibold'
                    : isCompleted
                      ? 'text-emerald-600'
                      : 'text-slate-400'
                }`}
              >
                {STAGE_LABELS[stage]}
              </span>
            </div>
            {idx < STAGE_ORDER.length - 1 && (
              <div
                className={`h-0.5 flex-1 -mt-5 ${
                  idx < currentIdx ? 'bg-emerald-500' : 'bg-slate-200'
                }`}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
