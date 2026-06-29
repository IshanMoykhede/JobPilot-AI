import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Icon from '../components/common/Icon';

function LandingPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user && !loading) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, loading, navigate]);

  return (
    <div className="bg-jp-bg-app min-h-screen flex flex-col font-sans selection:bg-jp-accent/30 selection:text-jp-text-primary">
      <Header />
      
      <main className="flex-1 overflow-x-hidden">
        {/* ── Hero Section ──────────────────────────────── */}
        <section className="relative pt-32 pb-24 md:pt-48 md:pb-32 px-6 flex flex-col items-center justify-center text-center overflow-hidden">
          {/* Background Glows */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-jp-accent/15 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-jp-success/10 rounded-full blur-[120px] pointer-events-none" />
          
          <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
            {/* Pill */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-jp-accent-muted/20 border border-jp-accent/20 mb-8 backdrop-blur-md">
              <Icon name="auto_awesome" className="text-[16px] text-jp-accent" />
              <span className="text-[12px] font-semibold text-jp-accent tracking-wide uppercase">New: ATS Analysis Engine v2.0</span>
            </div>
            
            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-jp-text-primary mb-6 leading-[1.1]">
              Land Your Next Job <br className="hidden md:block"/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-jp-accent to-blue-400">With AI Precision.</span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-[18px] md:text-[20px] text-jp-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
              Search jobs, analyze ATS fit, generate tailored resumes, and discover skill gaps using your personal high-precision AI co-pilot.
            </p>
            
            {/* CTA */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center w-full sm:w-auto">
              <Link to="/auth" className="w-full sm:w-auto px-8 py-3.5 bg-jp-text-primary text-jp-bg-app rounded-xl font-semibold hover:bg-jp-text-secondary transition-colors text-center text-[15px]">
                Start Searching Free
              </Link>
              <Link to="#demo" className="w-full sm:w-auto px-8 py-3.5 bg-jp-bg-raised border border-jp-border text-jp-text-primary rounded-xl font-semibold hover:border-jp-accent/50 hover:bg-jp-bg-surface transition-colors flex items-center justify-center gap-2 text-[15px]">
                <Icon name="play_circle" className="text-[20px]" />
                Watch Demo
              </Link>
            </div>
          </div>
        </section>

        {/* ── Workflow Diagram ──────────────────────────── */}
        <section className="py-12 px-6 border-y border-jp-border-subtle bg-jp-bg-surface/50">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-8 items-center text-center">
              {[
                { icon: "search", label: "Search Jobs", color: "text-jp-text-primary" },
                { icon: "analytics", label: "Analyze Fit", color: "text-jp-text-primary" },
                { icon: "bolt", label: "Match Skills", color: "text-jp-text-primary" },
                { icon: "edit_document", label: "Tailor Resume", color: "text-jp-text-primary" },
                { icon: "workspace_premium", label: "Get Hired", color: "text-jp-success", bg: "bg-jp-success-muted/20 border-jp-success/20" },
              ].map((step, i) => (
                <div key={i} className="flex flex-col items-center">
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-4 ${step.bg || 'bg-jp-bg-raised border border-jp-border'}`}>
                    <Icon name={step.icon} className={`text-[28px] ${step.color}`} />
                  </div>
                  <h3 className="text-[14px] font-semibold text-jp-text-primary">{step.label}</h3>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Features Grid ─────────────────────────────── */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-4xl font-semibold tracking-tight text-jp-text-primary mb-4">Powerful AI Features</h2>
              <p className="text-[18px] text-jp-text-secondary max-w-2xl mx-auto">The ultimate toolset for the high-performance modern job seeker.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { icon: "travel_explore", title: "AI Job Search", desc: "Automatically crawl job boards and filter by your exact skill match and preference profile." },
                { icon: "fact_check", title: "ATS Score Analysis", desc: "Know exactly how recruiters see your resume. Get a precise score and fix hidden issues." },
                { icon: "history_edu", title: "Resume Tailoring", desc: "Generate context-aware bullet points that highlight relevant experience for every specific role." },
                { icon: "extension", title: "Skill Gap Detection", desc: "Identify the exact certifications or projects you need to become the top 1% candidate." },
                { icon: "view_kanban", title: "Application Tracking", desc: "Centralized pipeline for all your interviews. Never miss a follow-up or response." },
                { icon: "insights", title: "Career Insights", desc: "Predict salary trends and long-term career growth paths based on real-time market data." },
              ].map((feature, i) => (
                <div key={i} className="jp-card p-8 hover:border-jp-accent/30 transition-all group relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-10 transition-opacity">
                    <Icon name={feature.icon} className="text-8xl text-jp-text-primary" />
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-jp-bg-raised border border-jp-border flex items-center justify-center mb-6">
                    <Icon name={feature.icon} className="text-[24px] text-jp-text-primary" />
                  </div>
                  <h3 className="text-[18px] font-semibold text-jp-text-primary mb-3 relative z-10">{feature.title}</h3>
                  <p className="text-[14px] text-jp-text-secondary leading-relaxed relative z-10">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA Section ───────────────────────────────── */}
        <section className="py-32 px-6 bg-jp-bg-inset border-t border-jp-border-subtle">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-semibold tracking-tight text-jp-text-primary mb-6">Ready to Find Your Next Opportunity?</h2>
            <p className="text-[18px] text-jp-text-secondary mb-10 max-w-2xl mx-auto">
              Join thousands of professionals landing better jobs faster with AI.
            </p>
            <Link to="/auth" className="inline-block px-8 py-4 bg-jp-accent text-white rounded-xl font-semibold text-[16px] hover:bg-jp-accent-hover transition-colors shadow-lg shadow-jp-accent/20">
              Get Started Now — It's Free
            </Link>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}

export default LandingPage;
