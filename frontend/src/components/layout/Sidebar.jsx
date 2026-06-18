import React from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../common/Icon";
import { useAuth } from "../../context/AuthContext";

/**
 * Left navigation sidebar, shared across all pages.
 *
 * Props:
 *  - activeItem: string — which nav key is highlighted.
 *      One of: "dashboard" | "search" | "resumes" | "profile"
 *  - bottomCard: ReactNode — custom content rendered above
 *      "Help Center" / "Log Out" (e.g. user profile card on
 *      Dashboard, or "Power up your search" promo on Search Results)
 *
 * Usage:
 *   <Sidebar activeItem="dashboard" bottomCard={<UserProfileCard />} />
 *   <Sidebar activeItem="search" bottomCard={<UpgradePromoCard />} />
 */

const NAV_ITEMS = [
    { key: "dashboard", label: "Dashboard", icon: "dashboard" },
    { key: "search", label: "Job Searches", icon: "search" },
    { key: "resumes", label: "Generated Resumes", icon: "description" },
    { key: "profile", label: "Profile", icon: "person" },
];

export default function Sidebar({ activeItem = "dashboard", bottomCard = null }) {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/auth");
    };

    return (
        <aside
            className="hidden md:flex flex-col h-full w-64 border-r py-6 px-4 shrink-0 overflow-y-auto"
            style={{
                borderColor: "var(--color-outline-variant)",
                backgroundColor: "var(--color-surface)",
            }}
        >
            {/* Logo */}
            <div className="mb-10 px-2">
                <div className="flex items-center gap-3">
                    <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{
                            backgroundColor: "var(--color-primary)",
                            color: "var(--color-on-primary)",
                        }}
                    >
                        <Icon name="rocket_launch" fill />
                    </div>
                    <div>
                        <h1
                            className="text-[20px] leading-[28px] font-bold tracking-[-0.01em]"
                            style={{ color: "var(--color-primary)" }}
                        >
                            JobPilot AI
                        </h1>
                        <p
                            className="text-[12px] leading-[16px] tracking-[0.01em] font-medium"
                            style={{ color: "var(--color-on-surface-variant)" }}
                        >
                            AI Career Engine
                        </p>
                    </div>
                </div>
            </div>

            {/* Nav links */}
            <nav className="flex-1 space-y-1">
                {NAV_ITEMS.map((item) => {
                    const isActive = item.key === activeItem;
                    const path = item.key === "dashboard" ? "/dashboard" : `/${item.key}`;
                    return (
                        <a
                            key={item.key}
                            href={path}
                            className="flex items-center gap-3 rounded-lg px-3 py-2 transition-colors"
                            style={
                                isActive
                                    ? {
                                        backgroundColor: "var(--color-surface-container)",
                                        color: "var(--color-primary)",
                                        fontWeight: 600,
                                    }
                                    : { color: "var(--color-on-surface-variant)" }
                            }
                            onMouseEnter={(e) => {
                                if (!isActive) e.currentTarget.style.backgroundColor = "var(--color-surface-container-low)";
                            }}
                            onMouseLeave={(e) => {
                                if (!isActive) e.currentTarget.style.backgroundColor = "transparent";
                            }}
                        >
                            <Icon name={item.icon} />
                            <span className="text-[14px] leading-[20px] font-medium">{item.label}</span>
                        </a>
                    );
                })}
            </nav>

            {/* Bottom section */}
            <div className="mt-auto space-y-4">
                {bottomCard}

                <div className="space-y-1">
                    <a
                        href="#"
                        className="flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-[var(--color-surface-container-low)]"
                        style={{ color: "var(--color-on-surface-variant)" }}
                    >
                        <Icon name="help" />
                        <span className="text-[14px] leading-[20px] font-medium">Help Center</span>
                    </a>
                    <a
                        href="#"
                        className="flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-[rgba(186,26,26,0.08)]"
                        style={{ color: "var(--color-error)" }}
                        onClick={(e) => { e.preventDefault(); handleLogout(); }}
                    >
                        <Icon name="logout" />
                        <span className="text-[14px] leading-[20px] font-medium">Log Out</span>
                    </a>
                </div>
            </div>
        </aside>
    );
}