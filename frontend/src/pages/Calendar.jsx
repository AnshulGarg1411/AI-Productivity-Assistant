import { useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

import { useMeetingsQuery, useMeetings } from "../hooks/useMeetings";
import "../styles/fullcalendar-theme.css";

const TYPE_COLORS = {
  ONLINE: "#266d8f",
  OFFLINE: "#7a559e",
};

const Calendar = () => {
  const { data: meetings, isLoading } = useMeetingsQuery();
  const { syncMutation } = useMeetings();
  const [selectedMeeting, setSelectedMeeting] = useState(null);

  const events = useMemo(() => {
    if (!meetings) return [];
    return meetings
      .filter((m) => m.status !== "CANCELLED")
      .map((m) => ({
        id: String(m.id),
        title: m.title,
        start: m.start_time,
        end: m.end_time,
        backgroundColor: TYPE_COLORS[m.meeting_type] || "#266d8f",
        borderColor: TYPE_COLORS[m.meeting_type] || "#266d8f",
        extendedProps: m,
      }));
  }, [meetings]);

  return (
    <div className="max-w-5xl mx-auto px-10 py-8">
      <div className="text-3xl mb-3 leading-none">📅</div>
      <div className="flex justify-between items-end mb-6">
        <h1 className="text-2xl font-semibold text-ink tracking-tight">Calendar</h1>
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
      </div>

      <div className="border border-border rounded-lg p-4">
        {isLoading ? (
          <p className="text-sm text-ink-faint text-center py-10">Loading calendar...</p>
        ) : (
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "dayGridMonth,timeGridWeek,timeGridDay",
            }}
            height="auto"
            events={events}
            className="notion-calendar"
            eventClick={(info) => {
              setSelectedMeeting(info.event.extendedProps);
              toast(info.event.title, { icon: "📅" });
            }}
          />
        )}
      </div>

      {selectedMeeting && (
        <div className="border border-border rounded-lg p-5 mt-4">
          <h3 className="text-sm font-semibold text-ink">{selectedMeeting.title}</h3>
          <p className="text-sm text-ink-muted mt-1">
            {selectedMeeting.description || "No description"}
          </p>
          {selectedMeeting.meeting_link && (
            <a
              href={selectedMeeting.meeting_link}
              target="_blank"
              rel="noreferrer"
              className="text-accent text-sm mt-2 inline-block hover:underline"
            >
              Join meeting →
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default Calendar;
