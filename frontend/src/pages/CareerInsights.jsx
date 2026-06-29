import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/common/Toast';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';

export default function CareerInsights() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(true);
  const [activeRole, setActiveRole] = useState(null);
  const [hoveredDetail, setHoveredDetail] = useState(null);

  const fetchInsights = async () => {
    if (!token) return;
    setLoadingInsights(true);
    try {
      const res = await fetch('http://localhost:8000/profile/insights', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      } else {
        // Handle 404 NO INSIGHTS YET
        setInsights({ status: 'NO_INSIGHTS' });
      }
    } catch (err) {
      console.error("Error fetching insights:", err);
      toast.error("Failed to fetch insights.");
      setInsights({ status: 'NO_INSIGHTS' });
    } finally {
      setLoadingInsights(false);
    }
  };

  const generateInsights = async () => {
    if (!token) return;
    setLoadingInsights(true);
    try {
      const res = await fetch('http://localhost:8000/profile/insights/generate', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
        toast.success("AI career insights updated!");
      } else {
        const errData = await res.json();
        toast.error(errData.detail || "Failed to generate insights.");
      }
    } catch (err) {
      console.error("Error generating insights:", err);
      toast.error("Error connecting to server to generate insights.");
    } finally {
      setLoadingInsights(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [token]);

  // Determine state variables
  const completeness = insights?.profile_completeness || 0;
  const missingFields = insights?.missing_fields || [];
  
  // Extract nested insights data
  const marketIntelMap = (insights && insights.insights) ? insights.insights.market_intelligence : null;
  const status = insights ? insights.status : 'NO_INSIGHTS';
  const generatedAt = insights ? insights.generated_at : null;

  // Derive target roles and select active target role details
  const roles = marketIntelMap ? Object.keys(marketIntelMap) : [];
  const selectedRole = activeRole && roles.includes(activeRole) ? activeRole : roles[0];
  const marketIntel = marketIntelMap && selectedRole ? marketIntelMap[selectedRole] : null;
  const recResult = (insights && insights.insights && insights.insights.recommendations && selectedRole)
    ? insights.insights.recommendations[selectedRole]
    : null;

  const getMatchStyles = (status) => {
    switch (status) {
      case 'DEMONSTRATED':
        return {
          bgClass: 'bg-jp-success-muted/20 text-jp-success border-jp-success/30 hover:bg-jp-success-muted/30',
          dotClass: 'bg-jp-success',
          label: 'Demonstrated'
        };
      case 'CLAIMED':
        return {
          bgClass: 'bg-jp-warning-muted/20 text-jp-warning border-jp-warning/30 hover:bg-jp-warning-muted/30',
          dotClass: 'bg-jp-warning',
          label: 'Claimed'
        };
      case 'MISSING':
      default:
        return {
          bgClass: 'bg-jp-error-muted/20 text-jp-error border-jp-error/30 hover:bg-jp-error-muted/30',
          dotClass: 'bg-jp-error',
          label: 'Missing'
        };
    }
  };

  if (loadingInsights) {
    return (
      <AppShell breadcrumbs={[{ label: "Career Agent" }]}>
        <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh] space-y-6">
          <div className="relative w-20 h-20 flex items-center justify-center">
            <Icon name="progress_activity" className="text-[48px] text-jp-accent animate-spin" />
            <Icon name="auto_awesome" className="text-[20px] text-white absolute animate-pulse" />
          </div>
          <div className="text-center space-y-3 px-6">
            <p className="text-[16px] font-bold text-jp-text-primary">Agent analyzing market context...</p>
            <p className="text-[14px] text-jp-text-tertiary font-medium">
              Searching live hiring expectations and synthesizing level-aware recommendations.
            </p>
          </div>
        </div>
      </AppShell>
    );
  }

  if (status === 'NO_INSIGHTS') {
    return (
      <AppShell breadcrumbs={[{ label: "Career Agent" }]}>
        <div className="p-6 lg:p-10 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[50vh] animate-fade-in">
          <div className="w-20 h-20 rounded-full bg-jp-bg-raised border border-jp-border flex items-center justify-center text-jp-accent mb-6 shadow-sm">
            <Icon name="explore" className="text-[36px]" />
          </div>
          <h2 className="text-2xl font-bold text-jp-text-primary mb-3">Unlock Market Demands</h2>
          <p className="text-[15px] text-jp-text-secondary leading-relaxed max-w-md text-center mb-8">
            Complete your profile and run the AI Career Agent to discover how your skills stack up against live market trends.
          </p>
          <button
            onClick={generateInsights}
            className="px-6 py-3.5 jp-btn jp-btn-primary rounded-xl text-[15px] font-bold shadow-lg shadow-jp-accent/20"
          >
            <Icon name="auto_awesome" className="text-[20px]" />
            Generate Career Insights
          </button>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell breadcrumbs={[{ label: "Career Agent" }]}>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-8 animate-fade-in">
        
        {/* PAGE HEADER */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-jp-text-primary tracking-tight flex items-center gap-3">
              <Icon name="auto_awesome" className="text-jp-accent" />
              AI Career Agent
            </h1>
            <p className="text-[15px] text-jp-text-secondary mt-2">
              Deep market intelligence and actionable gap roadmaps tailored to your profile.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {generatedAt && (
              <span className="text-[12px] font-medium text-jp-text-muted bg-jp-bg-inset px-3 py-1.5 rounded-lg border border-jp-border-subtle">
                Synced: {new Date(generatedAt).toLocaleDateString()}
              </span>
            )}
            <button
              onClick={generateInsights}
              className="flex items-center gap-2 px-4 py-2 bg-jp-bg-surface hover:bg-jp-bg-inset text-jp-text-primary font-bold text-[13px] rounded-xl transition-colors border border-jp-border shadow-sm"
            >
              <Icon name="refresh" className="text-[16px]" /> Re-run Analysis
            </button>
          </div>
        </div>

        {/* STALE BANNER */}
        {status === 'STALE' && (
          <div className="flex items-center justify-between p-4 bg-jp-warning-muted/10 border border-jp-warning/30 rounded-xl shadow-sm">
            <div className="flex items-center gap-3 text-[14px] font-semibold text-jp-warning">
              <Icon name="info" className="text-[20px]" />
              Your profile has changed recently. These insights might be outdated.
            </div>
            <button
              onClick={generateInsights}
              className="px-4 py-2 bg-jp-warning hover:bg-jp-warning/90 text-[#0A0A0B] font-bold text-[13px] rounded-lg transition-colors flex items-center gap-1.5"
            >
              <Icon name="refresh" className="text-[16px]" />
              Update Now
            </button>
          </div>
        )}

        {/* TOP METRICS ROW: Focus on Profile Strength & Role Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Completeness Card */}
          <div className="col-span-1 p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm flex items-center gap-6">
            <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="48" cy="48" r="42" className="text-jp-bg-inset" stroke="currentColor" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="42"
                  className="text-jp-accent transition-all duration-700"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray="264"
                  strokeDashoffset={264 - (264 * completeness) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-[22px] font-bold text-jp-text-primary">{Math.round(completeness)}%</span>
              </div>
            </div>
            <div>
              <h3 className="text-[14px] font-bold text-jp-text-secondary uppercase tracking-wider mb-1">Profile Strength</h3>
              <p className="text-[15px] font-semibold text-jp-text-primary">
                {completeness >= 80 ? "Excellent Context" : "Needs Optimization"}
              </p>
              {missingFields.length > 0 && (
                <p className="text-[12px] text-jp-warning font-medium mt-1">Missing {missingFields.length} critical fields</p>
              )}
            </div>
          </div>

          {/* Analyzed Roles & Sources */}
          {marketIntel && (
            <div className="col-span-1 md:col-span-2 p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm flex flex-col justify-center">
              <h3 className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider mb-3">View Insights For:</h3>
              <div className="flex flex-wrap items-center gap-3">
                {roles.map((role) => (
                  <button
                    key={role}
                    onClick={() => setActiveRole(role)}
                    className={`px-5 py-2.5 text-[14px] font-bold rounded-xl border transition-all ${
                          selectedRole === role
                        ? 'bg-jp-accent text-white border-jp-accent shadow-lg shadow-jp-accent/20 scale-[1.02]'
                        : 'bg-jp-bg-inset text-jp-text-secondary border-jp-border-subtle hover:text-jp-text-primary hover:bg-jp-bg-raised'
                    }`}
                  >
                    {role}
                  </button>
                ))}
              </div>
              <div className="mt-4 flex items-center gap-2">
                <span className="text-[12px] font-medium text-jp-text-tertiary">Agent aggregated data from</span>
                <span className="px-2 py-0.5 bg-jp-bg-inset border border-jp-border-subtle rounded-md text-[12px] font-bold text-jp-text-secondary">
                  {marketIntel.analyzed_sources_count} industry sources
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 
            DYNAMIC CONTENT AREA
            Using 'key' forces React to re-render and re-trigger the CSS animation 
        */}
        {marketIntel && (
          <div key={selectedRole} className="animate-fade-in space-y-8">
            
            {/* STACKED SECTION 1: MARKET INTELLIGENCE */}
            <div className="space-y-6">
              <h2 className="text-[20px] font-bold text-jp-text-primary border-b border-jp-border-subtle pb-3">
                Market Intelligence
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div className="lg:col-span-2 space-y-6">
                  {/* Market Summary */}
                  <div className="p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm">
                    <h3 className="text-[15px] font-bold text-jp-text-primary mb-3 flex items-center gap-2">
                      <Icon name="monitoring" className="text-jp-accent text-[18px]" /> Market Summary
                    </h3>
                    <p className="text-[14px] leading-relaxed text-jp-text-secondary p-4 bg-jp-bg-inset rounded-xl border border-jp-border-subtle">
                      {marketIntel.market_summary}
                    </p>
                  </div>
                  
                  {/* Skill Legends */}
                  <div className="flex flex-wrap gap-6 px-2">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-jp-success shadow-[0_0_8px_rgba(34,197,94,0.5)]"></span>
                      <span className="text-[13px] font-semibold text-jp-text-primary">Demonstrated (Has Evidence)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-jp-warning shadow-[0_0_8px_rgba(245,158,11,0.5)]"></span>
                      <span className="text-[13px] font-semibold text-jp-text-primary">Claimed (No Evidence)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-jp-error shadow-[0_0_8px_rgba(239,68,68,0.5)]"></span>
                      <span className="text-[13px] font-semibold text-jp-text-primary">Missing from Profile</span>
                    </div>
                  </div>

                  {/* Skills Grid */}
                  <div className="p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm space-y-6">
                    <div className="space-y-4">
                      <h4 className="text-[13px] font-bold text-jp-text-primary uppercase tracking-wider flex items-center gap-2 border-b border-jp-border-subtle pb-2">
                        Must Have Skills
                      </h4>
                      <div className="flex flex-wrap gap-3">
                        {marketIntel.must_have_skills.map(skill => {
                          const styles = getMatchStyles(skill.match_status);
                          return (
                            <span 
                              key={skill.name} 
                              onMouseEnter={() => setHoveredDetail({ title: skill.name, label: styles.label, desc: skill.why_this_matters || 'Required skill expected by current job listings.', dotClass: styles.dotClass, demand: skill.demand_signal })}
                              onMouseLeave={() => setHoveredDetail(null)}
                              className={`border px-4 py-2 rounded-xl flex items-center gap-2 text-[13px] font-bold transition-colors cursor-help shadow-sm ${styles.bgClass}`}
                            >
                              <span className={`w-2 h-2 rounded-full shrink-0 ${styles.dotClass}`} />
                              <span>{skill.name}</span>
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    {marketIntel.emerging_skills && marketIntel.emerging_skills.length > 0 && (
                      <div className="space-y-4 pt-2">
                        <h4 className="text-[13px] font-bold text-jp-text-primary uppercase tracking-wider flex items-center gap-2 border-b border-jp-border-subtle pb-2">
                          Emerging Tech
                        </h4>
                        <div className="flex flex-wrap gap-3">
                          {marketIntel.emerging_skills.map(skill => {
                            const styles = getMatchStyles(skill.match_status);
                            return (
                              <span 
                                key={skill.name} 
                                onMouseEnter={() => setHoveredDetail({ title: skill.name, label: styles.label, desc: skill.why_this_matters || 'Emerging technology growing in job demand.', dotClass: styles.dotClass, demand: skill.demand_signal })}
                                onMouseLeave={() => setHoveredDetail(null)}
                                className={`border px-4 py-2 rounded-xl flex items-center gap-2 text-[13px] font-bold transition-colors cursor-help shadow-sm ${styles.bgClass}`}
                              >
                                <span className={`w-2 h-2 rounded-full shrink-0 ${styles.dotClass}`} />
                                <span>{skill.name}</span>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Inspector HUD on the right side of Market Intelligence */}
                <div className="lg:col-span-1">
                  <div className="p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm h-full flex flex-col sticky top-6">
                    <h3 className="text-[14px] font-bold text-jp-text-primary uppercase tracking-wider mb-4 border-b border-jp-border-subtle pb-2">
                      Inspector HUD
                    </h3>
                    
                    {hoveredDetail ? (
                      <div className="animate-fade-in space-y-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full shadow-[0_0_8px_currentColor] ${hoveredDetail.dotClass}`} />
                          <span className="text-[16px] font-bold text-jp-text-primary uppercase tracking-wide">{hoveredDetail.title}</span>
                        </div>
                        {hoveredDetail.demand && (
                          <span className="inline-block text-[11px] font-bold text-jp-text-secondary uppercase border border-jp-border-subtle bg-jp-bg-inset px-2.5 py-1 rounded-lg">
                            Demand: {hoveredDetail.demand}
                          </span>
                        )}
                        <p className="text-[14px] text-jp-text-secondary font-medium leading-relaxed bg-jp-bg-inset p-4 rounded-xl border border-jp-border-subtle">
                          {hoveredDetail.desc}
                        </p>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center text-center h-full text-jp-text-muted animate-fade-in gap-3 py-10">
                        <div className="w-14 h-14 rounded-full bg-jp-bg-inset border border-jp-border-subtle flex items-center justify-center shrink-0">
                          <Icon name="mouse" className="text-[28px]" />
                        </div>
                        <div>
                          <span className="text-[14px] font-bold text-jp-text-primary block mb-1">Hover over skills</span>
                          <span className="text-[13px] font-medium text-jp-text-tertiary px-4 block">Point at any skill block on the left to reveal deep market rationale.</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* STACKED SECTION 2: HIGH IMPACT ROADMAP */}
            {recResult && (
              <div className="space-y-6 pt-6">
                <h2 className="text-[20px] font-bold text-jp-text-primary border-b border-jp-border-subtle pb-3">
                  High Impact Roadmap
                </h2>

                {recResult.gap_analysis?.missing_skills?.length > 0 && (
                  <div className="p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm">
                    <span className="text-[13px] font-bold text-jp-error uppercase tracking-wider block mb-3">Critical Missing Gaps</span>
                    <div className="flex flex-wrap gap-2">
                      {recResult.gap_analysis.missing_skills.map(s => (
                        <span key={s} className="bg-jp-error-muted/10 text-jp-error text-[13px] font-bold border border-jp-error/20 px-3.5 py-1.5 rounded-lg flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-jp-error shadow-[0_0_8px_rgba(239,68,68,0.5)]" /> {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {recResult.recommendations?.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recResult.recommendations.map((rec, idx) => {
                      const leftBorderColor = rec.impact === 'HIGH' ? 'border-t-jp-success' :
                                              rec.impact === 'MEDIUM' ? 'border-t-indigo-500' : 'border-t-jp-text-muted';
                      return (
                        <div key={idx} className={`p-6 border border-jp-border border-t-[4px] ${leftBorderColor} rounded-2xl bg-jp-bg-surface shadow-sm space-y-4 flex flex-col`}>
                          <div className="flex items-start justify-between gap-4">
                            <h4 className="text-[16px] font-bold text-jp-text-primary leading-snug">
                              {rec.title}
                            </h4>
                            <span className={`inline-block text-[10px] font-bold px-2 py-1 rounded border uppercase shrink-0 ${
                              rec.impact === 'HIGH' ? 'bg-jp-success-muted/10 border-jp-success/20 text-jp-success' :
                              rec.impact === 'MEDIUM' ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400' : 'bg-jp-bg-app border-jp-border text-jp-text-secondary'
                            }`}>
                              Impact: {rec.impact}
                            </span>
                          </div>
                          <div className="text-[14px] text-jp-text-secondary leading-relaxed bg-jp-bg-inset p-4 rounded-xl border border-jp-border-subtle flex-1">
                            {rec.action}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="p-6 rounded-2xl border border-jp-border bg-jp-bg-surface shadow-sm">
                    <p className="text-[14px] text-jp-text-tertiary">No action items generated yet.</p>
                  </div>
                )}
              </div>
            )}

          </div>
        )}

      </div>
    </AppShell>
  );
}
