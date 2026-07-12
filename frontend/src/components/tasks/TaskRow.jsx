import { CheckCircle2, Circle, Pencil, Trash2, Mail, CalendarDays, Sparkles } from "lucide-react";
import { format, isPast } from "date-fns";
import {
  PRIORITY_TAG,
  CATEGORY_TAG,
  pill,
} from "../../lib/tagStyles";

const SOURCE_BADGE = {
  EMAIL: {
    icon: Mail,
    label: "Created from an email",
    className: "bg-[var(--color-tag-blue-bg)] text-[var(--color-tag-blue-text)]",
  },
  CALENDAR: {
    icon: CalendarDays,
    label: "Created from a meeting",
    className: "bg-[var(--color-tag-purple-bg)] text-[var(--color-tag-purple-text)]",
  },
  AI: {
    icon: Sparkles,
    label: "Created by the AI assistant",
    className: "bg-[var(--color-tag-yellow-bg)] text-[var(--color-tag-yellow-text)]",
  },
};

const TaskRow = ({ task, onComplete, onEdit, onDelete }) => {
  const isCompleted = task.status === "COMPLETED";
  const overdue =
    !isCompleted && task.due_date && isPast(new Date(task.due_date));
  const sourceBadge = SOURCE_BADGE[task.source];

  return (
    <div className="group grid grid-cols-[minmax(0,1fr)_110px_90px_130px_36px] items-center gap-3 px-3 py-2.5 border-b border-border hover:bg-surface transition-colors">
      {/* Name column: checkbox + title */}
      <div className="flex items-center gap-2.5 min-w-0">
        <button
          onClick={() => !isCompleted && onComplete(task)}
          className="shrink-0"
          title={isCompleted ? "Completed" : "Mark as complete"}
        >
          {isCompleted ? (
            <CheckCircle2 size={17} className="text-[var(--color-tag-green-text)]" />
          ) : (
            <Circle size={17} className="text-ink-faint hover:text-accent transition-colors" />
          )}
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <span
              className={`text-sm truncate ${
                isCompleted ? "line-through text-ink-faint" : "text-ink"
              }`}
            >
              {task.title}
            </span>
            {sourceBadge && (
              <span
                title={sourceBadge.label}
                className={`inline-flex items-center justify-center w-4 h-4 rounded shrink-0 ${sourceBadge.className}`}
              >
                <sourceBadge.icon size={11} />
              </span>
            )}
          </div>
          {task.description && (
            <span className="text-xs text-ink-faint truncate block">
              {task.description}
            </span>
          )}
        </div>
      </div>

      {/* Category */}
      <div>
        <span className={pill(CATEGORY_TAG[task.category])}>{task.category}</span>
      </div>

      {/* Priority */}
      <div>
        <span className={pill(PRIORITY_TAG[task.priority])}>{task.priority}</span>
      </div>

      {/* Due date */}
      <div className="text-xs font-mono tabular-nums text-ink-muted">
        <span className={overdue ? "text-[var(--color-tag-red-text)] font-medium" : ""}>
          {format(new Date(task.due_date), "MMM d")}
        </span>
        {overdue && <span className="ml-1.5 text-[var(--color-tag-red-text)]">Overdue</span>}
      </div>

      {/* Actions - reveal on row hover */}
      <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity justify-end">
        <button
          onClick={() => onEdit(task)}
          className="p-1.5 text-ink-faint hover:text-ink hover:bg-surface-hover rounded"
        >
          <Pencil size={13} />
        </button>
        <button
          onClick={() => onDelete(task)}
          className="p-1.5 text-ink-faint hover:text-[var(--color-tag-red-text)] hover:bg-surface-hover rounded"
        >
          <Trash2 size={13} />
        </button>
      </div>
    </div>
  );
};

export default TaskRow;
