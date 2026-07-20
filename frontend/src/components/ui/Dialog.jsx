import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import Icon from "../common/Icon";

export function Dialog({ isOpen, onClose, children, className = "", title }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />
      
      {/* Dialog Content */}
      <div className={`relative z-10 w-full max-w-lg p-6 bg-jp-bg-surface border border-jp-border rounded-xl shadow-2xl animate-scale-in ${className}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          {title && <h2 className="text-lg font-semibold text-jp-text-primary">{title}</h2>}
          <button 
            onClick={onClose}
            className="p-1 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-raised rounded-md transition-colors ml-auto"
          >
            <Icon name="close" className="text-[20px]" />
          </button>
        </div>

        {/* Body */}
        <div>{children}</div>
      </div>
    </div>,
    document.body
  );
}
