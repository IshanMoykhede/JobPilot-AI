import React from 'react';
import { Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';
import CircularProgress from '../components/common/CircularProgress';
import SkillTag from '../components/common/SkillTag';

function JobDetail() {
  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "Search Results", href: "/search" },
      { label: "Job Detail" },
    ]}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">

        {/* ── Job Header ──────────────────────────────────── */}
        <section className="jp-card p-6 flex flex-col md:flex-row md:items-center gap-5">
          <div className="w-14 h-14 rounded-xl bg-jp-bg-raised border border-jp-border flex items-center justify-center shrink-0">
            <Icon name="business" className="text-[28px] text-jp-text-muted" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-semibold text-jp-text-primary tracking-tight">Senior DevOps Architect</h1>
            <div className="flex flex-wrap items-center gap-3 mt-1.5 text-[13px] text-jp-text-tertiary">
              <span className="flex items-center gap-1"><Icon name="business" className="text-[16px]" /> CloudStream Solutions</span>
              <span className="flex items-center gap-1"><Icon name="location_on" className="text-[16px]" /> Pune, Hybrid</span>
              <span className="jp-badge jp-badge-accent">Full-time</span>
            </div>
          </div>
          <div className="flex items-center gap-5 shrink-0">
            <CircularProgress percentage={89} size={56} strokeWidth={4} label="Match" />
            <div className="flex flex-col gap-2">
              <button className="jp-btn jp-btn-primary">
                <Icon name="bolt" className="text-[16px]" />
                Generate Resume
              </button>
              <button className="jp-btn jp-btn-secondary">
                Apply Now
              </button>
            </div>
          </div>
        </section>

        {/* ── Three Column Layout ─────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Column 1: Job Requirements */}
          <div className="lg:col-span-4">
            <div className="jp-card flex flex-col overflow-hidden">
              <div className="px-5 py-3 border-b border-jp-border-subtle">
                <h3 className="text-[11px] font-semibold text-jp-accent uppercase tracking-wider">Job Requirements</h3>
              </div>
              <div className="p-5 space-y-6 overflow-y-auto max-h-[600px]">
                <div>
                  <h4 className="text-[14px] font-semibold text-jp-text-primary mb-3">Responsibilities</h4>
                  <ul className="space-y-2 text-[13px] text-jp-text-secondary list-disc pl-4 leading-relaxed">
                    <li>Architect and maintain highly scalable, fault-tolerant infrastructure on AWS.</li>
                    <li>Automate CI/CD pipelines for complex microservices using Jenkins and GitHub Actions.</li>
                    <li>Design container orchestration strategies with Docker and Kubernetes (EKS).</li>
                    <li>Lead security hardening initiatives and compliance audits.</li>
                    <li>Collaborate with dev teams to optimize application performance.</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-[14px] font-semibold text-jp-text-primary mb-3">Qualifications</h4>
                  <ul className="space-y-2 text-[13px] text-jp-text-secondary list-disc pl-4 leading-relaxed">
                    <li>8+ years of experience in DevOps or Infrastructure Engineering.</li>
                    <li>Deep expertise in Terraform and Infrastructure as Code.</li>
                    <li>Strong background in Linux administration and Shell scripting.</li>
                    <li>AWS Solutions Architect Professional preferred.</li>
                  </ul>
                </div>
                <div className="pt-4 border-t border-jp-border-subtle">
                  <h4 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-3">Key Skills</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {["AWS", "Terraform", "Docker", "CI/CD", "Kubernetes", "Python"].map(skill => (
                      <SkillTag key={skill} label={skill} variant="accent" />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Column 2: AI Analysis */}
          <div className="lg:col-span-4 space-y-4">
            <div className="jp-card p-5 space-y-5">
              <div className="flex items-center justify-between">
                <h3 className="text-[11px] font-semibold text-jp-accent uppercase tracking-wider">AI Match Analysis</h3>
                <span className="jp-badge jp-badge-success">High Confidence</span>
              </div>

              {/* Readiness Bar */}
              <div className="p-4 rounded-lg bg-jp-bg-raised border border-jp-border-subtle">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[13px] font-medium text-jp-text-primary">Application Readiness</span>
                  <span className="text-[13px] font-semibold text-jp-accent">82%</span>
                </div>
                <div className="h-1.5 bg-jp-bg-app rounded-full overflow-hidden">
                  <div className="h-full bg-jp-accent rounded-full" style={{ width: "82%" }} />
                </div>
              </div>

              {/* Analysis Cards */}
              <div className="space-y-3">
                <div className="p-3 rounded-lg border-l-[3px] border-l-jp-accent bg-jp-accent-muted/20 border border-jp-border-subtle border-l-0">
                  <div className="flex gap-2.5">
                    <Icon name="auto_awesome" fill className="text-[18px] text-jp-accent shrink-0 mt-0.5" />
                    <div>
                      <p className="text-[13px] font-semibold text-jp-text-primary">Why This Job Matches</p>
                      <p className="text-[12px] text-jp-text-secondary mt-1 leading-relaxed">Your 5 years of AWS experience directly aligns with their architectural needs. Your Kubernetes background exceeds their base requirements.</p>
                    </div>
                  </div>
                </div>
                <div className="p-3 rounded-lg border-l-[3px] border-l-jp-error bg-jp-error-muted/30 border border-jp-border-subtle border-l-0">
                  <div className="flex gap-2.5">
                    <Icon name="warning" fill className="text-[18px] text-jp-error shrink-0 mt-0.5" />
                    <div>
                      <p className="text-[13px] font-semibold text-jp-text-primary">Missing Skills</p>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        <SkillTag label="Terraform" variant="error" />
                        <SkillTag label="Jenkins" variant="error" />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 rounded-lg border-l-[3px] border-l-jp-warning bg-jp-warning-muted/30 border border-jp-border-subtle border-l-0">
                  <div className="flex gap-2.5">
                    <Icon name="lightbulb" fill className="text-[18px] text-jp-warning shrink-0 mt-0.5" />
                    <div>
                      <p className="text-[13px] font-semibold text-jp-text-primary">Improvement Tip</p>
                      <p className="text-[12px] text-jp-text-secondary mt-1 italic leading-relaxed">"Add specific deployment metrics (e.g., 'reduced downtime by 30%') to boost your score."</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Modifications */}
            <div className="jp-card p-5">
              <h3 className="text-[11px] font-semibold text-jp-accent uppercase tracking-wider mb-4">AI Resume Modifications</h3>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-jp-error-muted/20 border border-jp-error/10">
                  <span className="text-[9px] font-bold text-jp-error uppercase tracking-wider">Before</span>
                  <p className="text-[12px] text-jp-text-secondary mt-1 leading-relaxed">Worked on Docker containers for various internal projects.</p>
                </div>
                <div className="p-3 rounded-lg bg-jp-success-muted/30 border border-jp-success/10">
                  <span className="text-[9px] font-bold text-jp-success uppercase tracking-wider">After</span>
                  <p className="text-[12px] text-jp-text-primary mt-1 font-medium leading-relaxed">Implemented Docker containerization for scalable microservices, improving deployment speed by 40%.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Column 3: Resume Generator + Checklist */}
          <div className="lg:col-span-4 space-y-4">
            <div className="jp-card flex flex-col overflow-hidden">
              <div className="px-5 py-3 border-b border-jp-border-subtle flex items-center justify-between">
                <h3 className="text-[11px] font-semibold text-jp-accent uppercase tracking-wider">Tailored Resume</h3>
                <button className="jp-btn-icon jp-btn-ghost jp-btn-sm">
                  <Icon name="fullscreen" className="text-[18px] text-jp-text-muted" />
                </button>
              </div>

              {/* Resume Preview */}
              <div className="bg-jp-bg-inset p-4 min-h-[280px] relative group">
                <div className="h-full bg-white rounded shadow-md p-5 overflow-hidden">
                  <div className="w-full h-3 bg-jp-accent/10 rounded mb-3" />
                  <div className="w-2/3 h-3 bg-jp-accent/10 rounded mb-5" />
                  <div className="space-y-2">
                    <div className="h-2 w-full bg-gray-100 rounded" />
                    <div className="h-2 w-5/6 bg-gray-100 rounded" />
                    <div className="h-2 w-full bg-gray-100 rounded" />
                    <div className="h-2 w-4/6 bg-gray-100 rounded" />
                  </div>
                  <div className="mt-5 pt-5 border-t border-gray-100">
                    <div className="h-3 w-1/4 bg-jp-accent/10 rounded mb-3" />
                    <div className="h-2 w-full bg-gray-100 rounded mb-1.5" />
                    <div className="h-2 w-full bg-gray-100 rounded mb-1.5" />
                    <div className="h-2 w-2/3 bg-gray-100 rounded" />
                  </div>
                </div>
                <div className="absolute inset-0 bg-jp-bg-app/60 backdrop-blur-[1px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="jp-btn jp-btn-primary jp-btn-sm shadow-lg">
                    <Icon name="edit" className="text-[16px]" />
                    Edit Resume
                  </button>
                </div>
              </div>

              {/* Controls */}
              <div className="p-5 space-y-4 border-t border-jp-border-subtle">
                <div>
                  <label className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-1.5 block">Resume Focus</label>
                  <select className="jp-select w-full">
                    <option>Balanced (Recommended)</option>
                    <option>Skills-Heavy</option>
                    <option>Projects-Focused</option>
                    <option>Leadership & Strategy</option>
                  </select>
                </div>
                <button className="jp-btn jp-btn-primary w-full">
                  <Icon name="bolt" className="text-[18px]" />
                  Generate Tailored Resume
                </button>
                <p className="text-[11px] text-center text-jp-text-muted">Takes ~15 seconds to rebuild with AI</p>
              </div>
            </div>

            {/* Application Checklist */}
            <div className="jp-card overflow-hidden">
              <div className="bg-jp-accent px-5 py-3 flex items-center justify-between">
                <span className="text-white font-semibold text-[13px] flex items-center gap-1.5">
                  <Icon name="checklist" className="text-[18px]" />
                  Application Checklist
                </span>
                <span className="bg-white/20 text-white px-2 py-0.5 rounded text-[10px] font-bold">3/5</span>
              </div>
              <div className="p-5 space-y-3">
                {[
                  { label: "Resume Uploaded", done: true },
                  { label: "Job Selected", done: true },
                  { label: "Match Score Generated", done: true },
                  { label: "Resume Tailored", done: false },
                  { label: "Apply on Portal", done: false },
                ].map((item, idx) => (
                  <label key={idx} className="flex items-center gap-3 cursor-pointer group">
                    <div className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${item.done ? 'bg-jp-accent border-jp-accent' : 'border-jp-border-active bg-transparent'}`}>
                      {item.done && <Icon name="check" className="text-[12px] text-white" />}
                    </div>
                    <span className={`text-[13px] ${item.done ? 'text-jp-text-secondary line-through' : 'text-jp-text-primary'} group-hover:text-jp-text-primary transition-colors`}>
                      {item.label}
                    </span>
                  </label>
                ))}
              </div>
              <div className="px-5 pb-5">
                <button className="jp-btn jp-btn-secondary w-full jp-btn-sm">View Next Steps</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default JobDetail;