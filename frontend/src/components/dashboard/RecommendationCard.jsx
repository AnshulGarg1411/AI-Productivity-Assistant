import { Sparkles } from "lucide-react";
import { PRIORITY_TAG, pill } from "../../lib/tagStyles";

const RecommendationCard = ({ recommendations }) => {
  return (
    <div className="bg-canvas border border-border rounded-lg p-6">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-md bg-[var(--color-tag-yellow-bg)] flex items-center justify-center">
          <Sparkles size={14} className="text-[var(--color-tag-yellow-text)]" />
        </div>
        <h2 className="text-sm font-medium text-ink">Recommendations</h2>
      </div>

      <div className="space-y-2">
        {recommendations.map((item, index) => (
          <div
            key={index}
            className="border border-border rounded-md p-4 hover:bg-surface transition-colors"
          >
            <div className="flex justify-between items-start gap-3">
              <h3 className="text-sm font-medium text-ink">{item.title}</h3>
              <span className={pill(PRIORITY_TAG[item.priority])}>{item.priority}</span>
            </div>
            <p className="text-sm text-ink-muted mt-1.5">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationCard;
