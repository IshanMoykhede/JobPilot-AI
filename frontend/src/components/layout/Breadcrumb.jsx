import React from "react";
import Icon from "../common/Icon";

/**
 * Breadcrumb trail used in TopHeader's `left` slot (e.g. "Dashboard › Search Results").
 *
 * Usage:
 *   <TopHeader left={<Breadcrumb items={[
 *     { label: "Dashboard", href: "/" },
 *     { label: "Search Results" },
 *   ]} />} right={<UserAvatarMenu />} />
 *
 * Props:
 *  - items: Array<{ label: string, href?: string, onClick?: () => void }>
 *      The last item is rendered as the active/current page (highlighted, no link styling).
 */
export default function Breadcrumb({ items = [] }) {
    return (
        <nav className="flex items-center gap-2">
            {items.map((item, index) => {
                const isLast = index === items.length - 1;
                return (
                    <React.Fragment key={item.label}>
                        {isLast ? (
                            <span className="text-[14px] leading-[20px] font-semibold" style={{ color: "var(--color-primary)" }}>
                                {item.label}
                            </span>
                        ) : (
                            <a
                                href={item.href || "#"}
                                onClick={item.onClick}
                                className="text-[14px] leading-[20px] font-medium hover:text-[var(--color-primary)] transition-colors"
                                style={{ color: "var(--color-on-surface-variant)" }}
                            >
                                {item.label}
                            </a>
                        )}
                        {!isLast && (
                            <Icon name="chevron_right" className="text-[16px]" style={{ color: "var(--color-outline)" }} />
                        )}
                    </React.Fragment>
                );
            })}
        </nav>
    );
}