import { CheckSquare } from "lucide-react";

const Stat = ({ label, value, tone }) => (
  <div className="flex justify-between items-center py-2">
    <span className="text-sm text-ink-muted">{label}</span>
    <span className={`text-sm font-semibold font-mono tabular-nums ${tone || "text-ink"}`}>
      {value}
    </span>
  </div>
);

const TaskCard = ({ tasks }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-orange-bg)] flex items-center justify-center">
          <CheckSquare size={14} className="text-[var(--color-tag-orange-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Tasks</h2>
      </div>

      <div className="divide-y divide-border">
        <Stat label="Pending" value={tasks.pending} />
        <Stat label="Completed" value={tasks.completed} tone="text-[var(--color-tag-green-text)]" />
        <Stat label="Overdue" value={tasks.overdue} tone="text-[var(--color-tag-red-text)]" />
        <Stat
          label="High priority"
          value={tasks.high_priority}
          tone="text-[var(--color-tag-orange-text)]"
        />
      </div>
    </div>
  );
};

export default TaskCard;
