import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Icon from '../components/common/Icon';

function LandingPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    if (user && !loading) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="bg-jp-bg-app min-h-screen flex flex-col font-sans selection:bg-jp-accent/30 selection:text-jp-text-primary overflow-hidden">
      <Header />
      
      <main className="flex-1">
        {/* ── Hero Section ──────────────────────────────── */}
        <section className="relative pt-32 pb-24 md:pt-48 md:pb-40 px-6 flex flex-col items-center justify-center text-center">
          {/* Animated Grid Background */}
          <div className="absolute inset-0 bg-grid opacity-10 z-0"></div>
          
          {/* Background Glows */}
          <div 
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-jp-accent/5 rounded-full blur-[150px] pointer-events-none z-0 transition-transform duration-75 ease-out" 
            style={{ transform: `translate(-50%, ${scrollY * 0.2}px)` }}
          />
          <div 
            className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-jp-success/5 rounded-full blur-[120px] pointer-events-none z-0 transition-transform duration-75 ease-out" 
            style={{ transform: `translateY(${scrollY * 0.15}px)` }}
          />
          
          <div className="relative z-10 max-w-5xl mx-auto flex flex-col items-center animate-slide-up w-full">
            
            {/* Parallax Floating Product Badges (Desktop Only) */}
            <div 
              className="hidden md:flex absolute top-10 -left-10 items-center gap-2 bg-jp-bg-surface/80 backdrop-blur-md border border-jp-border-subtle px-4 py-2 rounded-xl shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-transform duration-75 ease-out"
              style={{ transform: `translateY(${scrollY * -0.2}px)` }}
            >
              <Icon name="check_circle" className="text-jp-success text-[16px]" />
              <span className="text-[12px] font-semibold text-jp-text-primary">ATS Optimized</span>
            </div>
            
            <div 
              className="hidden md:flex absolute top-40 -right-4 items-center gap-2 bg-jp-bg-surface/80 backdrop-blur-md border border-jp-border-subtle px-4 py-2 rounded-xl shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-transform duration-75 ease-out"
              style={{ transform: `translateY(${scrollY * -0.1}px)` }}
            >
              <div className="w-2 h-2 rounded-full bg-jp-accent animate-pulse"></div>
              <span className="text-[12px] font-semibold text-jp-text-primary">98% Match Score</span>
            </div>

            <div 
              className="hidden md:flex absolute -bottom-4 left-16 items-center gap-2 bg-jp-bg-surface/80 backdrop-blur-md border border-jp-border-subtle px-4 py-2 rounded-xl shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-transform duration-75 ease-out"
              style={{ transform: `translateY(${scrollY * -0.4}px)` }}
            >
              <Icon name="psychology" className="text-purple-400 text-[16px]" />
              <span className="text-[12px] font-semibold text-jp-text-primary">Skill Gap Analysis</span>
            </div>

            {/* Pill */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-jp-accent/10 border border-jp-accent/20 mb-8 backdrop-blur-md shadow-[0_0_15px_rgba(255,255,255,0.05)] text-[12px] font-bold text-jp-accent tracking-widest uppercase">
              <Icon name="bolt" className="text-[16px] animate-pulse" fill />
              The Job Search Cheat Code
            </div>
            
            {/* Headline */}
            <h1 className="text-5xl md:text-[5.5rem] font-extrabold tracking-tight text-jp-text-primary mb-8 leading-[1.05] drop-shadow-2xl">
              Stop Applying Into <br className="hidden md:block"/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-jp-accent via-blue-400 to-jp-accent-strong drop-shadow-[0_0_20px_var(--color-jp-accent-glow)]">The Black Hole.</span>
            </h1>
            
            {/* Subtitle / Scannable Checklist */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 mb-12 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center gap-2 text-jp-text-secondary text-[15px] font-medium">
                <Icon name="check" className="text-jp-success text-[18px]" />
                <span>AI finds relevant jobs</span>
              </div>
              <div className="flex items-center gap-2 text-jp-text-secondary text-[15px] font-medium">
                <Icon name="check" className="text-jp-success text-[18px]" />
                <span>Tailors every resume</span>
              </div>
              <div className="flex items-center gap-2 text-jp-text-secondary text-[15px] font-medium">
                <Icon name="check" className="text-jp-success text-[18px]" />
                <span>Identifies missing skills</span>
              </div>
            </div>
            
            {/* Cinematic CTA */}
            <div className="flex flex-col gap-6 justify-center items-center w-full animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <Link to="/auth" className="relative group w-full sm:w-auto">
                <div className="absolute -inset-1 bg-gradient-to-r from-jp-accent to-blue-500 rounded-xl blur opacity-20 group-hover:opacity-60 transition duration-500"></div>
                <button className="relative w-full sm:w-auto px-8 py-3.5 bg-jp-bg-surface border border-jp-border-subtle rounded-xl font-bold text-white transition-all hover:bg-jp-bg-raised text-[15px] flex items-center justify-center gap-3">
                  Find My Best Jobs <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>
              
              {/* Trust Indicators */}
              <div className="flex items-center gap-4 sm:gap-6 text-[12px] font-medium text-jp-text-tertiary">
                <span className="flex items-center gap-1.5"><Icon name="lock" className="text-[14px]" /> No credit card required</span>
                <span className="w-1 h-1 rounded-full bg-jp-border-subtle"></span>
                <span className="flex items-center gap-1.5"><Icon name="verified" className="text-[14px]" /> ATS Friendly</span>
                <span className="w-1 h-1 rounded-full bg-jp-border-subtle hidden sm:block"></span>
                <span className="hidden sm:flex items-center gap-1.5"><Icon name="update" className="text-[14px]" /> 10,000+ jobs indexed daily</span>
              </div>
            </div>
          </div>
        </section>

        {/* ── Dashboard Product Showcase (Flat UI) ──────────────────────────── */}
        <section className="relative px-6 pb-24 -mt-6 z-20">
          <div 
            className="max-w-5xl mx-auto transition-transform duration-75 ease-out"
            style={{ transform: `translateY(${scrollY * 0.08}px)` }}
          >
            <div className="w-full h-[300px] md:h-[500px] bg-jp-bg-surface border border-jp-border-subtle rounded-xl overflow-hidden flex flex-col relative shadow-[0_40px_80px_rgba(0,0,0,0.4)] ring-1 ring-white/5">
              {/* Browser Header */}
              <div className="h-12 bg-jp-bg-app/80 border-b border-jp-border-subtle flex items-center px-4 gap-2">
                <div className="w-3 h-3 rounded-full bg-jp-error"></div>
                <div className="w-3 h-3 rounded-full bg-jp-warning"></div>
                <div className="w-3 h-3 rounded-full bg-jp-success"></div>
                <div className="mx-auto bg-jp-bg-surface rounded-md px-32 py-1 text-[11px] font-medium text-jp-text-muted hidden md:block">app.jobpilot.ai/search</div>
              </div>
              {/* Abstract UI content */}
              <div className="flex-1 p-4 md:p-8 grid grid-cols-12 gap-6 relative overflow-y-auto overflow-x-hidden md:overflow-hidden">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-jp-accent/20 blur-[100px] rounded-full group-hover:bg-jp-accent/40 transition-colors duration-700"></div>
                
                {/* Sidebar Mock */}
                <div className="col-span-3 hidden md:flex flex-col gap-3">
                  <div className="h-8 bg-jp-bg-raised rounded-lg w-full flex items-center px-3 gap-2">
                    <Icon name="history" className="text-jp-accent text-[14px]" />
                    <span className="text-[11px] font-medium text-jp-text-primary">DevOps in Pune</span>
                  </div>
                  <div className="h-8 bg-transparent hover:bg-jp-bg-raised/50 rounded-lg w-full flex items-center px-3 gap-2">
                    <Icon name="history" className="text-jp-text-muted text-[14px]" />
                    <span className="text-[11px] font-medium text-jp-text-secondary">AI Engineer Roles</span>
                  </div>
                  <div className="h-8 bg-transparent hover:bg-jp-bg-raised/50 rounded-lg w-full flex items-center px-3 gap-2">
                    <Icon name="history" className="text-jp-text-muted text-[14px]" />
                    <span className="text-[11px] font-medium text-jp-text-secondary">Remote Next.js Dev</span>
                  </div>
                </div>
                
                {/* Main Content Mock */}
                <div className="col-span-12 md:col-span-9 flex flex-col gap-4">
                  <div className="h-12 bg-jp-bg-raised/50 border border-jp-accent/30 rounded-xl w-full flex items-center px-4 gap-3 shadow-[0_0_15px_rgba(255,255,255,0.05)]">
                    <Icon name="search" className="text-jp-accent text-[18px]" />
                    <span className="text-[13px] text-jp-text-primary">Senior React Developer at Stripe</span>
                  </div>
                  <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* Job Cards Column */}
                    <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Job Card 1 */}
                      <div className="bg-jp-bg-surface/80 rounded-xl p-5 border border-jp-success/30 relative overflow-hidden flex flex-col justify-between hover:border-jp-success/60 transition-colors cursor-default h-full">
                         <div className="absolute top-0 right-0 w-24 h-24 bg-jp-success/10 blur-xl"></div>
                         
                         <div className="relative z-10">
                           <div className="flex justify-between items-start mb-2">
                             <h4 className="text-[14px] font-bold text-jp-text-primary">Senior Frontend Engineer</h4>
                             <span className="text-[10px] font-bold text-jp-success-text bg-jp-success/10 px-2 py-0.5 rounded-full ring-1 ring-jp-success/20">98% MATCH</span>
                           </div>
                           <p className="text-[12px] text-jp-text-secondary mb-4">Stripe • Remote • $160k - $210k</p>
                           
                           <div className="flex flex-wrap gap-2">
                             <span className="text-[10px] bg-jp-bg-raised border border-jp-border px-2 py-1 rounded text-jp-text-muted">React</span>
                             <span className="text-[10px] bg-jp-bg-raised border border-jp-border px-2 py-1 rounded text-jp-text-muted">TypeScript</span>
                             <span className="text-[10px] bg-jp-bg-raised border border-jp-border px-2 py-1 rounded text-jp-text-muted">GraphQL</span>
                           </div>
                         </div>
                         
                         <div className="flex flex-wrap gap-2 relative z-10 mt-6 pt-4 border-t border-jp-border-subtle/50">
                           <button className="flex-1 bg-jp-accent/20 hover:bg-jp-accent/30 text-jp-accent-text border border-jp-accent/30 py-2 rounded-lg text-[11px] font-semibold transition-colors flex items-center justify-center gap-1.5 shadow-[0_0_10px_rgba(56,189,248,0.1)]">
                              <Icon name="description" className="text-[12px]" /> Tailor Resume
                           </button>
                           <button className="flex-1 bg-jp-success/20 hover:bg-jp-success/30 text-jp-success-text border border-jp-success/30 py-2 rounded-lg text-[11px] font-semibold transition-colors flex items-center justify-center gap-1.5 shadow-[0_0_10px_rgba(74,222,128,0.1)]">
                              <Icon name="send" className="text-[12px]" /> Auto-Apply
                           </button>
                         </div>
                      </div>
                      
                      {/* Job Card 2 */}
                      <div className="bg-jp-bg-surface/80 rounded-xl p-5 border border-jp-warning/30 relative overflow-hidden flex flex-col justify-between hover:border-jp-warning/60 transition-colors cursor-default h-full">
                         <div className="absolute top-0 right-0 w-24 h-24 bg-jp-warning/10 blur-xl"></div>
                         
                         <div className="relative z-10">
                           <div className="flex justify-between items-start mb-2">
                             <h4 className="text-[14px] font-bold text-jp-text-primary">React Native Developer</h4>
                             <span className="text-[10px] font-bold text-jp-warning-text bg-jp-warning/10 px-2 py-0.5 rounded-full ring-1 ring-jp-warning/20">85% MATCH</span>
                           </div>
                           <p className="text-[12px] text-jp-text-secondary mb-4">Airbnb • New York • $140k - $180k</p>
                           
                           <div className="flex flex-wrap gap-2">
                             <span className="text-[10px] bg-jp-bg-raised border border-jp-border px-2 py-1 rounded text-jp-text-muted">React Native</span>
                             <span className="text-[10px] bg-jp-error/10 border border-jp-error/30 text-jp-error px-2 py-1 rounded flex items-center gap-1">
                               <Icon name="warning" className="text-[10px]" /> Swift
                             </span>
                           </div>
                         </div>
                         
                         <div className="flex flex-wrap gap-2 relative z-10 mt-6 pt-4 border-t border-jp-border-subtle/50">
                           <button className="flex-1 bg-jp-bg-raised hover:bg-jp-bg-raised/80 text-jp-text-secondary border border-jp-border py-2 rounded-lg text-[11px] font-semibold transition-colors flex items-center justify-center gap-1.5">
                              <Icon name="school" className="text-[12px]" /> Learn Swift
                           </button>
                           <button className="flex-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 py-2 rounded-lg text-[11px] font-semibold transition-colors flex items-center justify-center gap-1.5 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
                              <Icon name="mic" className="text-[12px]" /> Prep Interview
                           </button>
                         </div>
                      </div>
                    </div>

                    {/* AI Analysis Side Panel (Fills the Void) */}
                    <div className="bg-jp-bg-surface/90 backdrop-blur-md rounded-xl p-5 border border-jp-accent/20 flex flex-col gap-4 relative overflow-hidden hidden lg:flex">
                      <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-jp-accent/15 blur-[60px] rounded-full"></div>
                      
                      <div className="flex items-center gap-2 border-b border-jp-border-subtle pb-3">
                        <Icon name="analytics" className="text-jp-accent text-[16px]" />
                        <h4 className="text-[13px] font-bold text-jp-text-primary">AI Match Analysis</h4>
                      </div>
                      
                      <div className="space-y-4 relative z-10">
                        {/* Progress bars */}
                        <div>
                          <div className="flex justify-between text-[11px] mb-1.5">
                            <span className="text-jp-text-secondary">Semantic Skill Match</span>
                            <span className="text-jp-success">98%</span>
                          </div>
                          <div className="h-1.5 w-full bg-jp-bg-raised rounded-full overflow-hidden">
                            <div className="h-full bg-jp-success w-[98%] shadow-[0_0_8px_var(--color-jp-success-glow)]"></div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-[11px] mb-1.5">
                            <span className="text-jp-text-secondary">Experience Level</span>
                            <span className="text-jp-accent">100%</span>
                          </div>
                          <div className="h-1.5 w-full bg-jp-bg-raised rounded-full overflow-hidden">
                            <div className="h-full bg-jp-accent w-[100%] shadow-[0_0_8px_var(--color-jp-accent-glow)]"></div>
                          </div>
                        </div>

                        {/* AI Insight Pill */}
                        <div className="mt-4 bg-jp-accent/10 border border-jp-accent/20 rounded-lg p-3 flex gap-2">
                          <Icon name="auto_awesome" className="text-jp-accent text-[14px] shrink-0 mt-0.5" />
                          <p className="text-[11px] text-jp-accent-text leading-relaxed">
                            Your deep experience in React and GraphQL makes you an exceptional fit for the Stripe role. Consider emphasizing your CI/CD pipeline work in the resume.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Supported Platforms Marquee ──────────────────────────── */}
        <section className="py-12 px-6 border-y border-jp-border-subtle bg-jp-bg-surface/30">
          <div className="max-w-6xl mx-auto flex flex-col items-center">
            <p className="text-[12px] font-semibold text-jp-text-tertiary uppercase tracking-widest mb-8">Works seamlessly with top job boards & ATS platforms</p>
            <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-60 grayscale filter contrast-125">
              <span className="text-[22px] font-bold tracking-tighter font-sans">LinkedIn</span>
              <span className="text-[22px] font-extrabold tracking-tight font-sans">indeed</span>
              <span className="text-[22px] font-bold font-serif">Greenhouse</span>
              <span className="text-[22px] font-black tracking-widest font-sans">workday.</span>
              <span className="text-[22px] font-medium tracking-wide font-sans">LEVER</span>
            </div>
          </div>
        </section>

        {/* ── Features Bento Box Grid ─────────────────────────────── */}
        <section id="features" className="py-32 px-6 relative">
          <div 
            className="absolute left-0 top-1/3 w-96 h-96 bg-jp-success/5 blur-[120px] pointer-events-none transition-transform duration-75 ease-out"
            style={{ transform: `translateY(${scrollY * 0.1}px)` }}
          ></div>
          
          <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-20">
              <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-jp-text-primary mb-6">Unfair Advantage.</h2>
              <p className="text-[18px] md:text-[20px] text-jp-text-secondary max-w-2xl mx-auto">Stop applying into the void. Use specialized AI agents to analyze, tailor, and guarantee your application gets seen.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              
              {/* Big Bento 1 */}
              <div className="md:col-span-2 bg-jp-bg-surface border border-jp-border-subtle rounded-3xl p-8 md:p-12 relative overflow-hidden group hover:border-jp-accent/30 transition-colors">
                <div className="absolute -right-20 -top-20 w-64 h-64 bg-jp-accent/10 blur-[80px] rounded-full group-hover:bg-jp-accent/20 transition-all duration-500"></div>
                <Icon name="radar" className="text-jp-accent text-[40px] mb-6 drop-shadow-[0_0_12px_var(--color-jp-accent-glow)]" />
                <h3 className="text-3xl font-bold text-jp-text-primary mb-4">Semantic Job Matching</h3>
                <p className="text-[16px] text-jp-text-secondary max-w-md leading-relaxed">
                  Our LangGraph-powered search agent crawls thousands of listings and semantically matches them against your exact resume, skipping the noise.
                </p>
              </div>

              {/* Small Bento 1 */}
              <div className="md:col-span-1 bg-jp-bg-surface border border-jp-border-subtle rounded-3xl p-8 relative overflow-hidden group hover:border-jp-success/30 transition-colors">
                <Icon name="fact_check" className="text-jp-success text-[32px] mb-6 drop-shadow-[0_0_12px_rgba(72,187,120,0.5)]" />
                <h3 className="text-xl font-bold text-jp-text-primary mb-3">ATS Score Prediction</h3>
                <p className="text-[14px] text-jp-text-secondary leading-relaxed">
                  Know your match percentage before you even click apply. Fix critical missing skills instantly.
                </p>
              </div>

              {/* Small Bento 2 */}
              <div className="md:col-span-1 bg-jp-bg-surface border border-jp-border-subtle rounded-3xl p-8 relative overflow-hidden group hover:border-blue-400/30 transition-colors">
                <Icon name="description" className="text-blue-400 text-[32px] mb-6 drop-shadow-[0_0_12px_rgba(96,165,250,0.5)]" />
                <h3 className="text-xl font-bold text-jp-text-primary mb-3">Auto-Tailored Resumes</h3>
                <p className="text-[14px] text-jp-text-secondary leading-relaxed">
                  Generate hyper-specific bullet points perfectly aligned with the target job description.
                </p>
              </div>

              {/* Big Bento 2 */}
              <div className="md:col-span-2 bg-jp-bg-surface border border-jp-border-subtle rounded-3xl p-8 md:p-12 relative overflow-hidden group hover:border-purple-400/30 transition-colors">
                 <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-purple-400/10 blur-[80px] rounded-full group-hover:bg-purple-400/20 transition-all duration-500"></div>
                <Icon name="insights" className="text-purple-400 text-[40px] mb-6 drop-shadow-[0_0_12px_rgba(167,139,250,0.5)]" />
                <h3 className="text-3xl font-bold text-jp-text-primary mb-4">Deep Career Intelligence</h3>
                <p className="text-[16px] text-jp-text-secondary max-w-md leading-relaxed">
                  Map out your career trajectory. Discover the exact certifications, projects, and skills you need to reach Staff/Principal levels.
                </p>
              </div>

            </div>
          </div>
        </section>

        {/* ── How It Works ───────────────────────────────── */}
        <section id="how-it-works" className="py-24 px-6 border-t border-jp-border-subtle bg-jp-bg-surface/30">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-jp-text-primary mb-4">How it works</h2>
              <p className="text-[16px] text-jp-text-secondary">Three steps to your next offer.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8 relative">
              {/* Connecting line for desktop */}
              <div className="hidden md:block absolute top-8 left-[15%] right-[15%] h-[1px] bg-gradient-to-r from-transparent via-jp-border-subtle to-transparent z-0"></div>
              
              {/* Step 1 */}
              <div className="flex flex-col items-center text-center relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-jp-bg-app border border-jp-border flex items-center justify-center mb-6 shadow-[0_0_15px_rgba(0,0,0,0.2)]">
                  <Icon name="upload_file" className="text-blue-400 text-[24px]" />
                </div>
                <h3 className="text-[16px] font-bold text-jp-text-primary mb-2">1. Upload your resume</h3>
                <p className="text-[14px] text-jp-text-secondary max-w-xs leading-relaxed">Drop your existing PDF. Our AI parses your entire career history instantly.</p>
              </div>

              {/* Step 2 */}
              <div className="flex flex-col items-center text-center relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-jp-bg-app border border-jp-accent/30 flex items-center justify-center mb-6 shadow-[0_0_20px_var(--color-jp-accent-glow)] relative">
                  <div className="absolute inset-0 bg-jp-accent/10 rounded-2xl animate-pulse"></div>
                  <Icon name="radar" className="text-jp-accent text-[24px] relative z-10" />
                </div>
                <h3 className="text-[16px] font-bold text-jp-text-primary mb-2">2. AI finds matches</h3>
                <p className="text-[14px] text-jp-text-secondary max-w-xs leading-relaxed">We scan thousands of listings and surface only the ones where you have a high match.</p>
              </div>

              {/* Step 3 */}
              <div className="flex flex-col items-center text-center relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-jp-bg-app border border-jp-border flex items-center justify-center mb-6 shadow-[0_0_15px_rgba(0,0,0,0.2)]">
                  <Icon name="auto_awesome" className="text-jp-success text-[24px]" />
                </div>
                <h3 className="text-[16px] font-bold text-jp-text-primary mb-2">3. Auto-tailor & apply</h3>
                <p className="text-[14px] text-jp-text-secondary max-w-xs leading-relaxed">One click rewrites your resume perfectly for the target ATS. Apply with confidence.</p>
              </div>
            </div>
          </div>
        </section>
        {/* ── Testimonials ───────────────────────────────── */}
        <section id="testimonials" className="py-24 px-6 border-t border-jp-border-subtle relative overflow-hidden">
          <div 
            className="absolute top-1/2 left-0 w-96 h-96 bg-blue-500/5 blur-[120px] pointer-events-none transition-transform duration-75 ease-out"
            style={{ transform: `translateY(${scrollY * 0.1}px)` }}
          ></div>
          <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-jp-text-primary mb-4">Don't just take our word for it</h2>
              <p className="text-[16px] text-jp-text-secondary">Join thousands of engineers landing their dream roles.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-jp-bg-surface border border-jp-border-subtle rounded-2xl p-6 hover:border-jp-border transition-colors">
                <div className="flex text-jp-accent mb-4"><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /></div>
                <p className="text-[14px] text-jp-text-primary mb-6 leading-relaxed">"JobPilot completely rewrote my resume for a Staff role at Stripe. I got the interview in 3 days after months of silence."</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-jp-accent flex items-center justify-center font-bold text-white text-[12px]">SD</div>
                  <div>
                    <p className="text-[13px] font-bold text-jp-text-primary">Sarah D.</p>
                    <p className="text-[11px] text-jp-text-tertiary">Staff Engineer</p>
                  </div>
                </div>
              </div>
              <div className="bg-jp-bg-surface border border-jp-border-subtle rounded-2xl p-6 hover:border-jp-border transition-colors">
                <div className="flex text-jp-accent mb-4"><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /></div>
                <p className="text-[14px] text-jp-text-primary mb-6 leading-relaxed">"The semantic matching is insane. It found niche roles I didn't even know existed and told me exactly why I was a 99% match."</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center font-bold text-white text-[12px]">MJ</div>
                  <div>
                    <p className="text-[13px] font-bold text-jp-text-primary">Michael J.</p>
                    <p className="text-[11px] text-jp-text-tertiary">Data Scientist</p>
                  </div>
                </div>
              </div>
              <div className="bg-jp-bg-surface border border-jp-border-subtle rounded-2xl p-6 hover:border-jp-border transition-colors">
                <div className="flex text-jp-accent mb-4"><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /><Icon name="star" fill className="text-[16px]" /></div>
                <p className="text-[14px] text-jp-text-primary mb-6 leading-relaxed">"I was skeptical of AI resume writers, but this one actually understands technical context. It's like having a Senior Manager review your CV."</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-jp-success to-emerald-500 flex items-center justify-center font-bold text-white text-[12px]">AK</div>
                  <div>
                    <p className="text-[13px] font-bold text-jp-text-primary">Alex K.</p>
                    <p className="text-[11px] text-jp-text-tertiary">DevOps Engineer</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pricing ───────────────────────────────── */}
        <section id="pricing" className="py-24 px-6 border-t border-jp-border-subtle bg-jp-bg-surface/30">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-jp-text-primary mb-4">Simple, transparent pricing</h2>
              <p className="text-[16px] text-jp-text-secondary">Invest in your career. Upgrade when you're ready.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {/* Free Tier */}
              <div className="bg-jp-bg-app border border-jp-border-subtle rounded-3xl p-8 flex flex-col hover:border-jp-border transition-colors">
                <h3 className="text-[20px] font-bold text-jp-text-primary mb-2">Starter</h3>
                <p className="text-[14px] text-jp-text-secondary mb-6">Perfect for trying out the platform.</p>
                <div className="mb-8">
                  <span className="text-4xl font-extrabold text-jp-text-primary">$0</span>
                  <span className="text-jp-text-secondary text-[14px]">/month</span>
                </div>
                <ul className="flex flex-col gap-4 mb-8 flex-1">
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-border" /> 5 AI Resume Tailors / mo</li>
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-border" /> Basic Job Search</li>
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-border" /> 1 ATS Scan / mo</li>
                </ul>
                <Link to="/auth" className="w-full py-3 rounded-xl bg-jp-bg-raised text-jp-text-primary font-bold text-center border border-jp-border hover:bg-jp-border-subtle transition-colors">Get Started Free</Link>
              </div>

              {/* Pro Tier */}
              <div className="bg-jp-bg-app border border-jp-accent/50 rounded-3xl p-8 flex flex-col relative shadow-[0_0_30px_var(--color-jp-accent-glow)]">
                <div className="absolute top-0 right-8 -translate-y-1/2 bg-gradient-to-r from-jp-accent to-blue-500 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">Most Popular</div>
                <h3 className="text-[20px] font-bold text-jp-text-primary mb-2">Pro</h3>
                <p className="text-[14px] text-jp-text-secondary mb-6">For serious job seekers who want an unfair advantage.</p>
                <div className="mb-8 h-[40px] flex items-center">
                  <span className="text-[28px] font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-jp-accent to-blue-400">Revealing Soon</span>
                </div>
                <ul className="flex flex-col gap-4 mb-8 flex-1">
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-accent" /> Unlimited AI Resume Tailors</li>
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-accent" /> Semantic Job Matching</li>
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-accent" /> Unlimited ATS Scans</li>
                  <li className="flex items-center gap-3 text-[14px] text-jp-text-primary"><Icon name="check_circle" className="text-jp-accent" /> Skill Gap Analysis</li>
                </ul>
                <button disabled className="w-full py-3 rounded-xl bg-gradient-to-r from-jp-accent to-blue-500 text-white font-bold text-center opacity-80 cursor-not-allowed">Join Waitlist</button>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}

export default LandingPage;
