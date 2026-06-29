import React from "react";

/**
 * Circular progress ring (SVG).
 *
 * Props:
 *  - percentage: number (0-100)
 *  - size: number — width/height in px (default 48)
 *  - strokeWidth: number (default 4)
 *  - label: string — small caption under the percentage
 *  - color: CSS color override (default uses accent)
 *
 * Usage:
 *   <CircularProgress percentage={85} size={48} />
 *   <CircularProgress percentage={94} size={80} label="Match" />
 */
export default function CircularProgress({
  percentage = 0,
  size = 48,
  strokeWidth = 4,
  label,
  color,
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Dynamic color based on percentage
  const getColor = () => {
    if (color) return color;
    if (percentage >= 85) return "var(--color-jp-success)";
    if (percentage >= 70) return "var(--color-jp-accent)";
    if (percentage >= 50) return "var(--color-jp-warning)";
    return "var(--color-jp-error)";
  };

  const ringColor = getColor();

  return (
    <div className="relative inline-flex" style={{ width: size, height: size }}>
      <svg className="w-full h-full -rotate-90" viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="var(--color-jp-bg-raised)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={ringColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-semibold tracking-tight"
          style={{
            fontSize: size > 60 ? 18 : size > 40 ? 13 : 10,
            color: ringColor,
          }}
        >
          {percentage}%
        </span>
        {label && (
          <span className="text-[9px] font-semibold uppercase tracking-wider text-jp-text-muted">
            {label}
          </span>
        )}
      </div>
    </div>
  );
}