import { AlertTriangle } from "lucide-react";

const UrgentEmailCard = ({ emails }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-red-bg)] flex items-center justify-center">
          <AlertTriangle size={14} className="text-[var(--color-tag-red-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Urgent emails</h2>
      </div>

      {emails.length === 0 && (
        <p className="text-sm text-ink-faint">No urgent emails 🎉</p>
      )}

      <div className="space-y-1">
        {emails.slice(0, 5).map((mail, index) => (
          <div
            key={index}
            className="py-2.5 px-2 -mx-2 rounded-md hover:bg-surface transition-colors"
          >
            <h3 className="text-sm font-medium text-ink truncate">{mail.subject}</h3>
            <p className="text-xs text-ink-faint mt-0.5">{mail.sender}</p>
            <p className="text-xs text-ink-muted mt-1 line-clamp-1">{mail.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UrgentEmailCard;
