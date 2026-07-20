import React, { forwardRef } from "react";
import Icon from "../common/Icon";

const Input = forwardRef(({
  label,
  error,
  icon,
  className = "",
  containerClassName = "",
  helpText,
  id,
  ...props
}, ref) => {
  const inputId = id || Math.random().toString(36).substring(7);

  return (
    <div className={`flex flex-col gap-1.5 ${containerClassName}`}>
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-jp-text-primary">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-jp-text-muted">
            <Icon name={icon} className="text-[18px]" />
          </div>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`
            w-full bg-jp-bg-surface border rounded-lg px-4 py-2 text-sm text-jp-text-primary 
            placeholder:text-jp-text-muted transition-colors focus:outline-none focus:ring-1 
            disabled:opacity-50 disabled:cursor-not-allowed
            ${icon ? "pl-10" : ""}
            ${error 
              ? "border-jp-error focus:border-jp-error focus:ring-jp-error" 
              : "border-jp-border focus:border-jp-accent focus:ring-jp-accent"}
            ${className}
          `}
          {...props}
        />
      </div>
      {(error || helpText) && (
        <p className={`text-xs ${error ? "text-jp-error" : "text-jp-text-tertiary"}`}>
          {error || helpText}
        </p>
      )}
    </div>
  );
});

Input.displayName = "Input";

export default Input;
