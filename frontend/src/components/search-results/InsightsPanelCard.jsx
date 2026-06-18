import React from "react";
import Icon from "../common/Icon";

/**
 * Generic bordered card shell for the Search Results right-side
 * "AI Search Insights" panel. Used for:
 *  - "Most Common Skills Found" (with SkillProgressBar children)
 *  - "Market Intelligence" (with plain text children)
 *  - "Profile Optimization" (highlighted variant with CTA button)
 *
 * Props:
 *  - icon: string — Material Symbols icon name (optional)
 *  - title: string
 *  - variant: "default" | "highlight" | "alert" (default "default")
 *      - "default": white/neutral card
 *      - "highlight": filled with primary color (e.g. Profile Optimization)
 *      - "alert": orange/red tinted card (e.g. Skills to Learn)
 *  - children: ReactNode — card body content
 *
 * Usage:
 *   <InsightsPanelCard icon="insights" title="Most Common Skills Found">
 *     <SkillProgressBar label="AWS" percentage={80} />
 *     <SkillProgressBar label="Docker" percentage={65} />
 *   </InsightsPanelCard>
 *
 *   <InsightsPanelCard title="Skills to Learn" variant="alert">
 *     <p>Terraform, Jenkins, CI/CD appear in 60%+ of your search results.</p>
 *   </InsightsPanelCard>
 *
 *   <InsightsPanelCard icon="auto_awesome" title="Profile Optimization" variant="highlight">
 *     <p>Add deployment metrics...</p>
 *     <button>Apply Recommendations</button>
 *   </InsightsPanelCard>
 */

const VARIANT_STYLES = {
    default: {
        backgroundColor: "var(--color-surface-container-lowest)",
        borderColor: "var(--color-outline-variant)",
        titleColor: "var(--color-on-surface)",
        bodyColor: "var(--color-on-surface-variant)",
    },
    highlight: {
        backgroundColor: "var(--color-primary)",
        borderColor: "var(--color-primary)",
        titleColor: "var(--color-on-primary)",
        bodyColor: "var(--color-on-primary)",
    },
    alert: {
        backgroundColor: "#fff7ed", // orange-50
        borderColor: "#fed7aa", // orange-200
        titleColor: "#c2410c", // orange-700
        bodyColor: "#9a3412", // orange-800
    },
};

export default function InsightsPanelCard({ icon, title, variant = "default", children }) {
    const styles = VARIANT_STYLES[variant] || VARIANT_STYLES.default;

    return (
        <div
            className="rounded-xl border p-4 space-y-3"
            style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}
        >
            <h3
                className="text-[12px] leading-[16px] tracking-[0.01em] font-bold uppercase tracking-widest flex items-center gap-2"
                style={{ color: styles.titleColor }}
            >
                {icon && <Icon name={icon} className="text-[16px]" />}
                {title}
            </h3>
            <div className="text-[14px] leading-[20px]" style={{ color: styles.bodyColor }}>
                {children}
            </div>
        </div>
    );
}