import React, { useEffect, useState, createContext, useContext, useCallback } from "react";
import Icon from "./Icon";

const ToastContext = createContext(null);

/**
 * Toast notification system.
 *
 * Wrap your app with <ToastProvider>, then use useToast() to show notifications.
 *
 * Usage:
 *   const toast = useToast();
 *   toast.success("Profile saved!");
 *   toast.error("Something went wrong");
 *   toast.info("Generating resume...");
 */

function ToastItem({ id, message, variant = "info", onRemove }) {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setExiting(true);
      setTimeout(() => onRemove(id), 200);
    }, 4000);
    return () => clearTimeout(timer);
  }, [id, onRemove]);

  const icons = {
    success: "check_circle",
    error: "error",
    info: "info",
    warning: "warning",
  };

  const colors = {
    success: "text-jp-success",
    error: "text-jp-error",
    info: "text-jp-accent",
    warning: "text-jp-warning",
  };

  return (
    <div
      className={`
        flex items-center gap-3 px-4 py-3 rounded-xl bg-jp-bg-overlay border border-jp-border shadow-lg
        min-w-[300px] max-w-[420px] pointer-events-auto
        ${exiting ? 'opacity-0 translate-y-2' : ''}
      `}
      style={{
        animation: exiting ? 'toast-exit 0.2s ease forwards' : 'toast-enter 0.25s ease forwards',
      }}
    >
      <Icon name={icons[variant] || icons.info} fill className={`text-[20px] shrink-0 ${colors[variant]}`} />
      <p className="text-[13px] text-jp-text-primary font-medium flex-1">{message}</p>
      <button
        onClick={() => { setExiting(true); setTimeout(() => onRemove(id), 200); }}
        className="text-jp-text-muted hover:text-jp-text-secondary transition-colors shrink-0"
      >
        <Icon name="close" className="text-[16px]" />
      </button>
    </div>
  );
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((message, variant = "info") => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, variant }]);
  }, []);

  const toast = {
    success: (msg) => addToast(msg, "success"),
    error: (msg) => addToast(msg, "error"),
    info: (msg) => addToast(msg, "info"),
    warning: (msg) => addToast(msg, "warning"),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] flex flex-col-reverse items-center gap-2 pointer-events-none">
        {toasts.map(t => (
          <ToastItem key={t.id} {...t} onRemove={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
