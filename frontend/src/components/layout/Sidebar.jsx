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
      <div className={`flex items-center ${collapsed ? 'justify-center px-2' : 'px-4 justify-between'} h-14 shrink-0`}>
        {collapsed ? (
          <button onClick={onToggle} className="w-8 h-8 rounded-lg bg-jp-accent/10 hover:bg-jp-accent/20 transition-colors flex items-center justify-center group" title="Expand Sidebar">
            <Icon name="menu" className="text-jp-accent text-[18px] group-hover:scale-110 transition-transform" />
          </button>
        ) : (
          <>
            <Link to="/dashboard" className="flex items-center gap-2.5 no-underline hover:opacity-80 transition-opacity">
              <img src="/logo.png" alt="JobPilot Logo" className="w-8 h-8 rounded-lg shadow-sm shadow-jp-accent/30" />
              <span className="text-[15px] font-semibold text-jp-text-primary tracking-tight drop-shadow-sm">
                JobPilot AI
              </span>
            </Link>
            <button 
              onClick={onToggle} 
              className="w-7 h-7 rounded-lg text-jp-text-muted hover:text-jp-accent hover:bg-jp-bg-raised/50 flex items-center justify-center transition-colors"
              title="Collapse Sidebar"
            >
              <Icon name="menu_open" className="text-[18px]" />
            </button>
          </>
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
                flex items-center gap-3 rounded-xl px-3 h-10 text-[13px] font-semibold transition-all duration-300 no-underline relative group overflow-hidden
                ${collapsed ? 'justify-center px-0' : ''}
                ${isActive
                  ? 'bg-jp-accent/10 text-jp-accent-text shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] border border-jp-accent/20'
                  : 'text-jp-text-tertiary hover:text-white hover:bg-jp-bg-raised/50 border border-transparent'
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              {/* Subtle hover gradient */}
              {!isActive && <div className="absolute inset-0 bg-gradient-to-r from-jp-accent/0 to-jp-accent/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>}
              
              <Icon
                name={item.icon}
                fill={isActive}
                className={`text-[20px] relative z-10 transition-transform duration-300 group-hover:scale-110 ${isActive ? 'text-jp-accent drop-shadow-[0_0_8px_var(--color-jp-accent-glow)]' : ''}`}
              />
              {!collapsed && <span className="relative z-10 tracking-wide">{item.label}</span>}
              
              {/* Active Indicator Line */}
              {isActive && !collapsed && <div className="absolute left-0 top-2 bottom-2 w-1 bg-jp-accent rounded-r-full shadow-[0_0_8px_var(--color-jp-accent-glow)]"></div>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="mt-auto px-2 pb-4 space-y-1">
        <div className="jp-divider mb-3" />

        {!collapsed && (
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl mb-2 bg-jp-bg-raised/30 border border-jp-border-subtle hover:bg-jp-bg-raised/60 hover:border-jp-border transition-all duration-300 group cursor-pointer shadow-sm hover:shadow-md">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-jp-accent to-jp-accent-strong flex items-center justify-center text-[12px] font-bold text-white shrink-0 shadow-sm group-hover:shadow-[0_0_12px_var(--color-jp-accent-glow)] transition-shadow">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[13px] font-semibold text-jp-text-primary truncate group-hover:text-white transition-colors tracking-wide">{user?.name || "User"}</p>
              <p className="text-[11px] font-medium text-jp-text-tertiary truncate">{user?.email || ""}</p>
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
          hidden md:flex flex-col h-full shrink-0 border-r border-jp-border-subtle/40 bg-jp-bg-app/60 backdrop-blur-3xl
          transition-all duration-300 overflow-hidden relative z-20 shadow-[4px_0_24px_rgba(0,0,0,0.2)]
          ${collapsed ? 'w-16' : 'w-[260px]'}
        `}
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden animate-fade-in"
            onClick={onMobileClose}
          />
          <aside className="fixed left-0 top-0 bottom-0 w-64 bg-jp-bg-surface border-r border-jp-border-subtle z-50 md:hidden overflow-y-auto"
            style={{ animation: 'slide-in-right 0.2s ease forwards' }}
          >
            {sidebarContent}
          </aside>
        </>
      )}
    </>
  );
}