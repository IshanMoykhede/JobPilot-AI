import React from "react";

/**
 * Colored pill used for skill tags.
 *
 * Props:
 *  - label: string
 *  - variant: "success" | "warning" | "error" | "neutral" | "accent" (default "success")
 *  - icon: ReactNode — optional leading icon
 *
 * Usage:
 *   <SkillTag label="AWS" variant="success" />
 *   <SkillTag label="Terraform" variant="warning" />
 *   <SkillTag label="Jenkins CI" variant="error" />
 */
export default function SkillTag({ label, variant = "success", icon = null }) {
  return (
    <span className={`jp-badge jp-badge-${variant}`}>
      {icon}
      {label}
    </span>
  );
}