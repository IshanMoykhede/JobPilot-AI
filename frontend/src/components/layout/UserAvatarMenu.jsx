import React from "react";
import Icon from "../common/Icon";
import { Link } from "react-router-dom";

/**
 * User avatar + notification actions for TopHeader right slot.
 */
export default function UserAvatarMenu({ name = "User" }) {
  const initials = name
    .split(" ")
    .map(w => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="flex items-center gap-1">
      <button
        className="jp-btn-icon jp-btn-ghost"
        aria-label="Notifications"
      >
        <Icon name="notifications" className="text-[20px] text-jp-text-tertiary" />
      </button>
      <Link
        to="/profile"
        className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-jp-bg-raised transition-colors no-underline"
      >
        <div className="w-7 h-7 rounded-full bg-jp-accent-muted flex items-center justify-center text-[10px] font-bold text-jp-accent-text">
          {initials}
        </div>
        <span className="text-[13px] font-medium text-jp-text-secondary hidden sm:inline">
          {name}
        </span>
      </Link>
    </div>
  );
}