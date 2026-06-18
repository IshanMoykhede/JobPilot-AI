import React from "react";

/**
 * Sticky top header bar shell, shared across all pages.
 * Content differs per page, so `left` and `right` are passed in as nodes.
 *
 * Dashboard usage:
 *   <TopHeader
 *     left={<GlobalSearchInput />}
 *     right={<><NavLinks /><NotificationButton /><HistoryButton /></>}
 *   />
 *
 * Search Results usage:
 *   <TopHeader
 *     left={<Breadcrumbs items={["Dashboard", "Search Results"]} />}
 *     right={<UserAvatarMenu />}
 *   />
 */
export default function TopHeader({ left = null, right = null }) {
    return (
        <header
            className="flex justify-between items-center h-16 w-full px-8 sticky top-0 z-40 backdrop-blur-md border-b"
            style={{
                backgroundColor: "rgba(248,249,255,0.8)",
                borderColor: "rgba(195,197,217,0.3)",
            }}
        >
            <div className="flex items-center gap-6">{left}</div>
            <div className="flex items-center gap-4">{right}</div>
        </header>
    );
}