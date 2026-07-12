import { CalendarClock } from "lucide-react";

const TodayScheduleCard = ({ meetings }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-blue-bg)] flex items-center justify-center">
          <CalendarClock size={14} className="text-[var(--color-tag-blue-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Today's schedule</h2>
      </div>

      {meetings.length === 0 && (
        <p className="text-sm text-ink-faint">No meetings today.</p>
      )}

      <div className="space-y-1">
        {meetings.map((meeting, index) => (
          <div
            key={index}
            className="flex items-center gap-3 py-2 border-l-2 border-[var(--color-tag-blue-text)] pl-3"
          >
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-ink truncate">{meeting.title}</h3>
              <p className="text-xs text-ink-faint font-mono">{meeting.start_time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TodayScheduleCard;
