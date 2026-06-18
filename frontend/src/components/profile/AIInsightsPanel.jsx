import React from 'react';
import Icon from '../common/Icon';

export default function AIInsightsPanel({
  profileData,
  strengthScore,
  triggerToast,
  setProfileExists,
  setActiveStep
}) {
  return (
    <aside className="hidden lg:flex flex-col w-80 h-full border-l bg-white p-6 shrink-0 overflow-y-auto" style={{ borderColor: "var(--color-outline-variant)" }}>
      <h2 className="text-[20px] font-semibold mb-6 text-on-surface">AI Insights & Action</h2>

      <div className="space-y-6">
        {/* Profile Strength SVG Circle Gauge */}
        <div className="text-center p-6 rounded-2xl border" style={{ backgroundColor: "var(--color-surface-container-low)", borderColor: "rgba(195,197,217,0.5)" }}>
          <div className="mx-auto mb-4 flex justify-center">
            <div className="relative w-32 h-32 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" className="text-surface-container" stroke="currentColor" strokeWidth="8" fill="none" />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  className="text-primary transition-all duration-700"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray="351.8"
                  strokeDashoffset={351.8 - (351.8 * strengthScore) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-[24px] font-extrabold text-primary">{strengthScore}%</span>
                <span className="text-[10px] text-outline font-bold uppercase tracking-wider">Strength</span>
              </div>
            </div>
          </div>
          <p className="text-[14px] font-bold text-on-surface">
            {strengthScore === 100
              ? "Perfect Context Alignment!"
              : strengthScore > 75
              ? "Strong Matching Index"
              : "Needs Skill Optimization"}
          </p>
          <p className="text-[12px] text-outline mt-1 leading-normal">
            {strengthScore === 100
              ? "Excellent profile depth for job match engines."
              : "Improve your profile details for optimized job suggestions."}
          </p>
        </div>

        {/* Resume Metadata File details */}
        <div className="p-4 border border-outline-variant/60 rounded-xl bg-surface-container-lowest space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-[11px] font-bold text-outline uppercase tracking-wider">Active Resume Context</span>
            <span className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-0.5 rounded">PDF</span>
          </div>
          <div className="flex items-center gap-3 bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/30">
            <Icon name="picture_as_pdf" className="text-error text-[28px]" fill />
            <div className="overflow-hidden">
              <p className="text-[12px] font-bold text-on-surface truncate">
                {profileData.resume_metadata.file_name || "Extracted_Document.pdf"}
              </p>
              <p className="text-[10px] text-outline">
                Uploaded {profileData.resume_metadata.uploaded_at ? new Date(profileData.resume_metadata.uploaded_at).toLocaleDateString() : "recently"}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              if (window.confirm("Replacing the resume file will overwrite your existing profile details with the new resume data. Would you like to proceed?")) {
                setProfileExists(false);
                setActiveStep(1);
                triggerToast("Please upload a new resume file to replace details.");
              }
            }}
            className="w-full text-center py-2 text-[12px] font-bold text-primary bg-primary/5 hover:bg-primary/10 transition-colors border border-primary/20 rounded-lg"
          >
            Replace Resume File
          </button>
        </div>

        {/* Dynamically Generated AI Recommendations */}
        <div className="space-y-3">
          <h3 className="text-[11px] font-bold text-outline uppercase tracking-wider flex items-center gap-1">
            <Icon name="lightbulb" className="text-[15px] text-primary" /> AI Improvement Tips
          </h3>
          <ul className="space-y-3">
            {profileData.resume_data.skills.length < 5 && (
              <li className="flex gap-2.5 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
                <p className="text-[13px] text-on-surface-variant">
                  Add at least <span className="font-bold">5 skills</span> to double your matching prospects in search results.
                </p>
              </li>
            )}
            {!profileData.resume_data.contact_info.linkedin_url && (
              <li className="flex gap-2.5 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
                <p className="text-[13px] text-on-surface-variant">
                  Link your <span className="font-bold">LinkedIn URL</span> to build recruiter credibility.
                </p>
              </li>
            )}
            {profileData.resume_data.projects.length === 0 && (
              <li className="flex gap-2.5 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
                <p className="text-[13px] text-on-surface-variant">
                  Adding a <span className="font-bold">featured project</span> will showcase practical application of your tech stack.
                </p>
              </li>
            )}
            {strengthScore >= 80 && (
              <li className="flex gap-2.5 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
                <p className="text-[13px] text-on-surface-variant">
                  Profile is fully optimized! You can now generate <span className="font-bold">tailored resumes</span> on the resumes page.
                </p>
              </li>
            )}
          </ul>
        </div>
      </div>
    </aside>
  );
}
