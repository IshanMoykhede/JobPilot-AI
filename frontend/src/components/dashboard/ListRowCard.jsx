import React from "react";
import Icon from "../common/Icon";

/**
 * Generalized white card row used for:
 *  - "Recent Resumes" items (icon + title + subtitle + download button)
 *  - "Search History" items (icon + title + subtitle + timestamp text)
 *
 * Structure: [icon box] [title + subtitle] ............ [right slot]
 *
 * Props:
 *  - icon: string — Material Symbols icon name
 *  - iconFill: boolean — whether the icon should use filled style (default false)
 *  - iconBgColor: string — CSS color/rgba for the icon's background box
 *  - iconColor: string — CSS color for the icon itself
 *  - title: string
 *  - subtitle: string
 *  - right: ReactNode — content for the right side (button or text)
 *  - hoverEffect: boolean — apply hover border/shadow (default true, used for Recent Resumes)
 *
 * Usage (Recent Resumes):
 *   <ListRowCard
 *     icon="picture_as_pdf"
 *     iconFill
 *     iconBgColor="#fef2f2"   // bg-red-50
 *     iconColor="#ef4444"     // text-red-500
 *     title="DevOps @ Infosys"
 *     subtitle="Generated 2h ago"
 *     right={
 *       <button className="p-2 rounded-lg ..." style={{ color: "var(--color-outline)" }}>
 *         <Icon name="download" />
 *       </button>
 *     }
 *   />
 *
 * Usage (Search History):
 *   <ListRowCard
 *     icon="history"
 *     iconBgColor="var(--color-surface-container)"
 *     iconColor="var(--color-on-surface-variant)"
 *     title="Cloud Engineer in Bangalore"
 *     subtitle="12 results found"
 *     right={<p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium" style={{ color: "var(--color-outline)" }}>2d ago</p>}
 *     hoverEffect={false}
 *   />
 */
export default function ListRowCard({
    icon,
    iconFill = false,
    iconBgColor,
    iconColor,
    title,
    subtitle,
    right = null,
    hoverEffect = true,
}) {
    return (
        <div
            className={`group flex items-center justify-between p-4 bg-white border rounded-xl transition-all ${hoverEffect ? "hover:border-[var(--color-primary)]/50 hover:shadow-sm" : ""
                }`}
            style={{ borderColor: "var(--color-outline-variant)" }}
        >
            <div className="flex items-center gap-3">
                <div
                    className="w-10 h-10 rounded flex items-center justify-center"
                    style={{ backgroundColor: iconBgColor, color: iconColor }}
                >
                    <Icon name={icon} fill={iconFill} />
                </div>
                <div>
                    <p className="text-[14px] leading-[20px] font-bold">{title}</p>
                    <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium" style={{ color: "var(--color-outline)" }}>
                        {subtitle}
                    </p>
                </div>
            </div>
            {right}
        </div>
    );
}