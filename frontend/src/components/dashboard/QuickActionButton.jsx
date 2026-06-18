import React from "react";
import Icon, { withRipple, resetRipple } from "../common/Icon";

/**
 * Single quick-action tile used in the Dashboard's "Quick Actions" grid
 * (e.g. New Resume, Browse Jobs, Upload New, View Stats).
 *
 * Props:
 *  - icon: string — Material Symbols icon name
 *  - label: string
 *  - iconBgColor: string — CSS color/rgba for the icon's background circle
 *  - iconColor: string — CSS color for the icon itself
 *  - onClick: () => void
 *
 * Usage:
 *   <QuickActionButton icon="add_task" label="New Resume" iconBgColor="rgba(0,62,199,0.1)" iconColor="var(--color-primary)" />
 *   <QuickActionButton icon="travel_explore" label="Browse Jobs" iconBgColor="rgba(0,84,121,0.1)" iconColor="var(--color-tertiary)" />
 *   <QuickActionButton icon="backup" label="Upload New" iconBgColor="rgba(70,72,212,0.1)" iconColor="var(--color-secondary)" />
 *   <QuickActionButton icon="analytics" label="View Stats" iconBgColor="var(--color-surface-variant)" iconColor="var(--color-on-surface-variant)" />
 */
export default function QuickActionButton({ icon, label, iconBgColor, iconColor, onClick }) {
    return (
        <button
            className="flex flex-col items-center gap-3 p-6 bg-white border rounded-2xl hover:border-[var(--color-primary)] hover:bg-[var(--color-surface-container)] transition-all group"
            style={{ borderColor: "var(--color-outline-variant)" }}
            onClick={onClick}
            onMouseDown={withRipple}
            onMouseUp={resetRipple}
            onMouseLeave={resetRipple}
        >
            <div
                className="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform"
                style={{ backgroundColor: iconBgColor, color: iconColor }}
            >
                <Icon name={icon} />
            </div>
            <span className="text-[14px] leading-[20px] font-bold">{label}</span>
        </button>
    );
}