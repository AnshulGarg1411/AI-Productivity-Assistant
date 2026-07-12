import { Coffee } from "lucide-react";

const MorningBriefCard = ({ brief }) => {
  if (!brief) {
    return (
      <div className="bg-canvas border border-border rounded-lg p-6">
        <h2 className="text-sm font-medium text-ink">Morning brief</h2>
        <p className="text-sm text-ink-faint mt-2">No morning brief available.</p>
      </div>
    );
  }

  return (
    <div className="bg-accent-soft border border-[color-mix(in_srgb,var(--color-accent)_25%,transparent)] rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-3">
        <Coffee size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-ink">Morning brief</h2>
      </div>

      <h3 className="text-lg font-semibold text-ink">{brief.greeting}</h3>

      <div className="mt-4 space-y-2">
        {brief.summary.map((item, index) => (
          <div key={index} className="bg-canvas/70 rounded-md p-3 text-sm text-ink">
            {item}
          </div>
        ))}
      </div>

      <div className="mt-5 pt-4 border-t border-[color-mix(in_srgb,var(--color-accent)_20%,transparent)]">
        <h4 className="text-xs font-medium text-ink-muted uppercase tracking-wide mb-1">
          Top priority
        </h4>
        <p className="text-sm text-ink">{brief.top_priority || "No urgent task"}</p>
      </div>
    </div>
  );
};

export default MorningBriefCard;
