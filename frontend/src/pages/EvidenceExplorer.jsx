import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/common/Toast';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';

export default function EvidenceExplorer() {
  const { token } = useAuth();
  const toast = useToast();

  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchInsights = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/profile/insights', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      } else {
        setInsights(null);
      }
    } catch (err) {
      console.error("Error fetching insights:", err);
      toast.error("Failed to fetch insights.");
      setInsights(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [token]);

  if (loading) {
    return (
      <AppShell breadcrumbs={[{ label: "Candidate Knowledge Engine" }]}>
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Icon name="memory" className="text-[48px] text-jp-accent animate-pulse" />
          <p className="mt-4 text-[14px] text-jp-text-secondary font-mono">Querying intelligence graph...</p>
        </div>
      </AppShell>
    );
  }

  if (!insights || insights.status === 'NO_INSIGHTS') {
    return (
      <AppShell breadcrumbs={[{ label: "Candidate Knowledge Engine" }]}>
        <div className="p-8 max-w-5xl mx-auto flex flex-col items-center justify-center min-h-[50vh]">
          <Icon name="data_object" className="text-[48px] text-jp-text-muted mb-4" />
          <h2 className="text-xl font-bold text-jp-text-primary mb-2">No Data Found</h2>
          <p className="text-[14px] text-jp-text-secondary text-center max-w-md">
            The Candidate Knowledge Engine has not processed your profile yet.
          </p>
        </div>
      </AppShell>
    );
  }

  const {
    evidence_engine: ck = {},
    project_intelligence: projects = [],
    market_intelligence: market = {},
    recommendations: recs = {}
  } = insights.insights || {};

  const identity = ck.candidate_identity || {};
  const evaluations = ck.evidence_report?.evaluations || {};

  const renderBadge = (text, type = 'default') => {
    const colors = {
      default: 'bg-jp-bg-inset border-jp-border-subtle text-jp-text-primary',
      success: 'bg-jp-success/10 border-jp-success/20 text-jp-success',
      warning: 'bg-jp-warning/10 border-jp-warning/20 text-jp-warning',
      accent: 'bg-jp-accent/10 border-jp-accent/20 text-jp-accent'
    };
    return (
      <span className={`px-2 py-1 border rounded text-[12px] font-medium ${colors[type] || colors.default}`}>
        {text}
      </span>
    );
  };

  return (
    <AppShell breadcrumbs={[{ label: "Knowledge Engine Results" }]}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-8 font-sans">
        
        {/* HEADER */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-jp-border-subtle pb-6">
          <div>
            <h1 className="text-2xl font-bold text-jp-text-primary tracking-tight flex items-center gap-3">
              <Icon name="psychology" className="text-jp-accent" />
              Candidate Knowledge Engine Output
            </h1>
            <p className="text-[14px] text-jp-text-secondary mt-2">
              Structured representation of candidate data across multiple layers of intelligence.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[12px] px-3 py-1 bg-jp-bg-inset border border-jp-border-subtle rounded-md text-jp-text-primary">
              Status: <span className="font-bold text-jp-success">{insights.status}</span>
            </span>
          </div>
        </div>

        {/* IDENTITY & MATURITY SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-jp-bg-surface border border-jp-border rounded-xl p-6 space-y-4 shadow-sm">
            <h2 className="text-lg font-bold text-jp-text-primary border-b border-jp-border-subtle pb-2 flex items-center gap-2">
              <Icon name="fingerprint" className="text-jp-accent text-[20px]" /> Candidate Identity
            </h2>
            
            <div className="space-y-4 text-[14px]">
              <div>
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Primary Specialization</span>
                <div className="font-bold text-jp-text-primary">{identity.primary_specialization || 'N/A'}</div>
              </div>

              <div>
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Secondary Specializations</span>
                <div className="flex flex-wrap gap-2">
                  {identity.secondary_specializations?.map((s, i) => <span key={i}>{renderBadge(s)}</span>)}
                </div>
              </div>

              <div>
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Strongest Capabilities</span>
                <div className="flex flex-wrap gap-2">
                  {identity.strongest_capabilities?.map((c, i) => <span key={i}>{renderBadge(c, 'accent')}</span>)}
                </div>
              </div>

              <div>
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Tech Stack</span>
                <div className="flex flex-wrap gap-2">
                  {identity.primary_technology_stack?.map((t, i) => <span key={i}>{renderBadge(t, 'success')}</span>)}
                </div>
              </div>
              
              <div>
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Recruiter Summary</span>
                <p className="text-jp-text-secondary leading-relaxed">{identity.recruiter_summary}</p>
              </div>
            </div>
          </div>

          <div className="bg-jp-bg-surface border border-jp-border rounded-xl p-6 space-y-4 shadow-sm">
            <h2 className="text-lg font-bold text-jp-text-primary border-b border-jp-border-subtle pb-2 flex items-center gap-2">
              <Icon name="analytics" className="text-jp-warning text-[20px]" /> Maturity & Level
            </h2>
            
            <div className="grid grid-cols-2 gap-6 text-[14px]">
              <div className="bg-jp-bg-inset p-4 rounded-lg border border-jp-border-subtle">
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Calculated Level</span>
                <div className="text-xl font-bold text-jp-text-primary">{ck.candidate_level?.title || 'Unknown'}</div>
                <div className="text-[12px] text-jp-text-secondary mt-1">{ck.candidate_level?.total_months_experience || 0} months exp</div>
              </div>

              <div className="bg-jp-bg-inset p-4 rounded-lg border border-jp-border-subtle">
                <span className="block text-[11px] uppercase tracking-wider text-jp-text-muted mb-1">Projects</span>
                <div className="text-xl font-bold text-jp-text-primary">{ck.candidate_maturity?.project_count || 0}</div>
              </div>
            </div>

            <div className="mt-4">
               <h3 className="text-[13px] font-bold text-jp-text-primary mb-2">Overall Strengths</h3>
               <ul className="list-disc list-inside text-[13px] text-jp-text-secondary space-y-1">
                 {ck.evidence_report?.overall_strengths?.map((s, i) => <li key={i}>{s}</li>)}
               </ul>
            </div>

            <div className="mt-4">
               <h3 className="text-[13px] font-bold text-jp-text-primary mb-2">Overall Weaknesses</h3>
               <ul className="list-disc list-inside text-[13px] text-jp-text-secondary space-y-1">
                 {ck.evidence_report?.overall_weaknesses?.map((w, i) => <li key={i}>{w}</li>)}
               </ul>
            </div>
          </div>
        </div>

        {/* EVALUATIONS (EVIDENCE REPORT) */}
        <div className="bg-jp-bg-surface border border-jp-border rounded-xl p-6 shadow-sm overflow-hidden">
          <h2 className="text-lg font-bold text-jp-text-primary border-b border-jp-border-subtle pb-2 mb-4 flex items-center gap-2">
            <Icon name="fact_check" className="text-jp-success text-[20px]" /> Skill Evaluations
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-[13px] text-left border-collapse">
              <thead>
                <tr className="bg-jp-bg-inset text-jp-text-muted uppercase tracking-wider text-[11px]">
                  <th className="p-3 font-medium">Skill / Capability</th>
                  <th className="p-3 font-medium text-center">Category</th>
                  <th className="p-3 font-medium text-center">Confidence</th>
                  <th className="p-3 font-medium text-center">Status</th>
                  <th className="p-3 font-medium">Reasoning</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-jp-border-subtle">
                {Object.values(evaluations).map((ev, i) => (
                  <tr key={i} className="hover:bg-jp-bg-inset transition-colors">
                    <td className="p-3 font-bold text-jp-text-primary whitespace-nowrap">{ev.name}</td>
                    <td className="p-3 text-center">{renderBadge(ev.category)}</td>
                    <td className="p-3 text-center">
                      <span className={`font-bold ${ev.confidence_score >= 80 ? 'text-jp-success' : ev.confidence_score >= 50 ? 'text-jp-warning' : 'text-jp-error'}`}>
                        {ev.confidence_score}%
                      </span>
                    </td>
                    <td className="p-3 text-center">
                      {renderBadge(ev.evidence_status, ev.evidence_status === 'Demonstrated' ? 'success' : 'warning')}
                    </td>
                    <td className="p-3 text-jp-text-secondary text-[12px]">{ev.reasoning}</td>
                  </tr>
                ))}
                {Object.keys(evaluations).length === 0 && (
                  <tr>
                    <td colSpan="5" className="p-6 text-center text-jp-text-muted italic">No evaluations generated.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* MARKET INTELLIGENCE & RECOMMENDATIONS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
           <div className="bg-jp-bg-surface border border-jp-border rounded-xl p-6 space-y-4 shadow-sm">
             <h2 className="text-lg font-bold text-jp-text-primary border-b border-jp-border-subtle pb-2 flex items-center gap-2">
               <Icon name="trending_up" className="text-jp-accent text-[20px]" /> Market Intelligence
             </h2>
             {Object.keys(market).length > 0 ? (
               <div className="space-y-4">
                 {Object.entries(market).map(([role, intel]) => (
                   <div key={role} className="border border-jp-border-subtle rounded-lg p-4">
                     <h3 className="font-bold text-jp-text-primary text-[15px] mb-2">{role}</h3>
                     <p className="text-[13px] text-jp-text-secondary mb-3">{intel.market_summary}</p>
                     
                     <div className="space-y-2 text-[12px]">
                       <div>
                         <span className="font-bold text-jp-text-primary mr-2">Must-Haves:</span>
                         {intel.must_have_skills?.map((s, i) => <span key={i} className="text-jp-text-secondary mr-2">{s.name}</span>)}
                       </div>
                       <div>
                         <span className="font-bold text-jp-text-primary mr-2">Emerging:</span>
                         {intel.emerging_skills?.map((s, i) => <span key={i} className="text-jp-text-secondary mr-2">{s.name}</span>)}
                       </div>
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
               <div className="text-[13px] text-jp-text-muted italic">No market intelligence available.</div>
             )}
           </div>

           <div className="bg-jp-bg-surface border border-jp-border rounded-xl p-6 space-y-4 shadow-sm">
             <h2 className="text-lg font-bold text-jp-text-primary border-b border-jp-border-subtle pb-2 flex items-center gap-2">
               <Icon name="lightbulb" className="text-jp-warning text-[20px]" /> AI Recommendations
             </h2>
             {Object.keys(recs).length > 0 ? (
               <div className="space-y-4">
                 {Object.entries(recs).map(([role, r]) => (
                   <div key={role} className="border border-jp-border-subtle rounded-lg p-4">
                     <div className="flex justify-between items-start mb-2">
                       <h3 className="font-bold text-jp-text-primary text-[15px]">{role}</h3>
                       {renderBadge(`${r.match_score || 0}% Match`, r.match_score >= 80 ? 'success' : 'warning')}
                     </div>
                     <p className="text-[13px] text-jp-text-secondary mb-3">{r.verdict}</p>
                     
                     {r.critical_gaps?.length > 0 && (
                       <div className="text-[12px]">
                         <span className="block font-bold text-jp-error mb-1">Critical Gaps:</span>
                         <ul className="list-disc list-inside text-jp-text-secondary space-y-1">
                           {r.critical_gaps.map((g, i) => <li key={i}>{g.name}</li>)}
                         </ul>
                       </div>
                     )}
                   </div>
                 ))}
               </div>
             ) : (
               <div className="text-[13px] text-jp-text-muted italic">No recommendations available.</div>
             )}
           </div>
        </div>

      </div>
    </AppShell>
  );
}
