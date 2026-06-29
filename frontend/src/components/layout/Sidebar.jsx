import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Icon from "../common/Icon";
import { useAuth } from "../../context/AuthContext";

const NAV_ITEMS = [
  { key: "dashboard", path: "/dashboard", label: "Dashboard", icon: "space_dashboard" },
  { key: "search", path: "/search", label: "Job Search", icon: "search" },
  { key: "resumes", path: "/resumes", label: "Resumes", icon: "description" },
  { key: "profile", path: "/profile", label: "Profile", icon: "person" },
  { key: "insights", path: "/insights", label: "Career Agent", icon: "auto_awesome" },
  { key: "evidence", path: "/evidence", label: "Graph Engine", icon: "memory" },
];

export default function Sidebar({ collapsed = false, onToggle, mobileOpen = false, onMobileClose }) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const activeKey = NAV_ITEMS.find(item => location.pathname.startsWith(item.path))?.key || "dashboard";

  const initials = user?.name
    ? user.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
    : "U";

  const handleLogout = () => {
    logout();
  };

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={`flex items-center ${collapsed ? 'justify-center px-2' : 'px-4'} h-14 shrink-0`}>
        {collapsed ? (
          <div className="w-8 h-8 rounded-lg bg-jp-accent flex items-center justify-center">
            <Icon name="bolt" fill className="text-white text-[18px]" />
          </div>
        ) : (
          <Link to="/dashboard" className="flex items-center gap-2.5 no-underline">
            <div className="w-8 h-8 rounded-lg bg-jp-accent flex items-center justify-center shrink-0">
              <Icon name="bolt" fill className="text-white text-[18px]" />
            </div>
            <span className="text-[15px] font-semibold text-jp-text-primary tracking-tight">
              JobPilot AI
            </span>
          </Link>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-0.5">
        {NAV_ITEMS.map(item => {
          const isActive = item.key === activeKey;
          return (
            <Link
              key={item.key}
              to={item.path}
              onClick={onMobileClose}
              className={`
                flex items-center gap-3 rounded-lg px-3 h-9 text-[13px] font-medium transition-colors no-underline
                ${collapsed ? 'justify-center px-0' : ''}
                ${isActive
                  ? 'bg-jp-accent-muted text-jp-accent-text'
                  : 'text-jp-text-tertiary hover:text-jp-text-secondary hover:bg-jp-bg-raised'
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                name={item.icon}
                fill={isActive}
                className={`text-[20px] ${isActive ? 'text-jp-accent' : ''}`}
              />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="mt-auto px-2 pb-4 space-y-1">
        <div className="jp-divider mb-3" />

        {!collapsed && (
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg mb-2">
            <div className="w-8 h-8 rounded-full bg-jp-accent-muted flex items-center justify-center text-[11px] font-bold text-jp-accent-text shrink-0">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[13px] font-medium text-jp-text-primary truncate">{user?.name || "User"}</p>
              <p className="text-[11px] text-jp-text-muted truncate">{user?.email || ""}</p>
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className={`
            flex items-center gap-3 rounded-lg px-3 h-9 text-[13px] font-medium w-full transition-colors
            text-jp-text-tertiary hover:text-jp-error hover:bg-jp-error-muted
            ${collapsed ? 'justify-center px-0' : ''}
          `}
          title={collapsed ? "Log out" : undefined}
        >
          <Icon name="logout" className="text-[20px]" />
          {!collapsed && <span>Log out</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={`
          hidden md:flex flex-col h-full shrink-0 border-r border-jp-border-subtle bg-jp-bg-app
          transition-all duration-200 overflow-hidden
          ${collapsed ? 'w-16' : 'w-60'}
        `}
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 z-40 md:hidden animate-fade-in"
            onClick={onMobileClose}
          />
          <aside className="fixed left-0 top-0 bottom-0 w-64 bg-jp-bg-app border-r border-jp-border-subtle z-50 md:hidden animate-slide-in-right overflow-y-auto"
            style={{ animation: 'slide-in-right 0.2s ease forwards' }}
          >
            {sidebarContent}
          </aside>
        </>
      )}
    </>
  );
}