import { Clock3 } from "lucide-react";

const FocusCard = ({ focus }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-ink-muted">
          Focus window
        </span>
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-purple-bg)] flex items-center justify-center">
          <Clock3 size={14} className="text-[var(--color-tag-purple-text)]" />
        </div>
      </div>

      {focus ? (
        <>
          <div className="flex items-baseline gap-2 font-mono tabular-nums">
            <span className="text-2xl font-semibold text-ink">{focus.start}</span>
            <span className="text-ink-faint text-sm">→</span>
            <span className="text-2xl font-semibold text-ink">{focus.end}</span>
          </div>
          <span className="inline-block mt-3 px-2 py-0.5 rounded-md text-xs font-medium bg-[var(--color-tag-purple-bg)] text-[var(--color-tag-purple-text)]">
            {focus.duration_minutes} min uninterrupted
          </span>
        </>
      ) : (
        <p className="text-sm text-ink-faint">No open window today.</p>
      )}
    </div>
  );
};

export default FocusCard;
