import React from 'react';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';
import CircularProgress from '../components/common/CircularProgress';

function Resumes() {
  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "Generated Resumes" },
    ]}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Grid & Filters */}
          <div className="flex-1 space-y-6">
            {/* Filter Bar */}
            <section className="jp-card p-3 flex flex-wrap items-center gap-3">
              <div className="flex-1 min-w-[200px] relative">
                <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-jp-text-muted" />
                <input
                  type="text"
                  placeholder="Search resumes..."
                  className="w-full pl-9 pr-3 py-1.5 bg-jp-bg-app border border-jp-border rounded-md text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
                />
              </div>
              <div className="flex items-center gap-2">
                <select className="jp-select text-[12px] py-1.5 pl-3 pr-7">
                  <option>All Dates</option>
                  <option>Today</option>
                  <option>This Week</option>
                </select>
                <select className="jp-select text-[12px] py-1.5 pl-3 pr-7">
                  <option>Role: All</option>
                  <option>DevOps</option>
                  <option>Backend</option>
                </select>
                <select className="jp-select text-[12px] py-1.5 pl-3 pr-7">
                  <option>Sort: Match Score</option>
                  <option>Sort: Newest</option>
                </select>
              </div>
            </section>

            {/* Resume Grid */}
            <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {[
                { title: "Senior DevOps Engineer", company: "Infosys", version: "v1.2", date: "Generated Today", match: 89, icon: "terminal" },
                { title: "Lead Backend Architect", company: "Google Cloud Platform", version: "v1.0", date: "2 days ago", match: 94, icon: "code" },
                { title: "Senior UX Designer", company: "Stripe", version: "v2.1", date: "1 week ago", match: 82, icon: "brush" },
              ].map((resume, idx) => (
                <div key={idx} className="jp-card-interactive p-5 flex flex-col relative group">
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 rounded-lg bg-jp-bg-raised flex items-center justify-center shrink-0">
                      <Icon name={resume.icon} className="text-[20px] text-jp-text-tertiary" />
                    </div>
                    <span className="jp-badge jp-badge-accent">{resume.version}</span>
                  </div>
                  
                  <div className="flex-1 mb-5">
                    <h3 className="text-[15px] font-semibold text-jp-text-primary mb-1 line-clamp-1">{resume.title}</h3>
                    <p className="text-[13px] text-jp-text-secondary">{resume.company}</p>
                    <p className="text-[12px] text-jp-text-muted mt-3 flex items-center gap-1.5">
                      <Icon name="schedule" className="text-[14px]" />
                      {resume.date}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-jp-border-subtle">
                    <div className="flex items-center gap-3">
                      <CircularProgress percentage={resume.match} size={36} strokeWidth={3} />
                      <span className="text-[12px] font-medium text-jp-text-secondary">Match Score</span>
                    </div>
                    <div className="flex gap-1">
                      <button className="jp-btn-icon jp-btn-ghost hover:text-jp-accent" title="Download PDF">
                        <Icon name="download" className="text-[18px]" />
                      </button>
                      <button className="jp-btn-icon jp-btn-ghost" title="More options">
                        <Icon name="more_vert" className="text-[18px]" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {/* Generate New Card */}
              <button className="jp-card border-dashed border-2 border-jp-border-subtle hover:border-jp-accent hover:bg-jp-accent-muted/20 flex flex-col items-center justify-center min-h-[220px] group transition-all">
                <div className="w-12 h-12 rounded-full bg-jp-bg-raised group-hover:bg-jp-accent flex items-center justify-center mb-3 transition-colors">
                  <Icon name="add" className="text-[24px] text-jp-text-muted group-hover:text-white transition-colors" />
                </div>
                <span className="text-[14px] font-medium text-jp-text-secondary group-hover:text-jp-accent transition-colors">
                  Generate New
                </span>
              </button>
            </section>
          </div>

          {/* Right Panel: Statistics */}
          <aside className="w-full lg:w-[320px] space-y-5">
            {/* Resume Statistics Card */}
            <section className="jp-card p-5">
              <h3 className="text-[14px] font-semibold text-jp-text-primary mb-4 flex items-center gap-2">
                <Icon name="analytics" className="text-[18px] text-jp-accent" />
                Resume Statistics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-[13px] text-jp-text-secondary">Total Resumes</span>
                  <span className="text-[14px] font-semibold text-jp-text-primary">15</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[13px] text-jp-text-secondary">Most Targeted</span>
                  <span className="jp-badge jp-badge-neutral">DevOps</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[13px] text-jp-text-secondary">Last Generated</span>
                  <span className="text-[13px] font-medium text-jp-text-primary">Today</span>
                </div>
              </div>
              <div className="mt-5 pt-5 border-t border-jp-border-subtle">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-[11px] font-medium text-jp-text-muted">Storage Quota</span>
                  <span className="text-[11px] text-jp-text-muted">6.5 MB / 10 MB</span>
                </div>
                <div className="h-1.5 w-full bg-jp-bg-raised rounded-full overflow-hidden">
                  <div className="h-full bg-jp-accent rounded-full" style={{ width: "65%" }}></div>
                </div>
              </div>
            </section>

            {/* Recent Activity */}
            <section className="jp-card p-5">
              <h3 className="text-[14px] font-semibold text-jp-text-primary mb-4">Recent Activity</h3>
              <ul className="space-y-4">
                <li className="flex gap-3">
                  <div className="w-2 h-2 mt-1.5 rounded-full bg-jp-accent shrink-0" />
                  <div>
                    <p className="text-[13px] text-jp-text-primary font-medium leading-tight">DevOps Resume updated</p>
                    <p className="text-[11px] text-jp-text-muted mt-0.5">14 mins ago</p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 mt-1.5 rounded-full bg-jp-success shrink-0" />
                  <div>
                    <p className="text-[13px] text-jp-text-primary font-medium leading-tight">PDF Exported: Google Cloud</p>
                    <p className="text-[11px] text-jp-text-muted mt-0.5">2 hours ago</p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 mt-1.5 rounded-full bg-jp-warning shrink-0" />
                  <div>
                    <p className="text-[13px] text-jp-text-primary font-medium leading-tight">Shared with 3 recruiters</p>
                    <p className="text-[11px] text-jp-text-muted mt-0.5">Yesterday</p>
                  </div>
                </li>
              </ul>
              <button className="jp-btn jp-btn-ghost w-full mt-4 jp-btn-sm text-[12px]">
                View Full History
              </button>
            </section>

            {/* AI Tips Card */}
            <section className="p-5 rounded-xl border border-jp-accent/20 bg-jp-accent-muted/20 relative overflow-hidden">
              <div className="relative z-10">
                <h4 className="text-[13px] font-semibold text-jp-text-primary mb-2 flex items-center gap-1.5">
                  <Icon name="lightbulb" fill className="text-[16px] text-jp-accent" />
                  AI Suggestion
                </h4>
                <p className="text-[12px] text-jp-text-secondary mb-4 leading-relaxed">
                  Try targeting "Cloud Infrastructure" keywords to increase your DevOps match score by 12%.
                </p>
                <button className="jp-btn jp-btn-primary w-full jp-btn-sm">
                  Apply Optimizations
                </button>
              </div>
            </section>
          </aside>
        </div>
      </div>
      
      {/* Mobile FAB */}
      <button className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-jp-accent text-white shadow-lg flex items-center justify-center md:hidden hover:bg-jp-accent-hover transition-colors z-40">
        <Icon name="add" className="text-[24px]" />
      </button>
    </AppShell>
  );
}

export default Resumes;
