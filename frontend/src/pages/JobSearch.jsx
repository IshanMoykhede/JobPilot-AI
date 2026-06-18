import React from "react";
import Sidebar from "../components/layout/SideBar";
import PromoCard from "../components/layout/PromoCard";
import TopHeader from "../components/layout/TopHeader";
import Breadcrumb from "../components/layout/Breadcrumb";
import UserAvatarMenu from "../components/layout/UserAvatarMenu";
import ResultsSummaryBar from "../components/search-results/ResultsSummaryBar";
import FilterBar from "../components/search-results/FilterBar";
import JobResultCard from "../components/search-results/JobResultCard";
import InsightsPanelCard from "../components/search-results/InsightsPanelCard";
import SkillProgressBar from "../components/search-results/SkillProgressBar";
import Icon from "../components/common/Icon";
import { themeVars } from "../styles/Theme";

export default function JobSearch() {
  return (
    <div
      style={{
        ...themeVars,
        fontFamily: "'Inter', sans-serif",
        backgroundColor: "var(--color-background)",
        color: "var(--color-on-background)",
        minHeight: "100vh",
      }}
      className="selection:bg-[var(--color-primary-container)] selection:text-[var(--color-on-primary-container)]"
    >
      <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />
      <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
        rel="stylesheet"
      />

      <div className="flex h-screen overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar activeItem="search" bottomCard={<PromoCard />} />

        {/* Main Content Pane */}
        <div className="flex-1 flex flex-col h-full overflow-hidden" style={{ backgroundColor: "rgba(248,249,255,0.5)" }}>
        {/* Top Header */}
        <TopHeader
          left={
            <Breadcrumb
              items={[
                { label: "Dashboard", href: "/dashboard" },
                { label: "Search Results" },
              ]}
            />
          }
          right={<UserAvatarMenu name="Alex Chen" />}
        />

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto flex flex-col justify-between">
          <div className="px-8 py-6 space-y-6 max-w-7xl w-full mx-auto">
            {/* Summary Bar */}
            <ResultsSummaryBar
              title="DevOps Engineer Jobs in Pune"
              stats={[
                { label: "127 Jobs Found" },
                { label: "10 Top Matches" },
                { label: "Average Match: 78%" },
              ]}
              onShareClick={() => alert("Sharing search results...")}
            />

            {/* Filter Bar */}
            <FilterBar
              filters={[
                { label: "Location", options: ["Pune", "Remote", "Bengaluru"] },
                { label: "Experience", options: ["0-2 years", "3-5 years", "5+ years"] },
                { label: "Work Mode", options: ["Remote", "Hybrid", "On-site"] },
                { label: "Min Match Score", options: ["70%+", "80%+", "90%+"] },
              ]}
              sortOptions={["Highest Match", "Most Recent", "Salary Range"]}
              sortValue="Highest Match"
              onFilterChange={(label, val) => console.log(`Filter ${label} changed to ${val}`)}
              onSortChange={(val) => console.log(`Sort changed to ${val}`)}
            />

            {/* Job Search & Insights Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              {/* Left: Job listings */}
              <div className="lg:col-span-8 space-y-4">
                <JobResultCard
                  logo={
                    <div className="w-full h-full bg-[#0a192f] flex items-center justify-center rounded-lg">
                      <div className="w-5 h-5 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee]"></div>
                    </div>
                  }
                  title="Senior DevOps Architect"
                  company="CloudStream Solutions"
                  location="Pune"
                  workMode="Hybrid"
                  matchPercentage={94}
                  recommended={{ rank: 1 }}
                  matchingSkills={["AWS (Expert)", "Docker", "Kubernetes"]}
                  missingSkills={["Terraform", "ArgoCD"]}
                  insightText={
                    <>
                      Your experience with EKS perfectly aligns with their stack. Mentioning your{" "}
                      <strong>multi-cluster management</strong> could secure an interview.
                    </>
                  }
                  onGenerateResume={() => alert("Generating tailored resume for Senior DevOps Architect...")}
                  onViewDetails={() => alert("Opening job details...")}
                />

                <JobResultCard
                  logo={
                    <div className="w-full h-full bg-[#1e293b] flex items-center justify-center rounded-lg">
                      <div className="w-4 h-4 rounded-full bg-amber-400"></div>
                    </div>
                  }
                  title="Cloud Infrastructure Engineer"
                  company="Nexus Systems"
                  location="Pune"
                  workMode="On-site"
                  matchPercentage={82}
                  matchingSkills={["Linux", "Terraform"]}
                  missingSkills={["Jenkins CI"]}
                  missingSkillsVariant="red"
                  summaryText="You meet 8 out of 10 primary requirements. They focus heavily on Infrastructure as Code."
                  onGenerateResume={() => alert("Generating tailored resume for Cloud Infrastructure Engineer...")}
                  onViewDetails={() => alert("Opening job details...")}
                />

                <JobResultCard
                  logo={
                    <div className="w-full h-full bg-[#111827] flex items-center justify-center rounded-lg">
                      <div className="w-4 h-4 rounded bg-emerald-400 transform rotate-45"></div>
                    </div>
                  }
                  title="Platform Engineer (SRE)"
                  company="Velocity AI"
                  location="Pune"
                  workMode="Remote"
                  matchPercentage={76}
                  matchingSkills={["Prometheus", "Go"]}
                  missingSkills={["Service Mesh"]}
                  missingSkillsVariant="red"
                  onGenerateResume={() => alert("Generating tailored resume for Platform Engineer...")}
                  onViewDetails={() => alert("Opening job details...")}
                />
              </div>

              {/* Right: Insights Sidebar */}
              <aside className="lg:col-span-4 space-y-4">
                <h3
                  className="text-[14px] leading-[20px] font-bold uppercase tracking-wider flex items-center gap-2 px-1"
                  style={{ color: "var(--color-on-surface-variant)" }}
                >
                  <Icon name="auto_awesome" className="text-primary text-[18px]" />
                  AI Search Insights
                </h3>

                <div className="space-y-4">
                  {/* Skills Found */}
                  <InsightsPanelCard icon="insights" title="Most Common Skills Found">
                    <div className="space-y-3 mt-1">
                      <SkillProgressBar label="AWS" percentage={80} />
                      <SkillProgressBar label="Docker" percentage={65} />
                      <SkillProgressBar label="Linux" percentage={55} />
                    </div>
                  </InsightsPanelCard>

                  {/* Skills to Learn */}
                  <InsightsPanelCard title="Skills to Learn" variant="alert">
                    <div className="space-y-3 mt-1">
                      <div className="flex flex-wrap gap-2">
                        <span className="inline-flex items-center gap-1 bg-[#fff7ed] text-[#c2410c] border border-[#fed7aa] rounded px-2.5 py-0.5 text-[12px] font-semibold">
                          ⬈ Terraform
                        </span>
                        <span className="inline-flex items-center gap-1 bg-[#fff7ed] text-[#c2410c] border border-[#fed7aa] rounded px-2.5 py-0.5 text-[12px] font-semibold">
                          ⬈ Jenkins
                        </span>
                        <span className="inline-flex items-center gap-1 bg-[#fff7ed] text-[#c2410c] border border-[#fed7aa] rounded px-2.5 py-0.5 text-[12px] font-semibold">
                          ⬈ CI/CD
                        </span>
                      </div>
                      <p className="text-[12px] text-[#9a3412] leading-[16px]">
                        These skills appear in 60%+ of your search results.
                      </p>
                    </div>
                  </InsightsPanelCard>

                  {/* Market Intelligence */}
                  <InsightsPanelCard icon="analytics" title="Market Intelligence">
                    <ul className="space-y-2 text-[13px] leading-[18px] list-disc pl-4 mt-1" style={{ color: "var(--color-on-surface-variant)" }}>
                      <li>
                        <strong>72%</strong> of matching jobs in Pune require{" "}
                        <span className="underline cursor-pointer">AWS Certification</span>.
                      </li>
                      <li>
                        Salary range for your profile is <strong>15% higher</strong> than average.
                      </li>
                    </ul>
                  </InsightsPanelCard>

                  {/* Profile Optimization */}
                  <InsightsPanelCard icon="check_circle" title="Profile Optimization" variant="highlight">
                    <div className="space-y-3 mt-1">
                      <p className="text-[13px] leading-[18px] text-white/90">
                        Add <strong>deployment metrics</strong> (e.g., 'reduced downtime by 30%') to
                        your resume to increase your match score with Top 3 employers.
                      </p>
                      <button className="w-full py-2 bg-white text-primary font-bold rounded-lg text-[13px] leading-[18px] transition-colors hover:bg-white/95">
                        Apply Recommendations
                      </button>
                    </div>
                  </InsightsPanelCard>

                  {/* Suggested Follow-ups */}
                  <div
                    className="border rounded-xl p-4 bg-white space-y-3"
                    style={{ borderColor: "var(--color-outline-variant)" }}
                  >
                    <h4 className="text-[11px] font-bold uppercase tracking-wider" style={{ color: "var(--color-outline)" }}>
                      Suggested Follow-ups
                    </h4>
                    <div className="flex flex-col gap-2">
                      {[
                        "Show only remote roles?",
                        "What's the salary range?",
                        "Learn Terraform fast?",
                        "Best company culture?",
                      ].map((text) => (
                        <button
                          key={text}
                          className="w-full text-left px-3 py-2 bg-white border rounded-lg text-[13px] leading-[18px] font-medium transition-colors hover:bg-[var(--color-surface-container-low)]"
                          style={{ borderColor: "var(--color-outline-variant)", color: "var(--color-on-surface)" }}
                          onClick={() => alert(`Asking AI: "${text}"`)}
                        >
                          {text}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </div>

          {/* Sticky Bottom Search input bar */}
          <div className="sticky bottom-4 mx-auto max-w-2xl w-full px-4 pb-4 mt-6">
            <div
              className="bg-white border rounded-full pl-5 pr-2 py-2 flex items-center shadow-lg hover:shadow-xl focus-within:ring-2 focus-within:ring-primary/20 transition-all"
              style={{ borderColor: "var(--color-outline-variant)" }}
            >
              <Icon name="auto_awesome" className="text-primary mr-3 text-[20px]" />
              <input
                type="text"
                placeholder="Ask AI to refine your search..."
                className="flex-1 bg-transparent border-none outline-none focus:ring-0 text-[14px]"
              />
              <button
                className="w-9 h-9 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-md hover:opacity-90 transition-opacity shrink-0"
                onClick={() => alert("Refining search with AI...")}
              >
                <Icon name="search" className="text-[18px]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  );
}