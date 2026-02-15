interface ProgressBarProps {
  completed: number;
  total: number;
  failed?: number;
}

export function ProgressBar({ completed, total, failed = 0 }: ProgressBarProps) {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  const failPct = total > 0 ? Math.round((failed / total) * 100) : 0;

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>
          {completed}/{total} completed
        </span>
        <span>{pct}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div className="flex h-full">
          <div
            className="bg-green-500 h-full transition-all duration-300"
            style={{ width: `${pct}%` }}
          />
          {failPct > 0 && (
            <div
              className="bg-red-400 h-full transition-all duration-300"
              style={{ width: `${failPct}%` }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
