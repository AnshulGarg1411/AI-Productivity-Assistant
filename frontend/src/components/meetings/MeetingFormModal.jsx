import { useState } from "react";
import { X } from "lucide-react";

const MEETING_TYPES = ["ONLINE", "OFFLINE"];
const MEETING_STATUSES = ["CONFIRMED", "TENTATIVE", "CANCELLED"];

const inputClass =
  "w-full mt-1 bg-canvas border border-border rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent";
const labelClass = "text-xs font-medium text-ink-muted";

const toDatetimeLocal = (date) => {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate()
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

const MeetingFormModal = ({ userId, onClose, onSubmit, isSubmitting }) => {
  const now = new Date();
  const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);

  const [form, setForm] = useState({
    title: "",
    description: "",
    organizer: "",
    location: "",
    meeting_link: "",
    start_time: toDatetimeLocal(now),
    end_time: toDatetimeLocal(oneHourLater),
    meeting_type: "ONLINE",
    status: "CONFIRMED",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;

    onSubmit({
      user_id: userId ?? 0,
      title: form.title,
      description: form.description || null,
      organizer: form.organizer || null,
      location: form.location || null,
      meeting_link: form.meeting_link || null,
      attendees: null,
      start_time: new Date(form.start_time).toISOString(),
      end_time: new Date(form.end_time).toISOString(),
      meeting_type: form.meeting_type,
      status: form.status,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 px-4">
      <div className="bg-canvas border border-border rounded-lg shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-base font-semibold text-ink">New meeting</h2>
          <button onClick={onClose} className="text-ink-faint hover:text-ink hover:bg-surface-hover rounded p-1">
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
              placeholder="e.g. Sprint Planning"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Start</label>
              <input
                type="datetime-local"
                name="start_time"
                value={form.start_time}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>End</label>
              <input
                type="datetime-local"
                name="end_time"
                value={form.end_time}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Type</label>
              <select
                name="meeting_type"
                value={form.meeting_type}
                onChange={handleChange}
                className={inputClass}
              >
                {MEETING_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select
                name="status"
                value={form.status}
                onChange={handleChange}
                className={inputClass}
              >
                {MEETING_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {form.meeting_type === "ONLINE" ? (
            <div>
              <label className={labelClass}>Meeting link</label>
              <input
                name="meeting_link"
                value={form.meeting_link}
                onChange={handleChange}
                className={inputClass}
                placeholder="https://meet.google.com/..."
              />
            </div>
          ) : (
            <div>
              <label className={labelClass}>Location</label>
              <input
                name="location"
                value={form.location}
                onChange={handleChange}
                className={inputClass}
                placeholder="e.g. Conference Room A"
              />
            </div>
          )}

          <div>
            <label className={labelClass}>Organizer</label>
            <input
              name="organizer"
              value={form.organizer}
              onChange={handleChange}
              className={inputClass}
            />
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
              Create meeting
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MeetingFormModal;
