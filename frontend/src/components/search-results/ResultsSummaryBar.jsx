import React from "react";
import Icon, { withRipple, resetRipple } from "../common/Icon";

/**
 * Heading row for the Search Results page:
 * "DevOps Engineer Jobs in Pune" + stat pills (Jobs Found, Top Matches,
 * Average Match) + "Share Search Results" button.
 *
 * Usage:
 *   <ResultsSummaryBar
 *     title="DevOps Engineer Jobs in Pune"
 *     stats={[
 *       { label: "127 Jobs Found" },
 *       { label: "10 Top Matches" },
 *       { label: "Average Match: 78%" },
 *     ]}
 *     onShareClick={() => {}}
 *   />
 *
 * Props:
 *  - title: string
 *  - stats: Array<{ label: string }>
 *  - onShareClick: () => void
 *  - shareLabel: string (default "Share Search Results")
 */
export default function ResultsSummaryBar({
    title,
    stats = [],
    onShareClick,
    shareLabel = "Share Search Results",
}) {
    return (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex flex-col gap-2">
                <h2 className="text-[20px] leading-[28px] font-semibold" style={{ color: "var(--color-on-surface)" }}>
                    {title}
                </h2>
                <div className="flex flex-wrap items-center gap-2">
                    {stats.map((stat, index) => (
                        <React.Fragment key={stat.label}>
                            <span
                                className="text-[12px] leading-[16px] tracking-[0.01em] font-semibold"
                                style={{ color: "var(--color-primary)" }}
                            >
                                {stat.label}
                            </span>
                            {index < stats.length - 1 && (
                                <span className="text-[12px]" style={{ color: "var(--color-outline-variant)" }}>
                                    |
                                </span>
                            )}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            <button
                className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface-container-low)] border border-white/10 rounded-lg text-[14px] leading-[20px] font-medium transition-all hover:bg-white/5 hover:border-primary/20 self-start sm:self-auto"
                style={{ color: "var(--color-on-surface)" }}
                onClick={onShareClick}
                onMouseDown={withRipple}
                onMouseUp={resetRipple}
                onMouseLeave={resetRipple}
            >
                <Icon name="share" className="text-[18px]" />
                {shareLabel}
            </button>
        </div>
    );
}