import React from "react";
import Icon from "../common/Icon";

/**
 * Filter bar for the Search Results page:
 * "Filters:" label + dropdowns (Location, Experience, Work Mode, Min Match Score)
 * on the left, "Sort By: Highest Match" dropdown on the right.
 *
 * Usage:
 *   <FilterBar
 *     filters={[
 *       { label: "Location", options: ["Pune", "Bengaluru", "Remote"] },
 *       { label: "Experience", options: ["0-2 years", "3-5 years", "5+ years"] },
 *       { label: "Work Mode", options: ["Remote", "Hybrid", "On-site"] },
 *       { label: "Min Match Score", options: ["50%", "70%", "90%"] },
 *     ]}
 *     sortOptions={["Highest Match", "Most Recent", "Salary"]}
 *     sortValue="Highest Match"
 *   />
 *
 * Props:
 *  - filters: Array<{ label: string, options: string[] }>
 *  - sortOptions: string[]
 *  - sortValue: string — currently selected sort label
 *  - onFilterChange: (filterLabel: string, value: string) => void
 *  - onSortChange: (value: string) => void
 */
export default function FilterBar({
    filters = [],
    sortOptions = [],
    sortValue,
    onFilterChange,
    onSortChange,
}) {
    return (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-[var(--color-surface-container-lowest)] border border-white/5 rounded-xl p-4" style={{ borderColor: "var(--color-outline-variant)" }}>
            <div className="flex flex-wrap items-center gap-3">
                <span className="text-[14px] leading-[20px] font-semibold" style={{ color: "var(--color-on-surface)" }}>
                    Filters:
                </span>
                {filters.map((filter) => (
                    <div className="relative" key={filter.label}>
                        <select
                            className="pl-3 pr-8 py-2 bg-[var(--color-surface-container-low)] text-white border border-white/10 rounded-lg text-[14px] leading-[20px] font-medium appearance-none"
                            style={{ borderColor: "var(--color-outline-variant)" }}
                            onChange={(e) => onFilterChange?.(filter.label, e.target.value)}
                            defaultValue={filter.label}
                        >
                            <option>{filter.label}</option>
                            {filter.options.map((opt) => (
                                <option key={opt}>{opt}</option>
                            ))}
                        </select>
                        <span className="absolute right-2 inset-y-0 flex items-center pointer-events-none" style={{ color: "var(--color-outline)" }}>
                            <Icon name="expand_more" />
                        </span>
                    </div>
                ))}
            </div>

            <div className="flex items-center gap-2">
                <span className="text-[14px] leading-[20px] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                    Sort By:
                </span>
                <div className="relative">
                    <select
                        className="pl-3 pr-8 py-2 bg-[var(--color-surface-container-low)] border border-white/10 rounded-lg text-[14px] leading-[20px] font-semibold appearance-none"
                        style={{ borderColor: "var(--color-primary)", color: "var(--color-primary)" }}
                        value={sortValue}
                        onChange={(e) => onSortChange?.(e.target.value)}
                    >
                        {sortOptions.map((opt) => (
                            <option key={opt}>{opt}</option>
                        ))}
                    </select>
                    <span className="absolute right-2 inset-y-0 flex items-center pointer-events-none" style={{ color: "var(--color-primary)" }}>
                        <Icon name="expand_more" />
                    </span>
                </div>
            </div>
        </div>
    );
}