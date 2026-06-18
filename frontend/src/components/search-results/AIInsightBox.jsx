import React from "react";
import Icon from "../common/Icon";

/**
 * Blue quote bubble shown inside job result cards, containing an
 * AI-generated tip about how the candidate's experience aligns with
 * the role (e.g. "Your experience with EKS perfectly aligns with
 * their stack...").
 *
 * Usage:
 *   <AIInsightBox text="Your experience with EKS perfectly aligns with their stack. Mentioning your multi-cluster management could secure an interview." />
 *
 * Props:
 *  - text: string — the tip text. Wrap key phrases in <strong> in the
 *      parent if you need bold emphasis, or pass a ReactNode instead of a string.
 *  - icon: string — Material Symbols icon name (default "location_on")
 */
export default function AIInsightBox({ text, icon = "location_on" }) {
    return (
        <div
            className="flex items-start gap-2 p-3 rounded-lg border text-[14px] leading-[20px] italic"
            style={{
                backgroundColor: "var(--color-surface-container-low)",
                borderColor: "var(--color-primary)",
                color: "var(--color-on-surface-variant)",
            }}
        >
            <Icon name={icon} className="text-[18px] mt-0.5 shrink-0" style={{ color: "var(--color-primary)" }} />
            <p>{text}</p>
        </div>
    );
}
