import { useMemo, useState } from "react";
import { Plus, Sparkles } from "lucide-react";

import { useTasksQuery, useTasks } from "../hooks/useTasks";
import { useAuth } from "../contexts/AuthContext";
import TaskRow from "../components/tasks/TaskRow";
import TaskFormModal from "../components/tasks/TaskFormModal";

const FILTERS = [
  { key: "ALL", label: "All" },
  { key: "TODO", label: "To do" },
  { key: "IN_PROGRESS", label: "In progress" },
  { key: "COMPLETED", label: "Completed" },
];

const SOURCE_FILTERS = [
  { key: "ALL", label: "All sources" },
  { key: "MANUAL", label: "Manual" },
  { key: "EMAIL", label: "From email" },
  { key: "CALENDAR", label: "From meetings" },
  { key: "AI", label: "AI assistant" },
];

const Tasks = () => {
  const { data: tasks, isLoading, error } = useTasksQuery();
  const { createMutation, updateMutation, completeMutation, deleteMutation } =
    useTasks();
  const { user } = useAuth();

  const [filter, setFilter] = useState("ALL");
  const [sourceFilter, setSourceFilter] = useState("ALL");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  const filteredTasks = useMemo(() => {
    if (!tasks) return [];
    return tasks.filter((t) => {
      const matchesStatus = filter === "ALL" || t.status === filter;
      const matchesSource = sourceFilter === "ALL" || t.source === sourceFilter;
      return matchesStatus && matchesSource;
    });
  }, [tasks, filter, sourceFilter]);

  const aiCreatedCount = useMemo(() => {
    if (!tasks) return 0;
    return tasks.filter((t) => t.source && t.source !== "MANUAL").length;
  }, [tasks]);

  const openCreateModal = () => {
    setEditingTask(null);
    setIsModalOpen(true);
  };

  const openEditModal = (task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleSubmit = (payload) => {
    if (editingTask) {
      updateMutation.mutate(
        { id: editingTask.id, task: payload },
        { onSuccess: () => setIsModalOpen(false) }
      );
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => setIsModalOpen(false),
      });
    }
  };

  const handleComplete = (task) => {
    completeMutation.mutate({
      id: task.id,
      actualMinutes: task.estimated_minutes,
    });
  };

  const handleDelete = (task) => {
    if (window.confirm(`Delete "${task.title}"?`)) {
      deleteMutation.mutate(task.id);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-sm text-ink-muted">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-sm text-[var(--color-tag-red-text)]">
          Failed to load tasks
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-10 py-8">
      <div className="text-3xl mb-3 leading-none">✅</div>
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-ink tracking-tight">Tasks</h1>
          {aiCreatedCount > 0 && (
            <p className="text-xs text-ink-faint mt-1 flex items-center gap-1">
              <Sparkles size={12} className="text-[var(--color-tag-yellow-text)]" />
              {aiCreatedCount} of these were created automatically from your
              emails, meetings, or the AI assistant
            </p>
          )}
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-1.5 bg-accent text-white text-sm font-medium px-3 py-1.5 rounded-md hover:bg-accent-hover transition-colors"
        >
          <Plus size={15} />
          New
        </button>
      </div>

      <div className="flex items-center justify-between flex-wrap gap-3 mb-4 border-b border-border">
        <div className="flex items-center gap-1">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                filter === f.key
                  ? "border-accent text-ink"
                  : "border-transparent text-ink-muted hover:text-ink"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          className="text-sm border border-border rounded-md px-2 py-1.5 mb-2 bg-canvas text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/40"
        >
          {SOURCE_FILTERS.map((s) => (
            <option key={s.key} value={s.key}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div className="border border-border rounded-lg overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-[minmax(0,1fr)_110px_90px_130px_36px] gap-3 px-3 py-2 bg-surface text-xs font-medium text-ink-muted uppercase tracking-wide">
          <span>Name</span>
          <span>Category</span>
          <span>Priority</span>
          <span>Due</span>
          <span />
        </div>

        {filteredTasks.length === 0 ? (
          <div className="p-10 text-center text-sm text-ink-faint">
            No tasks here yet.
          </div>
        ) : (
          filteredTasks.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onComplete={handleComplete}
              onEdit={openEditModal}
              onDelete={handleDelete}
            />
          ))
        )}

        <button
          onClick={openCreateModal}
          className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-ink-faint hover:text-ink hover:bg-surface transition-colors text-left"
        >
          <Plus size={14} />
          New task
        </button>
      </div>

      {isModalOpen && (
        <TaskFormModal
          initialTask={editingTask}
          userId={user?.id}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleSubmit}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
        />
      )}
    </div>
  );
};

export default Tasks;
