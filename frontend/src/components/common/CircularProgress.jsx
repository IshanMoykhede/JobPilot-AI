import React from "react";

/**
 * Circular progress ring (SVG), used for:
 *  - Dashboard "Profile Strength: 85%" panel (large size, with "Score" label)
 *  - Search Results job cards "AI Match %" indicator (small size, no label)
 *
 * Props:
 *  - percentage: number (0-100)
 *  - size: number — width/height in px (default 128, i.e. w-32 h-32)
 *  - strokeWidth: number (default 8)
 *  - label: string — small caption under the percentage (e.g. "Score"). Omit for compact use.
 *  - valueClassName: string — extra classes for the percentage text
 *
 * Usage (Dashboard, large with label):
 *   <CircularProgress percentage={85} size={128} label="Score" />
 *
 * Usage (Job card, small, compact):
 *   <CircularProgress percentage={94} size={48} strokeWidth={4} valueClassName="text-[12px]" />
 */
export default function CircularProgress({
    percentage = 0,
    size = 128,
    strokeWidth = 8,
    label,
    valueClassName = "text-[24px] leading-[32px] tracking-[-0.01em] font-bold",
}) {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    return (
        <div className="relative" style={{ width: size, height: size }}>
            <svg
                className="w-full h-full transform -rotate-90"
                viewBox={`0 0 ${size} ${size}`}
            >
                <circle
                    style={{ color: "var(--color-outline-variant)" }}
                    cx={size / 2}
                    cy={size / 2}
                    fill="transparent"
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                />
                <circle
                    style={{ color: "var(--color-primary)" }}
                    cx={size / 2}
                    cy={size / 2}
                    fill="transparent"
                    r={radius}
                    stroke="currentColor"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={valueClassName} style={{ color: "var(--color-primary)" }}>
                    {percentage}%
                </span>
                {label && (
                    <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: "var(--color-outline)" }}>
                        {label}
                    </span>
                )}
            </div>
        </div>
    );
}