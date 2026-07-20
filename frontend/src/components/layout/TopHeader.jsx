import React from "react";
import Icon from "../common/Icon";
import { Link } from "react-router-dom";

/**
 * Sticky top header bar for authenticated pages.
 * Renders left slot (breadcrumb) and right slot (user menu + actions).
 */
export default function TopHeader({ left = null, right = null, onMenuClick }) {
  return (
    <header className="flex items-center justify-between h-14 w-full px-6 sticky top-0 z-30 bg-transparent border-none">
      <div className="flex items-center gap-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-surface rounded-md transition-colors"
          aria-label="Open menu"
        >
          <Icon name="menu" className="text-[20px]" />
        </button>
        {left}
      </div>
      <div className="flex items-center gap-2">
        {right}
      </div>
    </header>
  );
}