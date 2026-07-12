import { Mail } from "lucide-react";

const Stat = ({ label, value, tone }) => (
  <div className="flex justify-between items-center py-2">
    <span className="text-sm text-ink-muted">{label}</span>
    <span className={`text-sm font-semibold font-mono tabular-nums ${tone || "text-ink"}`}>
      {value}
    </span>
  </div>
);

const EmailCard = ({ emails }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-blue-bg)] flex items-center justify-center">
          <Mail size={14} className="text-[var(--color-tag-blue-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Emails</h2>
      </div>

      <div className="divide-y divide-border">
        <Stat label="Total" value={emails.total} />
        <Stat label="Unread" value={emails.unread} tone="text-[var(--color-tag-red-text)]" />
        <Stat label="Important" value={emails.important} tone="text-[var(--color-tag-blue-text)]" />
      </div>
    </div>
  );
};

export default EmailCard;
