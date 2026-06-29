import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AppShell from "../components/layout/AppShell";
import Icon from "../components/common/Icon";
import CircularProgress from "../components/common/CircularProgress";
import SkillTag from "../components/common/SkillTag";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const firstName = user?.name?.split(" ")[0] || "there";
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <AppShell breadcrumbs={[{ label: "Dashboard" }]}>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-8">

        {/* ── Welcome + Search ─────────────────────────────── */}
        <section className="space-y-5">
          <div>
            <h1 className="text-2xl font-semibold text-jp-text-primary tracking-tight">
              Welcome back, {firstName}
            </h1>
            <p className="text-[14px] text-jp-text-tertiary mt-1">
              Search jobs and generate tailored resumes with AI.
            </p>
          </div>

          {/* AI Search Bar */}
          <form onSubmit={handleSearch} className="jp-card p-1.5 flex items-center gap-2">
            <div className="relative flex-1">
              <Icon name="auto_awesome" className="absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-jp-accent" />
              <input
                type="text"
                placeholder="Try: DevOps Engineer in Pune, Frontend Developer Remote..."
                className="w-full pl-10 pr-4 py-3 bg-transparent border-none text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button type="submit" className="jp-btn jp-btn-primary shrink-0">
              <Icon name="search" className="text-[18px]" />
              Search Jobs
            </button>
          </form>

          {/* Quick suggestions */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[12px] text-jp-text-muted font-medium">Popular:</span>
            {["DevOps Engineer", "Frontend Developer", "Cloud Architect", "SRE Manager"].map(tag => (
              <button
                key={tag}
                onClick={() => { setSearchQuery(tag); }}
                className="px-3 py-1 text-[12px] font-medium rounded-full border border-jp-border bg-jp-bg-surface text-jp-accent-text hover:bg-jp-bg-raised hover:border-jp-border-active transition-colors"
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        {/* ── Stats Row ────────────────────────────────────── */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: "description", label: "Resumes Generated", value: "12", color: "text-jp-accent" },
            { icon: "search", label: "Jobs Searched", value: "48", color: "text-jp-success" },
            { icon: "analytics", label: "Avg Match Score", value: "84%", color: "text-jp-warning" },
            { icon: "trending_up", label: "Profile Strength", value: "85%", color: "text-jp-accent" },
          ].map(stat => (
            <div key={stat.label} className="jp-card p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-jp-bg-raised flex items-center justify-center shrink-0">
                <Icon name={stat.icon} className={`text-[20px] ${stat.color}`} />
              </div>
              <div>
                <p className="text-[20px] font-semibold text-jp-text-primary leading-tight">{stat.value}</p>
                <p className="text-[12px] text-jp-text-tertiary">{stat.label}</p>
              </div>
            </div>
          ))}
        </section>

        {/* ── Two Column Layout ────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left: Activity */}
          <div className="lg:col-span-2 space-y-6">

            {/* Recent Resumes */}
            <section className="jp-card overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-jp-border-subtle">
                <h2 className="text-[14px] font-semibold text-jp-text-primary">Recent Resumes</h2>
                <Link to="/resumes" className="text-[12px] font-medium text-jp-accent hover:text-jp-accent-hover transition-colors no-underline">
                  View All →
                </Link>
              </div>
              <div className="divide-y divide-jp-border-subtle">
                {[
                  { title: "DevOps @ Infosys", time: "2h ago", match: 89, icon: "terminal" },
                  { title: "SRE Engineer @ Google", time: "Yesterday", match: 94, icon: "dns" },
                  { title: "Cloud Architect @ AWS", time: "3 days ago", match: 78, icon: "cloud" },
                ].map(item => (
                  <div key={item.title} className="flex items-center gap-3 p-4 hover:bg-jp-bg-raised/50 transition-colors cursor-pointer">
                    <div className="w-9 h-9 rounded-lg bg-jp-bg-raised flex items-center justify-center shrink-0">
                      <Icon name={item.icon} className="text-[18px] text-jp-text-tertiary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-jp-text-primary truncate">{item.title}</p>
                      <p className="text-[12px] text-jp-text-muted">{item.time}</p>
                    </div>
                    <CircularProgress percentage={item.match} size={36} strokeWidth={3} />
                    <button className="jp-btn-icon jp-btn-ghost jp-btn-sm opacity-0 group-hover:opacity-100">
                      <Icon name="download" className="text-[18px] text-jp-text-tertiary" />
                    </button>
                  </div>
                ))}
              </div>
            </section>

            {/* Search History */}
            <section className="jp-card overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-jp-border-subtle">
                <h2 className="text-[14px] font-semibold text-jp-text-primary">Recent Searches</h2>
                <button className="text-[12px] font-medium text-jp-text-muted hover:text-jp-text-secondary transition-colors">
                  Clear
                </button>
              </div>
              <div className="divide-y divide-jp-border-subtle">
                {[
                  { query: "Cloud Engineer in Bangalore", results: "12 results", time: "2d ago" },
                  { query: "Remote Kubernetes Architect", results: "45 results", time: "4d ago" },
                  { query: "Senior Frontend in Pune", results: "28 results", time: "1w ago" },
                ].map(item => (
                  <div key={item.query} className="flex items-center gap-3 p-4 hover:bg-jp-bg-raised/50 transition-colors cursor-pointer">
                    <Icon name="history" className="text-[18px] text-jp-text-muted shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-jp-text-primary truncate">{item.query}</p>
                      <p className="text-[12px] text-jp-text-muted">{item.results}</p>
                    </div>
                    <span className="text-[11px] text-jp-text-muted shrink-0">{item.time}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Right: Insights */}
          <div className="space-y-6">

            {/* Profile Strength */}
            <div className="jp-card p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[13px] font-semibold text-jp-text-primary">Profile Strength</h3>
                <span className="jp-badge jp-badge-success">High</span>
              </div>
              <div className="flex items-center gap-4 mb-4">
                <CircularProgress percentage={85} size={64} strokeWidth={5} label="Score" />
                <div>
                  <p className="text-[13px] text-jp-text-secondary">Excellent match for Senior DevOps roles</p>
                  <Link to="/profile" className="text-[12px] text-jp-accent hover:text-jp-accent-hover no-underline mt-1 inline-block">
                    Improve Profile →
                  </Link>
                </div>
              </div>
            </div>

            {/* Top Skills */}
            <div className="jp-card p-5">
              <h3 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Icon name="verified" fill className="text-[14px] text-jp-success" />
                Top Skills
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {["AWS", "Docker", "Kubernetes", "Python", "Linux"].map(skill => (
                  <SkillTag key={skill} label={skill} variant="success" />
                ))}
              </div>
            </div>

            {/* Skill Gaps */}
            <div className="jp-card p-5">
              <h3 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Icon name="trending_up" className="text-[14px] text-jp-warning" />
                Skills to Learn
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {["Terraform", "Jenkins", "Golang"].map(skill => (
                  <SkillTag key={skill} label={skill} variant="warning" />
                ))}
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="jp-card p-5">
              <h3 className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Icon name="lightbulb" fill className="text-[14px] text-jp-accent" />
                AI Recommendations
              </h3>
              <ul className="space-y-3">
                {[
                  <>Add <strong>CI/CD automation</strong> metrics to your latest resume.</>,
                  <>Highlight <strong>deployment frequency</strong> improvements for better match scores.</>,
                  <>Update your <strong>Cloud Architect</strong> certification to current date.</>,
                ].map((tip, i) => (
                  <li key={i} className="flex gap-2.5 text-[13px] text-jp-text-secondary leading-relaxed">
                    <div className="w-1 h-1 rounded-full bg-jp-accent mt-2 shrink-0" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-4 pt-4 border-t border-jp-border-subtle">
                <Link to="/insights" className="text-[12px] font-bold text-jp-accent hover:text-jp-accent-hover flex items-center gap-1 no-underline transition-colors w-max">
                  <Icon name="auto_awesome" className="text-[14px]" /> View Full Career Roadmap
                </Link>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: "add_task", label: "New Resume", color: "text-jp-accent", to: "/resumes" },
                { icon: "travel_explore", label: "Browse Jobs", color: "text-jp-success", to: "/search" },
                { icon: "auto_awesome", label: "Career Agent", color: "text-amber-500", to: "/insights" },
                { icon: "analytics", label: "View Stats", color: "text-jp-text-tertiary", to: "/profile" },
              ].map(action => (
                <Link
                  key={action.label}
                  to={action.to}
                  className="jp-card-interactive flex flex-col items-center gap-2 p-4 text-center no-underline"
                >
                  <div className="w-10 h-10 rounded-lg bg-jp-bg-raised flex items-center justify-center">
                    <Icon name={action.icon} className={`text-[20px] ${action.color}`} />
                  </div>
                  <span className="text-[12px] font-medium text-jp-text-secondary">{action.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}