import { useState } from "react";
import { X } from "lucide-react";

const CATEGORIES = ["WORK", "STUDY", "PERSONAL", "HEALTH"];
const PRIORITIES = ["LOW", "MEDIUM", "HIGH"];

const inputClass =
  "w-full mt-1 bg-canvas border border-border rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent";
const labelClass = "text-xs font-medium text-ink-muted";

const toDatetimeLocal = (isoString) => {
  if (!isoString) return "";
  const d = new Date(isoString);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
};

const TaskFormModal = ({ initialTask, userId, onClose, onSubmit, isSubmitting }) => {
  const [form, setForm] = useState({
    title: initialTask?.title || "",
    description: initialTask?.description || "",
    category: initialTask?.category || "WORK",
    priority: initialTask?.priority || "MEDIUM",
    due_date: initialTask
      ? toDatetimeLocal(initialTask.due_date)
      : toDatetimeLocal(new Date().toISOString()),
    estimated_minutes: initialTask?.estimated_minutes || 30,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.title.trim()) return;

    onSubmit({
      user_id: initialTask?.user_id ?? userId ?? 0,
      title: form.title,
      description: form.description || null,
      category: form.category,
      priority: form.priority,
      status: initialTask?.status || "TODO",
      due_date: new Date(form.due_date).toISOString(),
      estimated_minutes: Number(form.estimated_minutes),
      is_recurring: initialTask?.is_recurring || false,
      source: initialTask?.source || "MANUAL",
    });
  };

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 px-4">
      <div className="bg-canvas border border-border rounded-lg shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-base font-semibold text-ink">
            {initialTask ? "Edit task" : "New task"}
          </h2>
          <button
            onClick={onClose}
            className="text-ink-faint hover:text-ink hover:bg-surface-hover rounded p-1"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className={labelClass}>Title</label>
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              required
              className={inputClass}
              placeholder="e.g. Finish project report"
            />
          </div>

          <div>
            <label className={labelClass}>Description</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={2}
              className={inputClass}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Category</label>
              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                className={inputClass}
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={labelClass}>Priority</label>
              <select
                name="priority"
                value={form.priority}
                onChange={handleChange}
                className={inputClass}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Due date</label>
              <input
                type="datetime-local"
                name="due_date"
                value={form.due_date}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>

            <div>
              <label className={labelClass}>Estimated minutes</label>
              <input
                type="number"
                min={1}
                name="estimated_minutes"
                value={form.estimated_minutes}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-md text-sm text-ink-muted hover:bg-surface-hover"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3 py-1.5 rounded-md bg-accent text-white text-sm font-medium hover:bg-accent-hover disabled:opacity-50"
            >
              {initialTask ? "Save changes" : "Create task"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskFormModal;
