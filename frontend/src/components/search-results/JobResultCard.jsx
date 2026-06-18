import React from "react";
import Icon, { withRipple, resetRipple } from "../common/Icon";
import SkillTag from "../common/SkillTag";
import CircularProgress from "../common/CircularProgress";
import AIInsightBox from "./AIInsightBox";

/**
 * Main job listing card for the Search Results page.
 *
 * Structure:
 *   [logo] Title                                  [#1 Recommended badge]
 *          Company • Location (Work Mode)         [Match % ring]
 *          MATCHING SKILLS: [tags...]
 *          MISSING SKILLS: [tags...]
 *          [AIInsightBox] (optional)
 *          [Generate Tailored Resume] [View Details]
 *
 * Props:
 *  - logo: ReactNode — custom logo content (e.g. <img> or initials box). Optional.
 *  - title: string
 *  - company: string
 *  - location: string
 *  - workMode: string — e.g. "Hybrid", "On-site", "Remote"
 *  - matchPercentage: number
 *  - recommended: { rank: number } | null — shows "#N Recommended" badge if provided
 *  - matchingSkills: string[]
 *  - missingSkills: string[]
 *  - insightText: ReactNode — optional AI insight tip (renders AIInsightBox if provided)
 *  - summaryText: ReactNode — optional plain-text summary instead of AIInsightBox
 *      (e.g. "You meet 8 out of 10 primary requirements...")
 *  - onGenerateResume: () => void
 *  - onViewDetails: () => void
 *
 * Usage:
 *   <JobResultCard
 *     title="Senior DevOps Architect"
 *     company="CloudStream Solutions"
 *     location="Pune"
 *     workMode="Hybrid"
 *     matchPercentage={94}
 *     recommended={{ rank: 1 }}
 *     matchingSkills={["AWS (Expert)", "Docker", "Kubernetes"]}
 *     missingSkills={["Terraform", "ArgoCD"]}
 *     insightText={<>Your experience with EKS perfectly aligns with their stack. Mentioning your <strong>multi-cluster management</strong> could secure an interview.</>}
 *   />
 */
export default function JobResultCard({
    logo = null,
    title,
    company,
    location,
    workMode,
    matchPercentage,
    recommended = null,
    matchingSkills = [],
    missingSkills = [],
    missingSkillsVariant = "orange",
    insightText = null,
    summaryText = null,
    onGenerateResume,
    onViewDetails,
}) {
    return (
        <div
            className="bg-white border rounded-2xl p-6 space-y-4"
            style={{ borderColor: "var(--color-outline-variant)" }}
        >
            {/* Recommended badge */}
            {recommended && (
                <div className="flex justify-end -mt-2 -mr-2 mb-2">
                    <span
                        className="flex items-center gap-1 px-3 py-1 rounded-full text-[12px] leading-[16px] font-semibold"
                        style={{ backgroundColor: "var(--color-surface-container)", color: "var(--color-primary)" }}
                    >
                        <Icon name="workspace_premium" className="text-[14px]" />
                        #{recommended.rank} Recommended
                    </span>
                </div>
            )}

            <div className="flex items-start gap-4">
                {/* Logo */}
                <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
                    style={{ backgroundColor: "var(--color-surface-container)" }}
                >
                    {logo || <Icon name="business" style={{ color: "var(--color-on-surface-variant)" }} />}
                </div>

                {/* Title + meta */}
                <div className="flex-1 min-w-0">
                    <h3 className="text-[18px] leading-[24px] font-bold" style={{ color: "var(--color-on-surface)" }}>
                        {title}
                    </h3>
                    <p className="text-[14px] leading-[20px] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                        {company} • {location}
                        {workMode ? ` (${workMode})` : ""}
                    </p>
                </div>

                {/* Match ring */}
                <div className="flex flex-col items-center shrink-0">
                    <CircularProgress percentage={matchPercentage} size={56} strokeWidth={5} valueClassName="text-[14px] font-bold" />
                    <span className="text-[10px] font-semibold uppercase tracking-widest mt-1" style={{ color: "var(--color-outline)" }}>
                        AI Match
                    </span>
                </div>
            </div>

            {/* Matching skills */}
            {matchingSkills.length > 0 && (
                <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest mb-2" style={{ color: "var(--color-outline)" }}>
                        Matching Skills
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {matchingSkills.map((skill) => (
                            <SkillTag key={skill} label={skill} variant="green" />
                        ))}
                    </div>
                </div>
            )}

            {/* Missing skills */}
            {missingSkills.length > 0 && (
                <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest mb-2" style={{ color: "var(--color-outline)" }}>
                        Missing Skills
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {missingSkills.map((skill) => (
                            <SkillTag key={skill} label={skill} variant={missingSkillsVariant} />
                        ))}
                    </div>
                </div>
            )}

            {/* AI insight or plain summary */}
            {insightText && <AIInsightBox text={insightText} icon="lightbulb" />}
            {summaryText && (
                <p className="text-[14px] leading-[20px]" style={{ color: "var(--color-on-surface-variant)" }}>
                    {summaryText}
                </p>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-3 pt-2">
                <button
                    className="px-5 py-2 text-[14px] leading-[20px] font-medium rounded-lg transition-all hover:opacity-90"
                    style={{ backgroundColor: "var(--color-primary)", color: "var(--color-on-primary)" }}
                    onClick={onGenerateResume}
                    onMouseDown={withRipple}
                    onMouseUp={resetRipple}
                    onMouseLeave={resetRipple}
                >
                    Generate Tailored Resume
                </button>
                <button
                    className="px-5 py-2 bg-white border text-[14px] leading-[20px] font-medium rounded-lg transition-colors hover:bg-[var(--color-surface-container-low)]"
                    style={{ borderColor: "var(--color-outline-variant)", color: "var(--color-on-surface)" }}
                    onClick={onViewDetails}
                    onMouseDown={withRipple}
                    onMouseUp={resetRipple}
                    onMouseLeave={resetRipple}
                >
                    View Details
                </button>
            </div>
        </div>
    );
}