import React from "react";
import { Link } from "react-router-dom";
import Icon from "../common/Icon";

/**
 * Breadcrumb trail for TopHeader.
 * Last item is rendered as active (not a link).
 */
export default function Breadcrumb({ items = [] }) {
  return (
    <nav className="flex items-center gap-1.5">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <React.Fragment key={item.label}>
            {isLast ? (
              <span className="text-[13px] font-medium text-jp-text-primary">
                {item.label}
              </span>
            ) : (
              <Link
                to={item.href || "#"}
                className="text-[13px] font-medium text-jp-text-tertiary hover:text-jp-text-secondary transition-colors no-underline"
              >
                {item.label}
              </Link>
            )}
            {!isLast && (
              <Icon name="chevron_right" className="text-[14px] text-jp-text-muted" />
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}