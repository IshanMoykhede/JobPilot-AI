import React from "react";

export function Card({ className = "", children, interactive = false, ...props }) {
  return (
    <div 
      className={`
        relative bg-jp-bg-surface/80 backdrop-blur-xl border border-jp-border-subtle rounded-2xl 
        shadow-sm overflow-hidden
        ${interactive ? 'hover:border-jp-border-active hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 cursor-pointer group' : ''}
        ${className}
      `} 
      {...props}
    >
      {/* Subtle top gradient for depth */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none" />
      {children}
    </div>
  );
}

export function CardHeader({ className = "", children, ...props }) {
  return (
    <div className={`flex flex-col space-y-2 p-6 pb-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className = "", children, ...props }) {
  return (
    <h3 className={`text-[16px] font-semibold tracking-tight text-jp-text-primary ${className}`} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className = "", children, ...props }) {
  return (
    <p className={`text-[13px] text-jp-text-tertiary leading-relaxed ${className}`} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className = "", children, ...props }) {
  return (
    <div className={`p-6 pt-0 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className = "", children, ...props }) {
  return (
    <div className={`flex items-center p-6 pt-4 border-t border-jp-border-subtle/50 bg-jp-bg-overlay/20 ${className}`} {...props}>
      {children}
    </div>
  );
}
