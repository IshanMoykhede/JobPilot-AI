import React from "react";
import Icon from "../common/Icon";

/**
 * Right-side header content used in TopHeader's `right` slot on the
 * Search Results page: notification bell + help icon + user avatar/name.
 *
 * Usage:
 *   <TopHeader left={<Breadcrumb items={...} />} right={<UserAvatarMenu name="Alex Chen" avatarUrl="..." />} />
 *
 * Props:
 *  - name: string
 *  - avatarUrl: string
 *  - onNotificationsClick: () => void
 *  - onHelpClick: () => void
 *  - onAvatarClick: () => void
 */
export default function UserAvatarMenu({
    name = "Alex Chen",
    avatarUrl,
    onNotificationsClick,
    onHelpClick,
    onAvatarClick,
}) {
    return (
        <>
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
                onClick={onHelpClick}
                aria-label="Help"
            >
                <Icon name="help" />
            </button>
            <button
                className="flex items-center gap-2 hover:opacity-80 transition-opacity"
                onClick={onAvatarClick}
            >
                {avatarUrl ? (
                    <img
                        alt={name}
                        className="w-8 h-8 rounded-full object-cover border"
                        style={{ borderColor: "var(--color-outline-variant)" }}
                        src={avatarUrl}
                    />
                ) : (
                    <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-[12px] font-bold"
                        style={{ backgroundColor: "var(--color-primary-container)", color: "var(--color-on-primary-container)" }}
                    >
                        {name
                            .split(" ")
                            .map((w) => w[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase()}
                    </div>
                )}
                <span className="text-[14px] leading-[20px] font-semibold hidden sm:inline" style={{ color: "var(--color-on-surface)" }}>
                    {name}
                </span>
            </button>
        </>
    );
}