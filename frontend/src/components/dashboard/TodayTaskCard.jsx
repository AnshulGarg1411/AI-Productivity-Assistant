import { ListTodo } from "lucide-react";
import { PRIORITY_TAG, TASK_STATUS_TAG, pill } from "../../lib/tagStyles";

const TodayTaskCard = ({ tasks }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-green-bg)] flex items-center justify-center">
          <ListTodo size={14} className="text-[var(--color-tag-green-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Today's tasks</h2>
      </div>

      {tasks.length === 0 && (
        <p className="text-sm text-ink-faint">No tasks scheduled today.</p>
      )}

      <div className="space-y-1">
        {tasks.map((task, index) => (
          <div
            key={index}
            className="flex justify-between items-center py-2.5 px-2 -mx-2 rounded-md hover:bg-surface transition-colors"
          >
            <div className="min-w-0">
              <h3 className="text-sm font-medium text-ink truncate">{task.title}</h3>
              <span className={pill(PRIORITY_TAG[task.priority])}>{task.priority}</span>
            </div>
            <span className={pill(TASK_STATUS_TAG[task.status])}>
              {task.status.replace("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TodayTaskCard;
