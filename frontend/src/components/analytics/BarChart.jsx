// A tiny dependency-free bar chart. The project doesn't have a charting
// library installed (no recharts/chart.js in package.json), so this keeps
// things visual without adding a new dependency.
const BarChart = ({ data, valueSuffix = "" }) => {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="space-y-3">
      {data.map((item) => (
        <div key={item.label}>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-ink-muted">{item.label}</span>
            <span className="font-medium text-ink font-mono tabular-nums">
              {item.value}
              {valueSuffix}
            </span>
          </div>
          <div className="w-full h-1.5 bg-surface rounded-full overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{
                width: `${(item.value / max) * 100}%`,
                backgroundColor: item.color || "var(--color-accent)",
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default BarChart;
