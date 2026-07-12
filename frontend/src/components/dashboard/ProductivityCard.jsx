import { TrendingUp } from "lucide-react";

const ProductivityCard = ({ productivity }) => {
  const score = productivity?.score ?? 0;

  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-ink-muted">
          Productivity score
        </span>
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-blue-bg)] flex items-center justify-center">
          <TrendingUp size={14} className="text-[var(--color-tag-blue-text)]" />
        </div>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-5xl font-semibold text-ink font-mono tabular-nums">
          {score}
        </span>
        <span className="text-sm text-ink-faint">/ 100</span>
      </div>

      <p className="text-sm text-ink-muted mt-2">{productivity?.status}</p>

      <div className="w-full h-1.5 bg-surface rounded-full mt-4 overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all"
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default ProductivityCard;
