import React from "react";
import { useAuth } from "../context/AuthContext";
import Icon, { withRipple, resetRipple } from "../components/common/Icon";
import SkillTag from "../components/common/SkillTag";
import CircularProgress from "../components/common/CircularProgress";
import Sidebar from "../components/layout/SideBar";
import UserProfileCard from "../components/layout/userProfileCard";
import TopHeader from "../components/layout/TopHeader";
import GlobalSearchInput from "../components/layout/GlobalSearchInput";
import HeaderNavActions from "../components/layout/HeaderNavActions";
import AIJobSearchBar from "../components/dashboard/AIJobSearchBar";
import QuickActionButton from "../components/dashboard/QuickActionButton";
import ListRowCard from "../components/dashboard/ListRowCard";
import { themeVars } from "../styles/Theme";

export default function Dashboard() {
  const { user } = useAuth();
  const firstName = user?.name?.split(" ")[0] || "there";

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
        {/* Left Column: Sidebar */}
        <Sidebar activeItem="dashboard" bottomCard={<UserProfileCard name={user?.name} />} />

        {/* Center Column: Main Workspace */}
        <main className="flex-1 h-full overflow-y-auto relative" style={{ backgroundColor: "rgba(248,249,255,0.5)" }}>
          {/* <TopHeader left={<GlobalSearchInput />} right={<HeaderNavActions />} /> */}

          <div className="p-8 space-y-6 max-w-5xl mx-auto">
            {/* Welcome Section */}
            <section>
              <h2 className="text-[36px] leading-[44px] tracking-[-0.02em] font-semibold mb-4" style={{ color: "var(--color-on-surface)" }}>
                Welcome Back, {firstName}
              </h2>
              <p className="text-[16px] leading-[24px]" style={{ color: "var(--color-on-surface-variant)" }}>
                Search jobs and generate tailored resumes with AI assistance.
              </p>
            </section>

            {/* AI Job Search Section */}
            <AIJobSearchBar
              placeholder="Try: DevOps Engineer in Pune..."
              suggestions={["DevOps Engineer", "Frontend Developer", "SRE Manager", "Cloud Architect"]}
            />

            {/* Bento Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recently Generated Resumes */}
              <section className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-[20px] leading-[28px] font-semibold" style={{ color: "var(--color-on-surface)" }}>
                    Recent Resumes
                  </h3>
                  <button className="text-[12px] leading-[16px] tracking-[0.01em] font-semibold hover:underline" style={{ color: "var(--color-primary)" }}>
                    View All
                  </button>
                </div>
                <div className="space-y-3">
                  <ListRowCard
                    icon="picture_as_pdf"
                    iconFill
                    iconBgColor="#fef2f2"
                    iconColor="#ef4444"
                    title="DevOps @ Infosys"
                    subtitle="Generated 2h ago"
                    right={
                      <button
                        className="p-2 rounded-lg transition-colors group-hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-container)]"
                        style={{ color: "var(--color-outline)" }}
                      >
                        <Icon name="download" />
                      </button>
                    }
                  />
                  <ListRowCard
                    icon="description"
                    iconFill
                    iconBgColor="#eff6ff"
                    iconColor="var(--color-primary)"
                    title="SRE Engineer @ Google"
                    subtitle="Generated Yesterday"
                    right={
                      <button
                        className="p-2 rounded-lg transition-colors group-hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-container)]"
                        style={{ color: "var(--color-outline)" }}
                      >
                        <Icon name="download" />
                      </button>
                    }
                  />
                </div>
              </section>

              {/* Recent Searches */}
              <section className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-[20px] leading-[28px] font-semibold" style={{ color: "var(--color-on-surface)" }}>
                    Search History
                  </h3>
                  <button className="text-[12px] leading-[16px] tracking-[0.01em] font-semibold hover:underline" style={{ color: "var(--color-primary)" }}>
                    Clear
                  </button>
                </div>
                <div className="space-y-3">
                  <ListRowCard
                    icon="history"
                    iconBgColor="var(--color-surface-container)"
                    iconColor="var(--color-on-surface-variant)"
                    title="Cloud Engineer in Bangalore"
                    subtitle="12 results found"
                    hoverEffect={false}
                    right={
                      <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium" style={{ color: "var(--color-outline)" }}>
                        2d ago
                      </p>
                    }
                  />
                  <ListRowCard
                    icon="history"
                    iconBgColor="var(--color-surface-container)"
                    iconColor="var(--color-on-surface-variant)"
                    title="Remote Kubernetes Architect"
                    subtitle="45 results found"
                    hoverEffect={false}
                    right={
                      <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium" style={{ color: "var(--color-outline)" }}>
                        4d ago
                      </p>
                    }
                  />
                </div>
              </section>
            </div>

            {/* Quick Actions */}
            <section className="space-y-4">
              <h3 className="text-[20px] leading-[28px] font-semibold" style={{ color: "var(--color-on-surface)" }}>
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <QuickActionButton icon="add_task" label="New Resume" iconBgColor="rgba(0,62,199,0.1)" iconColor="var(--color-primary)" />
                <QuickActionButton icon="travel_explore" label="Browse Jobs" iconBgColor="rgba(0,84,121,0.1)" iconColor="var(--color-tertiary)" />
                <QuickActionButton icon="backup" label="Upload New" iconBgColor="rgba(70,72,212,0.1)" iconColor="var(--color-secondary)" />
                <QuickActionButton icon="analytics" label="View Stats" iconBgColor="var(--color-surface-variant)" iconColor="var(--color-on-surface-variant)" />
              </div>
            </section>
          </div>
        </main>

        {/* Right Column: Insights Panel */}
        <aside className="hidden lg:flex flex-col w-80 h-full border-l bg-white p-6 shrink-0 overflow-y-auto" style={{ borderColor: "var(--color-outline-variant)" }}>
          <h2 className="text-[20px] leading-[28px] font-semibold mb-6" style={{ color: "var(--color-on-surface)" }}>
            Profile Insights
          </h2>
          <div className="space-y-8">
            {/* Profile Strength */}
            <div className="text-center p-6 rounded-2xl border" style={{ backgroundColor: "var(--color-surface-container-low)", borderColor: "rgba(195,197,217,0.5)" }}>
              <div className="mx-auto mb-4 flex justify-center">
                <CircularProgress percentage={85} size={128} label="Score" />
              </div>
              <p className="text-[14px] leading-[20px] font-bold" style={{ color: "var(--color-on-surface)" }}>
                Profile Strength: High
              </p>
              <p className="text-[12px] leading-[16px] tracking-[0.01em] font-medium mt-1" style={{ color: "var(--color-outline)" }}>
                Excellent for Senior DevOps roles
              </p>
            </div>

            {/* Top Skills */}
            <div>
              <h3 className="text-[12px] leading-[16px] tracking-[0.01em] font-bold uppercase tracking-widest mb-4 flex items-center gap-2" style={{ color: "var(--color-outline)" }}>
                <Icon name="verified" className="text-[16px]" />
                Top Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {["AWS", "Docker", "Kubernetes", "Python", "Linux"].map((skill) => (
                  <SkillTag key={skill} label={skill} variant="green" />
                ))}
              </div>
            </div>

            {/* Skill Gap */}
            <div>
              <h3 className="text-[12px] leading-[16px] tracking-[0.01em] font-bold uppercase tracking-widest mb-4 flex items-center gap-2" style={{ color: "var(--color-outline)" }}>
                <Icon name="warning" className="text-[16px]" />
                Requested Missing Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {["Terraform", "Jenkins", "Golang"].map((skill) => (
                  <SkillTag key={skill} label={skill} variant="orange" />
                ))}
              </div>
            </div>

            {/* AI Recommendations */}
            <div>
              <h3 className="text-[12px] leading-[16px] tracking-[0.01em] font-bold uppercase tracking-widest mb-4 flex items-center gap-2" style={{ color: "var(--color-outline)" }}>
                <Icon name="lightbulb" className="text-[16px]" />
                AI Recommendations
              </h3>
              <ul className="space-y-4">
                <li className="flex gap-3">
                  <div className="w-1.5 h-1.5 rounded-full mt-2" style={{ backgroundColor: "var(--color-primary)" }} />
                  <p className="text-[14px] leading-[20px] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                    Add <span className="font-bold">CI/CD automation</span> metrics to your latest resume version.
                  </p>
                </li>
                <li className="flex gap-3">
                  <div className="w-1.5 h-1.5 rounded-full mt-2" style={{ backgroundColor: "var(--color-primary)" }} />
                  <p className="text-[14px] leading-[20px] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                    Highlight <span className="font-bold">deployment frequency</span> improvements for better match scores.
                  </p>
                </li>
                <li className="flex gap-3">
                  <div className="w-1.5 h-1.5 rounded-full mt-2" style={{ backgroundColor: "var(--color-primary)" }} />
                  <p className="text-[14px] leading-[20px] font-medium" style={{ color: "var(--color-on-surface-variant)" }}>
                    Update your <span className="font-bold">Cloud Architect</span> certification to current date.
                  </p>
                </li>
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}