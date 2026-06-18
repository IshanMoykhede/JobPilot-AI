import React from "react";
import Icon from "../common/Icon";

/**
 * Right-side header actions used in TopHeader's `right` slot on the Dashboard page:
 * Network/Activity nav links + notification bell + history icon button.
 *
 * Usage:
 *   <TopHeader left={<GlobalSearchInput />} right={<HeaderNavActions />} />
 *
 * Props:
 *  - links: Array<{ label: string, href?: string, onClick?: () => void }>
 *      Defaults to [Network, Activity]
 *  - onNotificationsClick: () => void
 *  - onHistoryClick: () => void
 */
export default function HeaderNavActions({
    links = [
        { label: "Network", href: "#" },
        { label: "Activity", href: "#" },
    ],
    onNotificationsClick,
    onHistoryClick,
}) {
    return (
        <>
            <nav className="flex gap-4 mr-4">
                {links.map((link) => (
                    <a
                        key={link.label}
                        href={link.href || "#"}
                        onClick={link.onClick}
                        className="text-[12px] leading-[16px] tracking-[0.01em] font-medium hover:text-[var(--color-primary)] transition-colors"
                        style={{ color: "var(--color-on-surface-variant)" }}
                    >
                        {link.label}
                    </a>
                ))}
            </nav>
            <button
                className="hover:text-[var(--color-primary)] transition-opacity"
                style={{ color: "var(--color-on-surface-variant)" }}
                onClick={onNotificationsClick}
                aria-label="Notifications"
            >
                <Icon name="notifications" />
            </button>
            <button
                className="hover:text-[var(--color-primary)] transition-opacity"
                style={{ color: "var(--color-on-surface-variant)" }}
                onClick={onHistoryClick}
                aria-label="History"
            >
                <Icon name="history_edu" />
            </button>
        </>
    );
}