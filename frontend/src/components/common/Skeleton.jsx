import React from "react";

/**
 * Skeleton loading placeholder.
 *
 * Props:
 *  - variant: "text" | "circle" | "rect" (default "text")
 *  - width: CSS width (default "100%")
 *  - height: CSS height (default depends on variant)
 *  - count: number of lines for text variant (default 1)
 *  - className: additional classes
 *
 * Usage:
 *   <Skeleton variant="text" count={3} />
 *   <Skeleton variant="circle" width={40} height={40} />
 *   <Skeleton variant="rect" height={120} />
 */
export default function Skeleton({
  variant = "text",
  width,
  height,
  count = 1,
  className = "",
}) {
  if (variant === "circle") {
    const size = width || height || 40;
    return (
      <div
        className={`jp-skeleton rounded-full shrink-0 ${className}`}
        style={{ width: size, height: size }}
      />
    );
  }

  if (variant === "rect") {
    return (
      <div
        className={`jp-skeleton ${className}`}
        style={{
          width: width || "100%",
          height: height || 120,
          borderRadius: "var(--radius-lg)",
        }}
      />
    );
  }

  // Text variant
  return (
    <div className={`space-y-2 ${className}`} style={{ width: width || "100%" }}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="jp-skeleton"
          style={{
            height: height || 14,
            width: i === count - 1 && count > 1 ? "70%" : "100%",
          }}
        />
      ))}
    </div>
  );
}
