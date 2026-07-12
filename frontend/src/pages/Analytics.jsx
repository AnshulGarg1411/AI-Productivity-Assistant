import { format } from "date-fns";
import { CheckCircle2, ListChecks, Timer, Video } from "lucide-react";

import { useTaskAnalyticsQuery } from "../hooks/useTasks";
import { useMeetingAnalyticsQuery } from "../hooks/useMeetings";
import BarChart from "../components/analytics/BarChart";
import RingStat from "../components/analytics/RingStat";

const StatCard = ({ icon, label, value, tone }) => (
  <div className="border border-border rounded-lg p-4 flex items-center gap-3">
    <div className={`w-9 h-9 rounded-md flex items-center justify-center shrink-0 ${tone}`}>
      {icon}
    </div>
    <div className="min-w-0">
      <p className="text-xs text-ink-faint truncate">{label}</p>
      <p className="text-lg font-semibold text-ink font-mono tabular-nums">{value}</p>
    </div>
  </div>
);

const Analytics = () => {
  const { data: taskAnalytics, isLoading: loadingTasks } =
    useTaskAnalyticsQuery();
  const { data: meetingAnalytics, isLoading: loadingMeetings } =
    useMeetingAnalyticsQuery();

  const isLoading = loadingTasks || loadingMeetings;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-sm text-ink-muted">Crunching your numbers...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-10 py-8">
      <div className="text-3xl mb-3 leading-none">📊</div>
      <h1 className="text-2xl font-semibold text-ink tracking-tight mb-6">Analytics</h1>

      {/* Top stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard
          icon={<ListChecks className="text-[var(--color-tag-blue-text)]" size={18} />}
          label="Total tasks"
          value={taskAnalytics?.total_tasks ?? 0}
          tone="bg-[var(--color-tag-blue-bg)]"
        />
        <StatCard
          icon={<CheckCircle2 className="text-[var(--color-tag-green-text)]" size={18} />}
          label="Completed tasks"
          value={taskAnalytics?.completed_tasks ?? 0}
          tone="bg-[var(--color-tag-green-bg)]"
        />
        <StatCard
          icon={<Timer className="text-[var(--color-tag-yellow-text)]" size={18} />}
          label="Avg. completion time"
          value={`${Math.round(taskAnalytics?.average_completion_time ?? 0)} min`}
          tone="bg-[var(--color-tag-yellow-bg)]"
        />
        <StatCard
          icon={<Video className="text-[var(--color-tag-purple-text)]" size={18} />}
          label="Meeting hours"
          value={(meetingAnalytics?.meeting_hours ?? 0).toFixed(1)}
          tone="bg-[var(--color-tag-purple-bg)]"
        />
      </div>

      {/* Rings */}
      <div className="border border-border rounded-lg p-6 mb-6">
        <h3 className="text-sm font-medium text-ink mb-6">Productivity overview</h3>
        <div className="flex flex-wrap gap-10 justify-center sm:justify-start">
          <RingStat
            value={taskAnalytics?.productivity_score ?? 0}
            label="Productivity score"
            color="var(--color-accent)"
          />
          <RingStat
            value={taskAnalytics?.completion_rate ?? 0}
            label="Task completion rate"
            color="#3c8768"
          />
          <RingStat
            value={taskAnalytics?.overdue_tasks ?? 0}
            max={Math.max(taskAnalytics?.total_tasks ?? 1, 1)}
            label="Overdue tasks"
            color="#d4433c"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Task breakdown */}
        <div className="border border-border rounded-lg p-6">
          <h3 className="text-sm font-medium text-ink mb-5">Task breakdown</h3>
          <BarChart
            data={[
              {
                label: "Completed",
                value: taskAnalytics?.completed_tasks ?? 0,
                color: "#3c8768",
              },
              {
                label: "Pending",
                value: taskAnalytics?.pending_tasks ?? 0,
                color: "#97740c",
              },
              {
                label: "Overdue",
                value: taskAnalytics?.overdue_tasks ?? 0,
                color: "#d4433c",
              },
              {
                label: "High Priority (Pending)",
                value: taskAnalytics?.high_priority_pending ?? 0,
                color: "var(--color-accent)",
              },
            ]}
          />
        </div>

        {/* Estimated vs actual */}
        <div className="border border-border rounded-lg p-6">
          <h3 className="text-sm font-medium text-ink mb-5">
            Estimated vs. actual time
          </h3>
          <BarChart
            data={[
              {
                label: "Estimated Minutes",
                value: taskAnalytics?.estimated_vs_actual?.estimated ?? 0,
                color: "#a7c4ef",
              },
              {
                label: "Actual Minutes",
                value: taskAnalytics?.estimated_vs_actual?.actual ?? 0,
                color: "var(--color-accent)",
              },
            ]}
            valueSuffix=" min"
          />
        </div>
      </div>

      {/* Meeting section */}
      <div className="border border-border rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-medium text-ink">Meeting load</h3>
          <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-[var(--color-tag-blue-bg)] text-[var(--color-tag-blue-text)]">
            {meetingAnalytics?.meeting_load}
          </span>
        </div>

        {meetingAnalytics?.free_slots?.length > 0 ? (
          <div className="space-y-1.5">
            <p className="text-xs text-ink-faint mb-2">
              Free slots available today:
            </p>
            {meetingAnalytics.free_slots.map((slot, i) => (
              <div
                key={i}
                className="flex justify-between text-sm p-2.5 rounded-md bg-surface font-mono tabular-nums"
              >
                <span className="text-ink">
                  {format(new Date(slot.start), "h:mm a")} –{" "}
                  {format(new Date(slot.end), "h:mm a")}
                </span>
                <span className="text-ink-faint">
                  {slot.duration_minutes} min
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-ink-faint text-sm">No free slots found.</p>
        )}
      </div>
    </div>
  );
};

export default Analytics;
