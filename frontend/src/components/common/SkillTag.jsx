import React from "react";

/**
 * Colored pill used for skill tags throughout the app
 * (e.g. "AWS", "Docker" in green for matching/known skills,
 * "Terraform", "Jenkins" in orange for missing/gap skills).
 *
 * Props:
 *  - label: string
 *  - variant: "green" | "orange" | "red" | "neutral" (default "green")
 *  - icon: ReactNode — optional leading icon (e.g. for "✗ Terraform" style)
 *
 * Usage:
 *   <SkillTag label="AWS" variant="green" />
 *   <SkillTag label="Terraform" variant="orange" />
 *   <SkillTag label="Jenkins CI" variant="red" />
 */

const VARIANT_CLASSES = {
    green: "bg-green-50 text-green-700 border-green-100",
    orange: "bg-orange-50 text-orange-700 border-orange-100",
    red: "bg-red-50 text-red-700 border-red-100",
    neutral: "bg-gray-50 text-gray-700 border-gray-100",
};

export default function SkillTag({ label, variant = "green", icon = null }) {
    const colorClasses = VARIANT_CLASSES[variant] || VARIANT_CLASSES.green;

    return (
        <span
            className={`px-3 py-1 text-[12px] leading-[16px] tracking-[0.01em] font-semibold rounded-md border inline-flex items-center gap-1 ${colorClasses}`}
        >
            {icon}
            {label}
        </span>
    );
}