const RingStat = ({ value, max = 100, label, color = "var(--color-accent)" }) => {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center">
      <svg width="110" height="110" viewBox="0 0 110 110">
        <circle
          cx="55"
          cy="55"
          r={radius}
          fill="none"
          stroke="var(--color-surface)"
          strokeWidth="8"
        />
        <circle
          cx="55"
          cy="55"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 55 55)"
        />
        <text
          x="55"
          y="61"
          textAnchor="middle"
          fontSize="22"
          fontWeight="600"
          fontFamily="var(--font-mono)"
          fill="var(--color-ink)"
        >
          {Math.round(value)}
        </text>
      </svg>
      <p className="text-sm text-ink-muted mt-1 text-center">{label}</p>
    </div>
  );
};

export default RingStat;
