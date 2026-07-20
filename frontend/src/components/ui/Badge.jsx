import React from "react";

export default function Badge({ children, variant = "default", className = "", ...props }) {
  const variants = {
    default: "bg-jp-bg-raised/80 text-jp-text-secondary border-jp-border-subtle",
    primary: "bg-jp-accent/10 text-jp-accent-text border-jp-accent/30 shadow-[0_0_8px_var(--color-jp-accent-glow)]",
    success: "bg-jp-success/10 text-jp-success-text border-jp-success/30 shadow-[0_0_8px_var(--color-jp-success-glow)]",
    warning: "bg-jp-warning/10 text-jp-warning-text border-jp-warning/30 shadow-[0_0_8px_var(--color-jp-warning-glow)]",
    error: "bg-jp-error/10 text-jp-error-text border-jp-error/30 shadow-[0_0_8px_var(--color-jp-error-glow)]",
  };

  const currentVariant = variants[variant] || variants.default;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold uppercase tracking-wider border backdrop-blur-sm ${currentVariant} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
