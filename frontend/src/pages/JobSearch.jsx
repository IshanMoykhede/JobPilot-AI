import React, { useState } from "react";
import { Link } from "react-router-dom";
import AppShell from "../components/layout/AppShell";
import Icon from "../components/common/Icon";
import SkillTag from "../components/common/SkillTag";
import CircularProgress from "../components/common/CircularProgress";

function JobCard({ title, company, location, workMode, matchPercentage, recommended, matchingSkills = [], missingSkills = [], insightText, onGenerateResume, onViewDetails }) {
  return (
    <div className="jp-card p-5 space-y-4 hover:border-jp-accent/30 transition-all">
      {recommended && (
        <div className="flex justify-end -mt-1 -mr-1">
          <span className="jp-badge jp-badge-accent">
            <Icon name="workspace_premium" className="text-[12px]" />
            #{recommended.rank} Recommended
          </span>
        </div>
      )}

      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-lg bg-jp-bg-raised border border-jp-border flex items-center justify-center shrink-0">
          <Icon name="business" className="text-[20px] text-jp-text-muted" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-[15px] font-semibold text-jp-text-primary">{title}</h3>
          <p className="text-[13px] text-jp-text-tertiary mt-0.5">
            {company} · {location}{workMode ? ` · ${workMode}` : ""}
          </p>
        </div>
        <CircularProgress percentage={matchPercentage} size={48} strokeWidth={4} />
      </div>

      {matchingSkills.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-jp-text-muted uppercase tracking-wider mb-2">Matching Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {matchingSkills.map(s => <SkillTag key={s} label={s} variant="success" />)}
          </div>
        </div>
      )}

      {missingSkills.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-jp-text-muted uppercase tracking-wider mb-2">Gaps</p>
          <div className="flex flex-wrap gap-1.5">
            {missingSkills.map(s => <SkillTag key={s} label={s} variant="warning" />)}
          </div>
        </div>
      )}

      {insightText && (
        <div className="flex gap-2.5 p-3 rounded-lg bg-jp-accent-muted/50 border border-jp-accent/10">
          <Icon name="lightbulb" fill className="text-[16px] text-jp-accent shrink-0 mt-0.5" />
          <p className="text-[12px] text-jp-text-secondary leading-relaxed">{insightText}</p>
        </div>
      )}

      <div className="flex gap-2 pt-1">
        <button className="jp-btn jp-btn-primary jp-btn-sm" onClick={onGenerateResume}>
          <Icon name="bolt" className="text-[16px]" />
          Generate Resume
        </button>
        <Link to="/job-detail" className="jp-btn jp-btn-secondary jp-btn-sm no-underline">
          View Details
        </Link>
      </div>
    </div>
  );
}

function InsightCard({ icon, title, children, variant }) {
  return (
    <div className={`jp-card p-4 ${variant === 'highlight' ? 'border-jp-accent/30 bg-jp-accent-muted/30' : ''}`}>
      <h4 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
        {icon && <Icon name={icon} className="text-[14px] text-jp-accent" />}
        {title}
      </h4>
      {children}
    </div>
  );
}

function SkillBar({ label, percentage }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[12px]">
        <span className="text-jp-text-secondary font-medium">{label}</span>
        <span className="text-jp-text-muted">{percentage}%</span>
      </div>
      <div className="h-1.5 bg-jp-bg-raised rounded-full overflow-hidden">
        <div className="h-full bg-jp-accent rounded-full transition-all" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}

export default function JobSearch() {
  const [refineQuery, setRefineQuery] = useState("");

  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "Search Results" },
    ]}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
        {/* Summary */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold text-jp-text-primary">DevOps Engineer Jobs in Pune</h1>
            <div className="flex items-center gap-4 mt-1">
              <span className="text-[13px] text-jp-text-tertiary">127 jobs found</span>
              <span className="text-[13px] text-jp-text-tertiary">10 top matches</span>
              <span className="text-[13px] text-jp-text-tertiary">Avg match: 78%</span>
            </div>
          </div>
          <button className="jp-btn jp-btn-secondary jp-btn-sm">
            <Icon name="share" className="text-[16px]" />
            Share
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { label: "Location", options: ["Pune", "Remote", "Bengaluru"] },
            { label: "Experience", options: ["0-2 years", "3-5 years", "5+ years"] },
            { label: "Work Mode", options: ["Remote", "Hybrid", "On-site"] },
            { label: "Min Match", options: ["70%+", "80%+", "90%+"] },
          ].map(filter => (
            <select key={filter.label} className="jp-select text-[12px]">
              <option>{filter.label}</option>
              {filter.options.map(opt => <option key={opt}>{opt}</option>)}
            </select>
          ))}
          <div className="ml-auto">
            <select className="jp-select text-[12px]">
              <option>Sort: Highest Match</option>
              <option>Sort: Most Recent</option>
              <option>Sort: Salary Range</option>
            </select>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Job Listings */}
          <div className="lg:col-span-8 space-y-4">
            <JobCard
              title="Senior DevOps Architect"
              company="CloudStream Solutions"
              location="Pune"
              workMode="Hybrid"
              matchPercentage={94}
              recommended={{ rank: 1 }}
              matchingSkills={["AWS (Expert)", "Docker", "Kubernetes"]}
              missingSkills={["Terraform", "ArgoCD"]}
              insightText={<>Your experience with EKS perfectly aligns with their stack. Mentioning your <strong>multi-cluster management</strong> could secure an interview.</>}
              onGenerateResume={() => alert("Generating tailored resume for Senior DevOps Architect...")}
            />
            <JobCard
              title="Cloud Infrastructure Engineer"
              company="Nexus Systems"
              location="Pune"
              workMode="On-site"
              matchPercentage={82}
              matchingSkills={["Linux", "Terraform"]}
              missingSkills={["Jenkins CI"]}
              insightText="You meet 8 out of 10 primary requirements. They focus heavily on Infrastructure as Code."
              onGenerateResume={() => alert("Generating tailored resume for Cloud Infrastructure Engineer...")}
            />
            <JobCard
              title="Platform Engineer (SRE)"
              company="Velocity AI"
              location="Pune"
              workMode="Remote"
              matchPercentage={76}
              matchingSkills={["Prometheus", "Go"]}
              missingSkills={["Service Mesh"]}
              onGenerateResume={() => alert("Generating tailored resume for Platform Engineer...")}
            />
          </div>

          {/* Insights Sidebar */}
          <aside className="lg:col-span-4 space-y-4">
            <h3 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider flex items-center gap-1.5 px-1">
              <Icon name="auto_awesome" fill className="text-[14px] text-jp-accent" />
              AI Search Insights
            </h3>

            <InsightCard icon="insights" title="Most Demanded Skills">
              <div className="space-y-2.5">
                <SkillBar label="AWS" percentage={80} />
                <SkillBar label="Docker" percentage={65} />
                <SkillBar label="Linux" percentage={55} />
              </div>
            </InsightCard>

            <InsightCard title="Skills to Learn" variant="alert">
              <div className="flex flex-wrap gap-1.5 mb-2">
                {["Terraform", "Jenkins", "CI/CD"].map(s => (
                  <SkillTag key={s} label={`↗ ${s}`} variant="accent" />
                ))}
              </div>
              <p className="text-[11px] text-jp-text-muted">Appear in 60%+ of your search results.</p>
            </InsightCard>

            <InsightCard icon="analytics" title="Market Intelligence">
              <ul className="space-y-2 text-[12px] text-jp-text-secondary leading-relaxed">
                <li className="flex gap-2"><span className="text-jp-accent shrink-0">•</span><span><strong>72%</strong> of matching jobs require AWS Certification.</span></li>
                <li className="flex gap-2"><span className="text-jp-accent shrink-0">•</span><span>Salary range for your profile is <strong>15% higher</strong> than average.</span></li>
              </ul>
            </InsightCard>

            <InsightCard icon="check_circle" title="Profile Optimization" variant="highlight">
              <p className="text-[12px] text-jp-text-secondary leading-relaxed mb-3">
                Add <strong>deployment metrics</strong> to your resume to increase match score with Top 3 employers.
              </p>
              <button className="jp-btn jp-btn-primary w-full jp-btn-sm">Apply Recommendations</button>
            </InsightCard>

            <div className="jp-card p-4 space-y-2">
              <h4 className="text-[10px] font-semibold text-jp-text-muted uppercase tracking-wider">Suggested Follow-ups</h4>
              {["Show only remote roles?", "What's the salary range?", "Learn Terraform fast?", "Best company culture?"].map(text => (
                <button
                  key={text}
                  className="w-full text-left px-3 py-2 rounded-lg text-[12px] font-medium text-jp-text-secondary bg-jp-bg-raised border border-jp-border-subtle hover:border-jp-accent/20 hover:text-jp-text-primary transition-all"
                  onClick={() => alert(`Asking AI: "${text}"`)}
                >
                  {text}
                </button>
              ))}
            </div>
          </aside>
        </div>

        {/* Sticky AI Refine Bar */}
        <div className="sticky bottom-4 max-w-xl mx-auto w-full">
          <div className="bg-jp-bg-surface/90 backdrop-blur-xl border border-jp-border rounded-full pl-4 pr-1.5 py-1.5 flex items-center gap-2 shadow-lg">
            <Icon name="auto_awesome" className="text-[18px] text-jp-accent shrink-0" />
            <input
              type="text"
              placeholder="Ask AI to refine your search..."
              className="flex-1 bg-transparent border-none outline-none text-[13px] text-jp-text-primary placeholder:text-jp-text-muted"
              value={refineQuery}
              onChange={(e) => setRefineQuery(e.target.value)}
            />
            <button className="w-8 h-8 rounded-full bg-jp-accent text-white flex items-center justify-center shrink-0 hover:bg-jp-accent-hover transition-colors">
              <Icon name="arrow_upward" className="text-[16px]" />
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}