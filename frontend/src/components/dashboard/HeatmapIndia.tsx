import React from 'react';
import { Link } from 'react-router-dom';

interface StateProgress {
  state_id: string;
  state_name: string;
  code: string;
  total_projects: number;
  completed: number;
  progress_pct: number;
}

interface HeatmapIndiaProps {
  stateProgress: StateProgress[];
}

export function HeatmapIndia({ stateProgress }: HeatmapIndiaProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-slate-900">
          🇮🇳 India Heatmap — State-wise Acquisition Progress
        </h3>
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-semibold">
          AI Insights • Beta
        </span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {stateProgress.map((sp) => (
          <Link
            key={sp.state_id}
            to="/state/dashboard"
            className="group rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all hover:border-primary-300"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-slate-900">{sp.state_name}</span>
              <span className="text-xs text-slate-400">{sp.code}</span>
            </div>
            <div className="text-2xl font-bold tabular-nums text-slate-900">
              {sp.total_projects}
            </div>
            <div className="text-xs text-slate-500">{sp.completed} completed</div>
            <div className="mt-2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${Math.min(sp.progress_pct, 100)}%`,
                  backgroundColor:
                    sp.progress_pct > 50
                      ? '#10B981'
                      : sp.progress_pct > 20
                        ? '#F59E0B'
                        : '#94A3B8',
                }}
              />
            </div>
            <div className="text-xs text-slate-400 mt-1">{sp.progress_pct}% progress</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
