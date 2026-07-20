import React from "react";
import Icon from "../common/Icon";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  disabled = false,
  isLoading = false,
  icon,
  iconPosition = "left",
  ...props
}) {
  const baseStyles = "inline-flex items-center justify-center font-medium rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-jp-bg-app disabled:opacity-50 disabled:pointer-events-none relative overflow-hidden group";
  
  const variants = {
    primary: "bg-jp-accent text-white hover:bg-jp-accent-hover shadow-[0_0_12px_var(--color-jp-accent-glow)] hover:shadow-[0_0_24px_var(--color-jp-accent-glow)] focus:ring-jp-accent border border-jp-accent/50 hover:-translate-y-0.5",
    secondary: "bg-jp-bg-raised/80 backdrop-blur-md text-jp-text-primary hover:bg-jp-bg-overlay border border-jp-border-subtle hover:border-jp-border-active focus:ring-jp-border shadow-sm hover:shadow-md hover:-translate-y-0.5",
    outline: "bg-transparent text-jp-text-primary border border-jp-border hover:border-jp-border-active hover:bg-white/5 focus:ring-jp-border",
    ghost: "bg-transparent text-jp-text-primary hover:bg-jp-bg-raised focus:ring-jp-border",
    danger: "bg-jp-error text-white hover:bg-jp-error/90 shadow-[0_0_12px_var(--color-jp-error-glow)] focus:ring-jp-error border border-jp-error/50 hover:-translate-y-0.5",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
    icon: "p-2",
  };

  const currentVariant = variants[variant] || variants.primary;
  const currentSize = sizes[size] || sizes.md;

  return (
    <button
      className={`${baseStyles} ${currentVariant} ${currentSize} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Icon name="progress_activity" className="animate-spin mr-2 text-[18px]" />
      ) : icon && iconPosition === "left" ? (
        <Icon name={icon} className={`mr-2 text-[18px]`} />
      ) : null}
      
      {children}
      
      {!isLoading && icon && iconPosition === "right" && (
        <Icon name={icon} className={`ml-2 text-[18px]`} />
      )}
    </button>
  );
}
