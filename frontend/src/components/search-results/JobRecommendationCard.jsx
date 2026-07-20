import React, { useState } from 'react';
import Icon from '../common/Icon';

const PRIORITY_CONFIG = {
  High: { color: 'text-red-400', bg: 'bg-red-400/10 border-red-400/20', icon: 'priority_high' },
  Medium: { color: 'text-amber-400', bg: 'bg-amber-400/10 border-amber-400/20', icon: 'remove' },
  Low: { color: 'text-blue-400', bg: 'bg-blue-400/10 border-blue-400/20', icon: 'arrow_downward' },
};

const DECISION_CONFIG = {
  'Strong Apply': { color: 'text-green-400', bg: 'bg-green-400/10 border-green-400/30', icon: 'rocket_launch' },
  'Apply': { color: 'text-blue-400', bg: 'bg-blue-400/10 border-blue-400/30', icon: 'send' },
  'Stretch Apply': { color: 'text-amber-400', bg: 'bg-amber-400/10 border-amber-400/30', icon: 'trending_up' },
  'Not Recommended': { color: 'text-red-400', bg: 'bg-red-400/10 border-red-400/30', icon: 'block' },
};

export default function JobRecommendationCard({ job, index = 0 }) {
  const [expanded, setExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('strengths');

  const jobMeta = job.job || {};
  const match = job.match || {};
  const guidance = job.guidance || {};
  const actions = job.actions || {};
  const score = match.score || 0;

  const decisionKey = match.application_decision || 'Apply';
  const decisionCfg = DECISION_CONFIG[decisionKey] || DECISION_CONFIG['Apply'];

  return (
    <div
      className="relative bg-jp-bg-surface/80 backdrop-blur-md border border-jp-border hover:border-jp-accent/40 rounded-2xl transition-all duration-300 shadow-xl overflow-hidden group animate-fade-in-up hover:-translate-y-0.5 hover:shadow-2xl hover:shadow-jp-accent/5"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Hover glow */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-bl from-jp-accent/5 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

      {/* ── Header ── */}
      <div className="p-6 pb-0">
        <div className="flex items-start justify-between gap-4">
          <div className="flex gap-4 min-w-0 flex-1">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-jp-bg-raised to-jp-bg-surface border border-jp-border flex items-center justify-center shrink-0 shadow-inner group-hover:border-jp-accent/30 transition-colors duration-300">
              <Icon name="business" className="text-[24px] text-jp-text-muted group-hover:text-jp-accent transition-colors duration-300" />
            </div>
            <div className="min-w-0">
              <h3 className="text-[17px] font-bold text-jp-text-primary truncate">{jobMeta.title}</h3>
              <p className="text-[14px] text-jp-text-tertiary mt-1 flex items-center flex-wrap gap-2">
                <span className="font-medium text-jp-text-secondary">{jobMeta.company}</span>
                {jobMeta.location && (
                  <><span>•</span><span className="flex items-center gap-1"><Icon name="location_on" className="text-[14px]" />{jobMeta.location}</span></>
                )}
                {jobMeta.work_mode && (
                  <><span>•</span><span className="px-2 py-0.5 rounded bg-jp-bg-raised text-[11px] font-semibold text-jp-text-secondary border border-jp-border-subtle">{jobMeta.work_mode}</span></>
                )}
              </p>
            </div>
          </div>

          {/* Score Circle */}
          <div className="flex flex-col items-center shrink-0">
            <div className={`relative flex items-center justify-center w-14 h-14 rounded-full border ${match.score_badge?.replace('jp-badge-', 'border-') || 'border-jp-accent/30'}`}
                 style={{ background: `conic-gradient(var(--color-jp-accent) ${score * 3.6}deg, transparent 0deg)`, padding: '3px' }}>
              <div className="w-full h-full rounded-full bg-jp-bg-surface flex items-center justify-center">
                <span className={`text-[15px] font-bold ${match.score_color || 'text-jp-accent'}`}>{Math.round(score)}%</span>
              </div>
            </div>
            <span className="text-[10px] font-bold text-jp-text-muted mt-1.5 uppercase tracking-wider">Match</span>
          </div>
        </div>

        {/* Decision Badge + Overall Fit */}
        <div className="mt-4 flex items-start gap-3">
          <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[11px] font-bold uppercase tracking-wider shrink-0 ${decisionCfg.bg} ${decisionCfg.color}`}>
            <Icon name={decisionCfg.icon} className="text-[14px]" />
            {decisionKey}
          </div>
          {match.confidence && (
            <span className="text-[11px] font-semibold text-jp-text-tertiary px-2 py-1 rounded bg-jp-bg-raised border border-jp-border-subtle">
              {match.confidence} Confidence
            </span>
          )}
        </div>

        {/* Overall Fit */}
        <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-jp-accent/5 to-transparent border-l-2 border-jp-accent">
          <div className="flex items-start gap-2">
            <Icon name="auto_awesome" className="text-[18px] text-jp-accent mt-0.5 shrink-0" />
            <p className="text-[13px] text-jp-text-secondary leading-relaxed">{guidance.overall_fit || 'No AI analysis available.'}</p>
          </div>
        </div>
      </div>

      {/* ── Expandable Guidance Tabs ── */}
      {expanded && (
        <div className="px-6 pt-5 animate-fade-in-up">
          {/* Tab Buttons */}
          <div className="flex gap-1 mb-4 p-1 bg-jp-bg-raised rounded-xl border border-jp-border-subtle">
            {[
              { id: 'strengths', label: 'Strengths', icon: 'check_circle' },
              { id: 'gaps', label: 'Gaps', icon: 'error_outline' },
              { id: 'resume', label: 'Resume', icon: 'description' },
              { id: 'interview', label: 'Interview', icon: 'mic' },
              { id: 'actions', label: 'Actions', icon: 'flag' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-jp-accent/15 text-jp-accent border border-jp-accent/30 shadow-sm'
                    : 'text-jp-text-tertiary hover:text-jp-text-secondary'
                }`}
              >
                <Icon name={tab.icon} className="text-[14px]" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="min-h-[120px] animate-fade-in-up">
            {activeTab === 'strengths' && (
              <div className="space-y-2">
                {guidance.strengths?.length > 0 ? guidance.strengths.map((s, i) => (
                  <div key={i} className="flex items-start gap-2.5 p-3 rounded-lg bg-green-400/5 border border-green-400/10">
                    <Icon name="check_circle" className="text-[16px] text-green-400 mt-0.5 shrink-0" />
                    <span className="text-[13px] text-jp-text-secondary leading-relaxed">{s}</span>
                  </div>
                )) : <p className="text-[13px] text-jp-text-tertiary italic p-4 text-center">No strengths data available.</p>}
              </div>
            )}

            {activeTab === 'gaps' && (
              <div className="space-y-2">
                {guidance.skill_gaps?.length > 0 ? guidance.skill_gaps.map((g, i) => (
                  <div key={i} className="flex items-start gap-2.5 p-3 rounded-lg bg-orange-400/5 border border-orange-400/10">
                    <Icon name="error_outline" className="text-[16px] text-orange-400 mt-0.5 shrink-0" />
                    <span className="text-[13px] text-jp-text-secondary leading-relaxed">{g}</span>
                  </div>
                )) : <p className="text-[13px] text-green-400 italic p-4 text-center flex items-center justify-center gap-2"><Icon name="celebration" className="text-[16px]" /> No skill gaps found!</p>}
              </div>
            )}

            {activeTab === 'resume' && (
              <div className="space-y-2">
                <p className="text-[11px] font-bold text-jp-accent uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Icon name="tips_and_updates" className="text-[14px]" /> Highlight these on your resume
                </p>
                {guidance.resume_focus_areas?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {guidance.resume_focus_areas.map((area, i) => (
                      <span key={i} className="px-3 py-1.5 rounded-full bg-jp-accent/10 border border-jp-accent/20 text-[12px] font-medium text-jp-accent">
                        {area}
                      </span>
                    ))}
                  </div>
                ) : <p className="text-[13px] text-jp-text-tertiary italic p-4 text-center">No resume focus areas available.</p>}
              </div>
            )}

            {activeTab === 'interview' && (
              <div className="space-y-2">
                <p className="text-[11px] font-bold text-violet-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Icon name="school" className="text-[14px]" /> Prepare for questions on
                </p>
                {guidance.interview_focus_areas?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {guidance.interview_focus_areas.map((area, i) => (
                      <span key={i} className="px-3 py-1.5 rounded-full bg-violet-400/10 border border-violet-400/20 text-[12px] font-medium text-violet-300">
                        {area}
                      </span>
                    ))}
                  </div>
                ) : <p className="text-[13px] text-jp-text-tertiary italic p-4 text-center">No interview focus areas available.</p>}
              </div>
            )}

            {activeTab === 'actions' && (
              <div className="space-y-2">
                {guidance.next_steps?.length > 0 ? guidance.next_steps.map((step, i) => {
                  const priority = step.priority || 'Medium';
                  const cfg = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.Medium;
                  return (
                    <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border ${cfg.bg}`}>
                      <div className={`w-6 h-6 rounded-md flex items-center justify-center ${cfg.bg}`}>
                        <Icon name={cfg.icon} className={`text-[14px] ${cfg.color}`} />
                      </div>
                      <span className="text-[13px] text-jp-text-secondary flex-1">{step.action}</span>
                      <span className={`text-[10px] font-bold uppercase tracking-wider ${cfg.color}`}>{priority}</span>
                    </div>
                  );
                }) : <p className="text-[13px] text-jp-text-tertiary italic p-4 text-center">No action items available.</p>}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Action Bar ── */}
      <div className="p-6 pt-5">
        <div className="flex gap-2 pt-4 border-t border-jp-border-subtle/50 flex-wrap">
          {/* Apply Now */}
          <a
            href={jobMeta.apply_url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => !jobMeta.apply_url && e.preventDefault()}
            className={`flex-1 min-w-[120px] py-2.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 text-[13px] ${
              jobMeta.apply_url
                ? 'bg-jp-accent hover:bg-jp-accent-hover text-white shadow-lg shadow-jp-accent/20 hover:shadow-jp-accent/30'
                : 'bg-jp-bg-raised text-jp-text-tertiary cursor-not-allowed border border-jp-border-subtle'
            }`}
          >
            <Icon name="open_in_new" className="text-[16px]" />
            {jobMeta.apply_url ? 'Apply Now' : 'No URL'}
          </a>

          {/* Tailor Resume */}
          {actions.can_tailor_resume && (
            <button className="px-4 py-2.5 rounded-xl bg-jp-bg-raised hover:bg-jp-accent/10 border border-jp-border-subtle hover:border-jp-accent/30 text-jp-text-secondary hover:text-jp-accent transition-all flex items-center gap-2 text-[13px] font-semibold">
              <Icon name="description" className="text-[16px]" />
              Tailor Resume
            </button>
          )}

          {/* Interview Prep */}
          {actions.can_prepare_interview && (
            <button className="px-4 py-2.5 rounded-xl bg-jp-bg-raised hover:bg-violet-400/10 border border-jp-border-subtle hover:border-violet-400/30 text-jp-text-secondary hover:text-violet-400 transition-all flex items-center gap-2 text-[13px] font-semibold">
              <Icon name="mic" className="text-[16px]" />
              Interview Prep
            </button>
          )}

          {/* Company Research — Coming Soon */}
          <button
            className="px-4 py-2.5 rounded-xl bg-jp-bg-raised border border-jp-border-subtle text-jp-text-muted transition-all flex items-center gap-2 text-[13px] font-semibold cursor-not-allowed opacity-60 relative group/tooltip"
            disabled
          >
            <Icon name="corporate_fare" className="text-[16px]" />
            Company Intel
            <span className="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded bg-jp-bg-raised border border-jp-border text-[10px] text-jp-text-tertiary whitespace-nowrap opacity-0 group-hover/tooltip:opacity-100 transition-opacity pointer-events-none shadow-lg">
              Coming Soon
            </span>
          </button>

          {/* View Details Toggle */}
          <button
            className="px-4 py-2.5 bg-jp-bg-raised hover:bg-jp-border text-jp-text-primary rounded-xl font-semibold transition-all border border-jp-border-subtle flex items-center gap-2 text-[13px]"
            onClick={() => setExpanded(!expanded)}
          >
            <Icon name={expanded ? 'expand_less' : 'expand_more'} className="text-[18px]" />
            {expanded ? 'Collapse' : 'View Details'}
          </button>
        </div>
      </div>
    </div>
  );
}
