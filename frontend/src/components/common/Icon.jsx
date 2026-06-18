import React from "react";

/**
 * Material Symbols icon wrapper.
 *
 * Usage:
 *   <Icon name="dashboard" />
 *   <Icon name="check_circle" fill className="text-[12px]" />
 *
 * Requires this stylesheet to be loaded once (e.g. in index.html or App.jsx):
 *   <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
 */
export default function Icon({ name, fill = false, className = "", style = {} }) {
    return (
        <span
            className={`material-symbols-outlined ${className}`}
            style={{
                fontVariationSettings: fill
                    ? "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24"
                    : "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24",
                ...style,
            }}
        >
            {name}
        </span>
    );
}

/**
 * Shared "press" micro-interaction handlers used on buttons/links
 * throughout the app (slight scale-down on press).
 *
 * Usage:
 *   <button onMouseDown={withRipple} onMouseUp={resetRipple} onMouseLeave={resetRipple}>
 */
export function withRipple(e) {
    e.currentTarget.style.transform = "scale(0.98)";
}

export function resetRipple(e) {
    e.currentTarget.style.transform = "scale(1)";
}