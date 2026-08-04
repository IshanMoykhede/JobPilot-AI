import React from "react";
import Icon from "../common/Icon";
import { Link, useLocation } from "react-router-dom";

export default function TopHeader({ right = null, onMenuClick }) {
  const location = useLocation();

  const navItems = [
    { name: "Job Search", path: "/search", icon: "search" },
    { name: "Resumes", path: "/resumes", icon: "description" },
    { name: "Profile", path: "/profile", icon: "person" }
  ];

  return (
    <header className="flex items-center justify-center w-full pt-4 pb-2 px-6 sticky top-0 z-40 bg-transparent pointer-events-none">
      <div className="flex items-center justify-between w-full max-w-5xl pointer-events-auto bg-jp-bg-surface/60 backdrop-blur-xl border border-jp-border-subtle rounded-full px-4 py-2 shadow-xl">
        
        {/* Left: Brand/Logo (Optional, could just be empty or a subtle logo) */}
        <div className="flex items-center gap-2 pr-4">
          <button
            onClick={onMenuClick}
            className="md:hidden p-2 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-raised rounded-full transition-colors"
            aria-label="Open menu"
          >
            <Icon name="menu" className="text-[20px]" />
          </button>
          <div className="hidden md:flex items-center gap-2 pl-2">
            <Icon name="work" className="text-jp-accent text-[20px]" />
            <span className="font-black text-white text-[14px] tracking-widest uppercase">JobPilot</span>
          </div>
        </div>

        {/* Center: Navigation Links */}
        <nav className="flex items-center gap-1 bg-black/20 p-1 rounded-full border border-white/5">
          {navItems.map(item => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-full text-[13px] font-semibold transition-all duration-300
                  ${isActive 
                    ? "bg-jp-accent text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]" 
                    : "text-jp-text-secondary hover:text-white hover:bg-white/5"
                  }
                `}
              >
                <Icon name={item.icon} className="text-[16px]" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Right: User Avatar */}
        <div className="flex items-center pl-4">
          {right}
        </div>
      </div>
    </header>
  );
}