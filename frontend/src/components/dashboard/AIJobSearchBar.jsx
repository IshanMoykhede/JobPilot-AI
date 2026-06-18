import React from "react";
import Icon, { withRipple, resetRipple } from "../common/Icon";

/**
 * AI-powered job search bar card.
 * Used at the top of the Dashboard page with filters + suggestions.
 * Can also be reused on the Search Results page with a different
 * placeholder and `showFilters={false}` / `showSuggestions={false}`
 * if a slimmer version is needed there.
 *
 * Props:
 *  - placeholder: string
 *  - value, onChange: controlled input props (optional)
 *  - onSearch: () => void — called when "Search Jobs" is clicked
 *  - showFilters: boolean — show Location/Experience/Work Type dropdowns (default true)
 *  - showSuggestions: boolean — show "Popular suggestions" tag row (default true)
 *  - suggestions: string[] — tag labels
 *  - onSuggestionClick: (tag: string) => void
 *  - filters: Array<{ label: string, options: string[] }> — override default filter dropdowns
 *  - searchButtonLabel: string — defaults to "Search Jobs"
 *
 * Usage (Dashboard):
 *   <AIJobSearchBar
 *     placeholder="Try: DevOps Engineer in Pune..."
 *     suggestions={["DevOps Engineer", "Frontend Developer", "SRE Manager", "Cloud Architect"]}
 *   />
 *
 * Usage (Search Results, slim):
 *   <AIJobSearchBar
 *     placeholder="Try: 'DevOps Engineer in Pune' or 'Senior Frontend Developer Remote'"
 *     showFilters={false}
 *     showSuggestions={false}
 *     searchButtonLabel="Search Jobs"
 *   />
 */

const DEFAULT_FILTERS = [
    { label: "Location", options: ["Bengaluru", "Pune", "Remote"] },
    { label: "Experience", options: ["0-2 years", "3-5 years", "5+ years"] },
    { label: "Work Type", options: ["Remote", "Hybrid", "On-site"] },
];

export default function AIJobSearchBar({
    placeholder = "Try: DevOps Engineer in Pune...",
    value,
    onChange,
    onSearch,
    showFilters = true,
    showSuggestions = true,
    suggestions = ["DevOps Engineer", "Frontend Developer", "SRE Manager", "Cloud Architect"],
    onSuggestionClick,
    filters = DEFAULT_FILTERS,
    searchButtonLabel = "Search Jobs",
}) {
    return (
        <section className="bg-white border rounded-2xl p-6 shadow-sm" style={{ borderColor: "var(--color-outline-variant)" }}>
            <div className="flex flex-col gap-6">
                <div className="space-y-4">
                    {/* Search input */}
                    <div className="relative flex items-stretch gap-4">
                        <div className="relative flex-1">
                            <span className="absolute inset-y-0 left-4 flex items-center" style={{ color: "var(--color-primary)" }}>
                                <Icon name="auto_awesome" className="text-[18px]" />
                            </span>
                            <input
                                className="w-full pl-12 pr-4 py-4 border rounded-xl text-[16px] leading-[24px] focus:ring-4 focus:ring-[var(--color-primary)]/10 transition-all"
                                style={{
                                    backgroundColor: "var(--color-surface-container-low)",
                                    borderColor: "var(--color-outline-variant)",
                                }}
                                placeholder={placeholder}
                                type="text"
                                value={value}
                                onChange={onChange}
                            />
                        </div>

                        {/* Slim mode: button sits inline with the input */}
                        {!showFilters && (
                            <button
                                className="flex items-center gap-2 px-6 text-[14px] leading-[20px] font-medium rounded-xl transition-all hover:opacity-90"
                                style={{ backgroundColor: "var(--color-primary)", color: "var(--color-on-primary)" }}
                                onClick={onSearch}
                                onMouseDown={withRipple}
                                onMouseUp={resetRipple}
                                onMouseLeave={resetRipple}
                            >
                                <Icon name="search" className="text-[18px]" />
                                {searchButtonLabel}
                            </button>
                        )}
                    </div>

                    {/* Filter dropdown row (Dashboard only) */}
                    {showFilters && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {filters.map((filter) => (
                                <div className="relative" key={filter.label}>
                                    <select
                                        className="w-full pl-3 pr-8 py-2.5 bg-white border rounded-lg text-[14px] leading-[20px] font-medium appearance-none"
                                        style={{ borderColor: "var(--color-outline-variant)" }}
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
                            <button
                                className="text-[14px] leading-[20px] font-medium py-2.5 rounded-lg transition-all active:scale-[0.98] hover:opacity-90"
                                style={{ backgroundColor: "var(--color-primary)", color: "var(--color-on-primary)" }}
                                onClick={onSearch}
                                onMouseDown={withRipple}
                                onMouseUp={resetRipple}
                                onMouseLeave={resetRipple}
                            >
                                {searchButtonLabel}
                            </button>
                        </div>
                    )}
                </div>

                {/* Suggestion tags */}
                {showSuggestions && (
                    <div>
                        <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium mb-3" style={{ color: "var(--color-outline)" }}>
                            Popular suggestions:
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {suggestions.map((tag) => (
                                <span
                                    key={tag}
                                    onClick={() => onSuggestionClick?.(tag)}
                                    className="px-3 py-1 border rounded-full text-[12px] leading-[16px] tracking-[0.01em] font-medium cursor-pointer transition-colors hover:bg-[var(--color-surface-container)]"
                                    style={{
                                        backgroundColor: "var(--color-surface-container-low)",
                                        borderColor: "var(--color-outline-variant)",
                                        color: "var(--color-primary)",
                                    }}
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
}