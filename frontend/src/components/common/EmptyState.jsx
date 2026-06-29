import React from "react";
import Icon from "./Icon";

/**
 * Empty state placeholder for sections with no data.
 *
 * Usage:
 *   <EmptyState
 *     icon="description"
 *     title="No resumes yet"
 *     description="Generate your first tailored resume to get started."
 *     action={{ label: "Generate Resume", onClick: () => {} }}
 *   />
 */
export default function EmptyState({
  icon = "inbox",
  title = "Nothing here yet",
  description = "",
  action = null,
  className = "",
}) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 px-6 text-center ${className}`}>
      <div className="w-12 h-12 rounded-xl bg-jp-bg-raised flex items-center justify-center mb-4">
        <Icon name={icon} className="text-[24px] text-jp-text-muted" />
      </div>
      <h3 className="text-[15px] font-semibold text-jp-text-primary mb-1">{title}</h3>
      {description && (
        <p className="text-[13px] text-jp-text-tertiary max-w-xs mb-5">{description}</p>
      )}
      {action && (
        <button
          className="jp-btn jp-btn-primary jp-btn-sm"
          onClick={action.onClick}
        >
          {action.icon && <Icon name={action.icon} className="text-[16px]" />}
          {action.label}
        </button>
      )}
    </div>
  );
}
