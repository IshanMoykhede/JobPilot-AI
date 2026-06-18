import React from "react";

/**
 * Labeled horizontal progress bar, used inside InsightsPanelCard for
 * "Most Common Skills Found" (e.g. AWS, Docker, Linux with fill bars).
 *
 * Usage:
 *   <SkillProgressBar label="AWS" percentage={80} />
 *   <SkillProgressBar label="Docker" percentage={65} />
 *   <SkillProgressBar label="Linux" percentage={55} />
 *
 * Props:
 *  - label: string
 *  - percentage: number (0-100)
 */
export default function SkillProgressBar({ label, percentage }) {
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-[12px] leading-[16px] tracking-[0.01em] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                <span>{label}</span>
            </div>
            <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: "var(--color-surface-container)" }}>
                <div
                    className="h-1.5 rounded-full"
                    style={{
                        width: `${percentage}%`,
                        backgroundColor: "var(--color-primary)",
                    }}
                />
            </div>
        </div>
    );
}