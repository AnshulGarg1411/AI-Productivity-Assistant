import { useState } from "react";
import { format } from "date-fns";
import {
  Plus,
  RefreshCw,
  Video,
  MapPin,
  AlertTriangle,
  Clock,
  Zap,
} from "lucide-react";

import {
  useMeetingsQuery,
  useMeetingAnalyticsQuery,
  useMeetings,
} from "../hooks/useMeetings";
import { useAuth } from "../contexts/AuthContext";
import MeetingFormModal from "../components/meetings/MeetingFormModal";
import { MEETING_STATUS_TAG, pill } from "../lib/tagStyles";

const StatBlock = ({ icon, label, value, danger }) => (
  <div className="border border-border rounded-lg p-4">
    <div className="flex items-center gap-1.5 text-ink-muted text-xs font-medium mb-2">
      {icon}
      {label}
    </div>
    <p
      className={`text-2xl font-semibold font-mono tabular-nums ${
        danger ? "text-[var(--color-tag-red-text)]" : "text-ink"
      }`}
    >
      {value}
    </p>
  </div>
);

const Meetings = () => {
  const { data: meetings, isLoading, error } = useMeetingsQuery();
  const { data: analytics } = useMeetingAnalyticsQuery();
  const { createMutation, syncMutation } = useMeetings();
  const { user } = useAuth();

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSubmit = (payload) => {
    createMutation.mutate(payload, {
      onSuccess: () => setIsModalOpen(false),
    });
  };

  const sortedMeetings = [...(meetings || [])].sort(
    (a, b) => new Date(a.start_time) - new Date(b.start_time)
  );

  return (
    <div className="max-w-5xl mx-auto px-10 py-8">
      <div className="text-3xl mb-3 leading-none">🗓️</div>
      <div className="flex justify-between items-end mb-6 flex-wrap gap-3">
        <h1 className="text-2xl font-semibold text-ink tracking-tight">Meetings</h1>
        <div className="flex gap-2">
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-1.5 border border-border text-ink text-sm font-medium px-3 py-1.5 rounded-md hover:bg-surface-hover disabled:opacity-50 transition-colors"
          >
            <RefreshCw
              size={14}
              className={syncMutation.isPending ? "animate-spin" : ""}
            />
            Sync Google Calendar
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 bg-accent text-white text-sm font-medium px-3 py-1.5 rounded-md hover:bg-accent-hover transition-colors"
          >
            <Plus size={15} />
            New
          </button>
        </div>
      </div>

      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <StatBlock
            icon={<Clock size={13} />}
            label="Meeting hours"
            value={analytics.meeting_hours.toFixed(1)}
          />
          <StatBlock
            icon={<Zap size={13} />}
            label="Meeting load"
            value={analytics.meeting_load}
          />
          <StatBlock
            icon={<Video size={13} />}
            label="Total meetings"
            value={analytics.total_meetings}
          />
          <StatBlock
            icon={<AlertTriangle size={13} />}
            label="Conflicts"
            value={analytics.conflicts.length}
            danger={analytics.conflicts.length > 0}
          />
        </div>
      )}

      {analytics?.best_focus_window && (
        <div className="bg-accent-soft border border-[color-mix(in_srgb,var(--color-accent)_25%,transparent)] rounded-lg p-5 mb-6">
          <h3 className="text-sm font-semibold text-ink mb-1">Best focus window</h3>
          <p className="text-lg text-ink font-mono tabular-nums">
            {format(new Date(analytics.best_focus_window.start), "h:mm a")} –{" "}
            {format(new Date(analytics.best_focus_window.end), "h:mm a")}{" "}
            <span className="text-sm text-ink-muted font-sans">
              ({analytics.best_focus_window.duration_minutes} min)
            </span>
          </p>
        </div>
      )}

      {analytics?.conflicts?.length > 0 && (
        <div className="bg-[var(--color-tag-red-bg)] border border-[var(--color-tag-red-text)]/20 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-semibold text-[var(--color-tag-red-text)] mb-2 flex items-center gap-1.5">
            <AlertTriangle size={15} />
            Scheduling conflicts
          </h3>
          <div className="space-y-1">
            {analytics.conflicts.map((c, i) => (
              <p key={i} className="text-sm text-[var(--color-tag-red-text)]">
                "{c.meeting1}" overlaps with "{c.meeting2}"
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="border border-border rounded-lg">
        <div className="px-4 py-3 border-b border-border">
          <h3 className="text-sm font-medium text-ink">All meetings</h3>
        </div>

        {isLoading && (
          <p className="text-sm text-ink-faint p-6 text-center">Loading meetings...</p>
        )}
        {error && (
          <p className="text-sm text-[var(--color-tag-red-text)] p-6 text-center">
            Failed to load meetings
          </p>
        )}

        {!isLoading && sortedMeetings.length === 0 && (
          <p className="text-sm text-ink-faint text-center py-10">
            No meetings yet. Create one or sync your Google Calendar.
          </p>
        )}

        <div className="divide-y divide-border">
          {sortedMeetings.map((meeting) => (
            <div
              key={meeting.id}
              className="flex items-center justify-between px-4 py-3 hover:bg-surface transition-colors"
            >
              <div className="min-w-0">
                <h4 className="text-sm font-medium text-ink truncate">{meeting.title}</h4>
                <p className="text-xs text-ink-faint flex items-center gap-1.5 mt-1 font-mono tabular-nums">
                  {meeting.meeting_type === "ONLINE" ? (
                    <Video size={12} />
                  ) : (
                    <MapPin size={12} />
                  )}
                  {format(new Date(meeting.start_time), "MMM d, h:mm a")} –{" "}
                  {format(new Date(meeting.end_time), "h:mm a")}
                  {meeting.location && ` · ${meeting.location}`}
                </p>
              </div>
              <span className={pill(MEETING_STATUS_TAG[meeting.status])}>
                {meeting.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {isModalOpen && (
        <MeetingFormModal
          userId={user?.id}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleSubmit}
          isSubmitting={createMutation.isPending}
        />
      )}
    </div>
  );
};

export default Meetings;
