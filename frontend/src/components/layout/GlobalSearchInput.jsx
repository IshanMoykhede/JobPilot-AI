import React from "react";
import Icon from "../common/Icon";

/**
 * Small search input used in TopHeader's `left` slot on the Dashboard page.
 *
 * Usage:
 *   <TopHeader left={<GlobalSearchInput />} right={...} />
 *
 * Props:
 *  - placeholder: string
 *  - value, onChange: standard controlled-input props (optional)
 */
export default function GlobalSearchInput({
    placeholder = "Global Search...",
    value,
    onChange,
}) {
    return (
        <div className="relative">
            <span className="absolute inset-y-0 left-3 flex items-center" style={{ color: "var(--color-outline)" }}>
                <Icon name="search" className="text-[16px]" />
            </span>
            <input
                className="pl-10 pr-4 py-1.5 border-none rounded-lg text-[14px] leading-[20px] font-medium w-64 focus:ring-2 focus:ring-[var(--color-primary)]/20"
                style={{ backgroundColor: "var(--color-surface-container-low)" }}
                placeholder={placeholder}
                type="text"
                value={value}
                onChange={onChange}
            />
        </div>
    );
}