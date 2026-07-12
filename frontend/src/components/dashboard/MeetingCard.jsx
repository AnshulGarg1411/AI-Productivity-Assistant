import { CalendarDays } from "lucide-react";

const Stat = ({ label, value, tone }) => (
  <div className="flex justify-between items-center py-2">
    <span className="text-sm text-ink-muted">{label}</span>
    <span className={`text-sm font-semibold font-mono tabular-nums ${tone || "text-ink"}`}>
      {value}
    </span>
  </div>
);

const MeetingCard = ({ meetings }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-green-bg)] flex items-center justify-center">
          <CalendarDays size={14} className="text-[var(--color-tag-green-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Meetings</h2>
      </div>

      <div className="divide-y divide-border">
        <Stat label="Today" value={meetings.today} />
        <Stat label="Upcoming" value={meetings.upcoming} />
        <Stat
          label="Meeting hours"
          value={meetings.meeting_hours}
          tone="text-[var(--color-tag-green-text)]"
        />
      </div>
    </div>
  );
};

export default MeetingCard;
