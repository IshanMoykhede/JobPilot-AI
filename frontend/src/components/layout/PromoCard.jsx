import React from "react";
import { withRipple, resetRipple } from "../common/Icon";

/**
 * Sidebar "bottom card" variant for the Search Results page.
 * Shows a short promo message and an "Upgrade to Pro" CTA.
 *
 * Usage:
 *   <Sidebar activeItem="search" bottomCard={<PromoCard />} />
 *
 * Props:
 *  - title: string
 *  - message: string
 *  - buttonLabel: string
 *  - onUpgradeClick: () => void
 */
export default function PromoCard({
    title = "Power up your search",
    message = "Get unlimited AI-tailored resumes and priority job matches.",
    buttonLabel = "Upgrade to Pro",
    onUpgradeClick,
}) {
    return (
        <div
            className="rounded-xl p-4 border"
            style={{
                backgroundColor: "var(--color-surface-container-low)",
                borderColor: "var(--color-outline-variant)",
            }}
        >
            <p className="text-[14px] leading-[20px] font-bold mb-1" style={{ color: "var(--color-on-surface)" }}>
                {title}
            </p>
            <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium mb-3" style={{ color: "var(--color-on-surface-variant)" }}>
                {message}
            </p>
            <button
                className="w-full py-2 text-[14px] leading-[20px] font-semibold rounded-lg transition-colors hover:opacity-90"
                style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-on-primary)",
                }}
                onClick={onUpgradeClick}
                onMouseDown={withRipple}
                onMouseUp={resetRipple}
                onMouseLeave={resetRipple}
            >
                {buttonLabel}
            </button>
        </div>
    );
}