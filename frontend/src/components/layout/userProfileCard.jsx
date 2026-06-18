import React from "react";
import Icon, { withRipple, resetRipple } from "../common/Icon";

/**
 * Sidebar "bottom card" variant for the Dashboard page.
 * Shows user avatar (or initials), name, status badge, and an "Upgrade Plan" CTA.
 *
 * Props:
 *  - name: string
 *  - avatarUrl: string (optional, falls back to initials)
 *  - statusLabel: string  (e.g. "Resume Uploaded")
 *  - onUpgradeClick: () => void
 */
export default function UserProfileCard({
    name = "User",
    avatarUrl,
    statusLabel = "Free Plan",
    onUpgradeClick,
}) {
    const initials = name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);

    return (
        <div
            className="rounded-xl p-4 border"
            style={{
                backgroundColor: "var(--color-surface-container-lowest)",
                borderColor: "var(--color-outline-variant)",
            }}
        >
            <div className="flex items-center gap-3 mb-3">
                {avatarUrl ? (
                    <img
                        alt="User Avatar"
                        className="w-10 h-10 rounded-full object-cover border"
                        style={{ borderColor: "var(--color-outline-variant)" }}
                        src={avatarUrl}
                    />
                ) : (
                    <div
                        className="w-10 h-10 rounded-full flex items-center justify-center text-[14px] font-bold"
                        style={{
                            backgroundColor: "var(--color-primary)",
                            color: "var(--color-on-primary)",
                        }}
                    >
                        {initials}
                    </div>
                )}
                <div>
                    <p className="text-[14px] leading-[20px] font-bold" style={{ color: "var(--color-on-surface)" }}>
                        {name}
                    </p>
                    <p
                        className="text-[10px] flex items-center gap-1 font-semibold uppercase tracking-wider"
                        style={{ color: "var(--color-primary)" }}
                    >
                        <Icon name="check_circle" fill className="text-[12px]" />
                        {statusLabel}
                    </p>
                </div>
            </div>
            <button
                className="w-full py-2 text-[14px] leading-[20px] font-semibold rounded-lg transition-colors border"
                style={{
                    backgroundColor: "var(--color-surface-container-highest)",
                    color: "var(--color-on-surface)",
                    borderColor: "rgba(115,118,136,0.3)",
                }}
                onClick={onUpgradeClick}
                onMouseDown={withRipple}
                onMouseUp={resetRipple}
                onMouseLeave={resetRipple}
            >
                Upgrade Plan
            </button>
        </div>
    );
}