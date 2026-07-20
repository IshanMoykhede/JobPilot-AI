import React, { useState } from "react";
import Icon from "../common/Icon";
import SkillTag from "../common/SkillTag";
import CircularProgress from "../common/CircularProgress";
import { Card } from "../ui/Card";
import Button from "../ui/Button";

export default function JobCard({ job, onGenerateResume }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const score = Math.round(job.final_score || 0);
  const isHighlyRecommended = job.rank <= 3;

  return (
    <Card className="flex flex-col bg-jp-bg-surface/60 border-jp-border-subtle hover:border-jp-accent/50 hover:shadow-[0_8px_32px_rgba(99,102,241,0.15)] transition-all relative overflow-hidden group">
      
      {/* ── Top Match Badge ── */}
      {isHighlyRecommended && (
        <div className="absolute top-0 right-10 z-10 hidden md:block">
          <div className="bg-gradient-to-b from-jp-accent to-jp-accent-strong text-white text-[10px] font-bold px-3 py-1 rounded-b-lg shadow-md tracking-wide uppercase flex items-center gap-1">
            <Icon name="workspace_premium" className="text-[12px]" />
            #{job.rank} Match
          </div>
        </div>
      )}

      {/* ── Main Row ── */}
      <div className="p-5 flex flex-col md:flex-row gap-5">
        
        {/* Left: Company Icon */}
        <div className="hidden md:flex w-14 h-14 rounded-2xl bg-gradient-to-br from-jp-bg-raised to-jp-bg-inset border border-jp-border items-center justify-center shrink-0 shadow-sm relative overflow-hidden group-hover:border-jp-accent/30 transition-colors">
          <Icon name="business" className="text-[28px] text-jp-text-muted group-hover:text-jp-accent transition-colors" />
        </div>

        {/* Center: Info */}
        <div className="flex-1 min-w-0 flex flex-col justify-center">
          <div className="flex items-center gap-3">
            <h3 className="text-[18px] font-bold text-jp-text-primary group-hover:text-jp-accent-text transition-colors truncate">
              {job.title}
            </h3>
            {isHighlyRecommended && (
              <span className="md:hidden shrink-0 bg-jp-accent text-white text-[9px] font-bold px-2 py-0.5 rounded shadow-sm tracking-wide uppercase flex items-center gap-1">
                <Icon name="workspace_premium" className="text-[10px]" />
                #{job.rank}
              </span>
            )}
          </div>
          
          <div className="flex items-center flex-wrap gap-x-2 gap-y-1 mt-1.5 text-[13px] text-jp-text-secondary">
            <span className="font-semibold text-jp-text-primary">{job.company}</span>
            <span className="w-1 h-1 rounded-full bg-jp-border-active"></span>
            <span>{job.location}</span>
            
            {job.work_mode && job.work_mode !== "Unknown" && (
              <>
                <span className="w-1 h-1 rounded-full bg-jp-border-active"></span>
                <span className="text-jp-accent-text/80">{job.work_mode}</span>
              </>
            )}
            
            {job.employment_type && (
              <>
                <span className="w-1 h-1 rounded-full bg-jp-border-active"></span>
                <span>{job.employment_type}</span>
              </>
            )}
            
            {job.salary_information && (
              <>
                <span className="w-1 h-1 rounded-full bg-jp-border-active"></span>
                <span className="text-jp-success-text/80 font-medium">{job.salary_information}</span>
              </>
            )}
          </div>

          {/* Inline Matching Skills (Always visible) */}
          {job.matching_skills && job.matching_skills.length > 0 && (
            <div className="flex items-center gap-1.5 mt-3 flex-wrap">
              <Icon name="check_circle" className="text-[14px] text-jp-success mr-1 shrink-0" />
              {job.matching_skills.slice(0, 5).map(s => (
                <span key={s} className="px-2 py-0.5 rounded text-[11px] font-medium bg-jp-success-muted/30 text-jp-success-text border border-transparent whitespace-nowrap">
                  {s}
                </span>
              ))}
              {job.matching_skills.length > 5 && (
                <span className="text-[11px] text-jp-text-tertiary ml-1 font-medium whitespace-nowrap">+{job.matching_skills.length - 5} more</span>
              )}
            </div>
          )}
        </div>

        {/* Right: Actions & Score */}
        <div className="flex flex-row md:flex-col items-center justify-between md:justify-center gap-4 shrink-0 md:pl-6 md:border-l border-jp-border-subtle mt-2 md:mt-0">
          
          {/* Score */}
          <div className="flex items-center gap-3 md:flex-col md:gap-1">
            <CircularProgress percentage={score} size={44} strokeWidth={4} />
            <span className="hidden md:block text-[10px] font-bold text-jp-text-muted uppercase tracking-widest">Score</span>
            <span className="md:hidden text-[14px] font-bold text-jp-text-primary">{score}%</span>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap md:flex-col items-center md:items-end justify-center md:justify-center gap-2 mt-3 md:mt-0 w-full md:w-auto">
            
            {/* Apply Now */}
            <a href={job.apply_url || "#"} target="_blank" rel="noopener noreferrer" className={`w-full md:w-auto ${!job.apply_url ? "pointer-events-none opacity-50" : ""}`}>
              <Button variant="outline" size="sm" className="w-full h-9 px-4 text-jp-text-secondary hover:text-jp-text-primary border-jp-border-subtle bg-jp-bg-surface hover:bg-jp-bg-raised whitespace-nowrap">
                <Icon name="open_in_new" className="text-[16px] mr-1.5" />
                {job.apply_url ? "Apply Now" : "Apply (Not Found)"}
              </Button>
            </a>
            
            {/* Interview Agent */}
            <Button variant="outline" size="sm" className="w-full md:w-auto h-9 px-4 text-jp-accent-text border-jp-accent/30 hover:border-jp-accent/60 bg-jp-accent/5 hover:bg-jp-accent/10 whitespace-nowrap transition-colors">
              <Icon name="psychology" className="text-[16px] mr-1.5" />
              Interview Agent
            </Button>

            {/* Tailor Resume */}
            <Button variant="primary" size="sm" onClick={onGenerateResume} className="w-full md:w-auto h-9 px-5 shadow-[0_0_12px_var(--color-jp-accent-glow)] whitespace-nowrap">
              <Icon name="bolt" className="text-[16px] mr-1.5" />
              Tailor Resume
            </Button>
            
          </div>

        </div>
      </div>

      {/* ── Expand Toggle ── */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-5 py-2.5 bg-jp-bg-raised/30 border-t border-jp-border-subtle flex items-center justify-center cursor-pointer hover:bg-jp-bg-raised/50 transition-colors group/expand"
      >
        <span className="text-[11px] font-bold text-jp-text-tertiary group-hover/expand:text-jp-accent uppercase tracking-widest flex items-center gap-1.5 transition-colors">
          {isExpanded ? "Hide Details" : "View Details & AI Insights"}
          <Icon name={isExpanded ? "expand_less" : "expand_more"} className="text-[16px]" />
        </span>
      </div>

      {/* ── Expanded Content ── */}
      {isExpanded && (
        <div className="p-5 border-t border-jp-border-subtle bg-jp-bg-app/40 space-y-6">
          
          {/* Insight Callout */}
          {job.insight_text && (
            <div className="flex gap-3 p-4 rounded-xl bg-gradient-to-r from-jp-accent-muted/40 to-transparent border border-jp-accent/20 relative overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-jp-accent rounded-l-xl"></div>
              <Icon name="lightbulb" fill className="text-[20px] text-jp-accent shrink-0 mt-0.5" />
              <p className="text-[13px] text-jp-text-secondary leading-relaxed font-medium">
                {job.insight_text}
              </p>
            </div>
          )}

          {/* Skill Gaps */}
          {job.missing_skills && job.missing_skills.length > 0 && (
            <div className="space-y-2">
              <p className="text-[12px] font-semibold text-jp-text-primary uppercase tracking-widest flex items-center gap-1.5">
                <Icon name="warning" className="text-[16px] text-jp-warning" />
                Missing Skills
              </p>
              <div className="flex flex-wrap gap-1.5">
                {job.missing_skills.map(s => (
                  <SkillTag key={s} label={s} variant="warning" className="bg-jp-warning-muted/30 border-transparent text-jp-warning-text py-1 px-3 text-[11px]" />
                ))}
              </div>
            </div>
          )}

          {/* Raw Description */}
          {job.original_description && (
            <div className="space-y-2">
              <p className="text-[12px] font-semibold text-jp-text-primary uppercase tracking-widest flex items-center gap-1.5">
                <Icon name="description" className="text-[16px] text-jp-text-muted" />
                Original Description
              </p>
              <div className="p-4 rounded-xl bg-jp-bg-surface border border-jp-border-subtle overflow-y-auto max-h-[300px] text-[13px] text-jp-text-secondary whitespace-pre-wrap leading-relaxed shadow-inner">
                {job.original_description}
              </div>
            </div>
          )}

        </div>
      )}

    </Card>
  );
}
