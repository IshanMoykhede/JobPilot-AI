import React, { useState } from 'react';
import Icon from '../common/Icon';

export default function AIInsightsPanel({
  profileData,
  strengthScore,
  triggerToast,
  setProfileExists,
  setActiveStep,
  insights,
  loadingInsights,
  refetchInsights,
  generateInsights
}) {
  // Determine state variables
  const completeness = insights ? insights.profile_completeness : strengthScore;
  const missingFields = insights ? insights.missing_fields : [];
  
  // Extract nested insights data
  const marketIntelMap = (insights && insights.insights) ? insights.insights.market_intelligence : null;
  const status = insights ? insights.status : 'NO_INSIGHTS';
  const generatedAt = insights ? insights.generated_at : null;

  // Active role tab state for market expectations
  const [activeRole, setActiveRole] = useState(null);

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
          bgClass: 'bg-emerald-50/80 text-emerald-800 border-emerald-200',
          dotClass: 'bg-emerald-500',
          label: 'Demonstrated'
        };
      case 'CLAIMED':
        return {
          bgClass: 'bg-amber-50/80 text-amber-800 border-amber-200',
          dotClass: 'bg-amber-500',
          label: 'Claimed'
        };
      case 'MISSING':
      default:
        return {
          bgClass: 'bg-rose-50/30 text-rose-800 border-rose-200',
          dotClass: 'bg-rose-400',
          label: 'Missing'
        };
    }
  };

  return (
    <aside className="hidden lg:flex flex-col w-80 h-full border-l bg-white p-6 shrink-0 overflow-y-auto" style={{ borderColor: "var(--color-outline-variant)" }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-[20px] font-semibold text-on-surface">AI Insights & Action</h2>
        {refetchInsights && (
          <button 
            onClick={() => {
              refetchInsights();
              triggerToast("Syncing career insights...");
            }}
            disabled={loadingInsights}
            className="p-1.5 hover:bg-secondary-container rounded-lg text-primary transition-colors disabled:opacity-50"
            title="Sync insights status"
          >
            <Icon name="sync" className={`text-[18px] ${loadingInsights ? 'animate-spin' : ''}`} />
          </button>
        )}
      </div>

      {loadingInsights ? (
        /* LOADING STATE */
        <div className="flex-1 flex flex-col items-center justify-center space-y-4">
          <div className="relative w-16 h-16 flex items-center justify-center">
            <Icon name="progress_activity" className="text-[40px] text-primary animate-spin" />
            <Icon name="auto_awesome" className="text-[18px] text-secondary absolute animate-pulse" />
          </div>
          <div className="text-center space-y-1 px-4">
            <p className="text-[13px] font-bold text-on-surface">Career Intelligence Agent at work...</p>
            <p className="text-[11px] text-outline leading-relaxed">
              Searching live hiring expectations and synthesizing level-aware recommendations. This may take 15-20 seconds.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          
          {/* STALE STATE WARNING BANNER */}
          {status === 'STALE' && (
            <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 text-amber-900 space-y-3 animate-fade-in">
              <div className="flex gap-2 items-start text-[11px] font-bold uppercase tracking-wider text-amber-800">
                <Icon name="change_circle" className="text-[16px] text-amber-700" fill />
                Profile Changes Detected
              </div>
              <p className="text-[11px] text-amber-800 leading-normal font-medium">
                You saved new profile details. Run the career agent to align recommendations with your updated profile.
              </p>
              <button
                onClick={generateInsights}
                className="w-full py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-[11px] rounded-lg shadow-sm transition-all hover:scale-[1.01] flex items-center justify-center gap-1.5"
              >
                <Icon name="auto_awesome" className="text-[13px]" />
                Update AI Insights
              </button>
            </div>
          )}

          {/* Profile Strength/Completeness Gauge */}
          <div className="text-center p-6 rounded-2xl border bg-[#fcfdff]" style={{ borderColor: "rgba(195,197,217,0.4)" }}>
            <div className="mx-auto mb-4 flex justify-center">
              <div className="relative w-32 h-32 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="64" cy="64" r="56" className="text-[#f1f3f9]" stroke="currentColor" strokeWidth="8" fill="none" />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    className="text-primary transition-all duration-700"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray="351.8"
                    strokeDashoffset={351.8 - (351.8 * completeness) / 100}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-[24px] font-extrabold text-primary">{Math.round(completeness)}%</span>
                  <span className="text-[10px] text-outline font-bold uppercase tracking-wider">Completeness</span>
                </div>
              </div>
            </div>
            <p className="text-[14px] font-bold text-on-surface">
              {completeness === 100
                ? "Profile Fully Completed!"
                : completeness >= 70
                ? "Good Profile Depth"
                : "Needs Profile Optimization"}
            </p>
            <p className="text-[12px] text-outline mt-1 leading-normal">
              {completeness === 100
                ? "Perfect context alignment for matched job searches."
                : "Complete missing details to get the most accurate AI suggestions."}
            </p>
          </div>

          {/* Missing Fields Warnings */}
          {missingFields && missingFields.length > 0 && (
            <div className="p-4 border border-orange-200 bg-orange-50/50 rounded-xl space-y-2">
              <div className="flex items-center gap-1.5 text-orange-700 font-bold text-[11px] uppercase tracking-wider">
                <Icon name="warning" className="text-[15px] text-orange-600" fill /> Missing Fields
              </div>
              <p className="text-[11px] text-outline leading-tight font-medium">
                Fill these fields to optimize matching:
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {missingFields.map((field) => (
                  <span key={field} className="bg-orange-100/60 text-orange-800 text-[10px] font-bold px-2 py-0.5 rounded">
                    {field}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* NO INSIGHTS / COLD START STATE */}
          {status === 'NO_INSIGHTS' && (
            <div className="p-5 rounded-2xl border text-center space-y-4 shadow-sm animate-fade-in" style={{
              background: 'linear-gradient(135deg, rgba(103, 80, 164, 0.08), rgba(98, 91, 113, 0.08))',
              borderColor: 'var(--color-primary-container)'
            }}>
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <Icon name="explore" className="text-[24px]" />
              </div>
              <div className="space-y-1">
                <h3 className="text-[14px] font-bold text-on-surface">Unlock Career Intelligence</h3>
                <p className="text-[11px] text-outline leading-normal font-medium">
                  Discover how your profile compares against live market trends. Run the agent to fetch insights for your preferred roles.
                </p>
              </div>
              <button
                onClick={generateInsights}
                className="w-full py-2.5 px-4 bg-primary hover:bg-primary/95 text-white font-bold text-[13px] rounded-xl flex items-center justify-center gap-2 shadow transition-all hover:scale-[1.01]"
              >
                <Icon name="auto_awesome" className="text-[16px]" />
                Generate AI Insights
              </button>
            </div>
          )}

          {/* ACTIVE STATE (COMPLETED OR STALE) */}
          {(status === 'COMPLETED' || status === 'STALE') && (
            <>
              {/* Market Intelligence Analysis */}
              {marketIntel && (
                <div className="p-4 border border-[#e3e6fc] bg-[#fafbff] rounded-xl space-y-3">
                  <div className="flex items-center gap-1.5 text-primary font-bold text-[11px] uppercase tracking-wider">
                    <Icon name="monitoring" className="text-[15px]" fill /> Live Market Demands
                  </div>

                  {/* Target Role Tab Selectors */}
                  {roles.length > 1 && (
                    <div className="flex flex-wrap gap-1.5 mb-2 border-b pb-2 border-outline-variant/30">
                      {roles.map((role) => (
                        <button
                          key={role}
                          onClick={() => setActiveRole(role)}
                          className={`px-2.5 py-1 text-[10px] font-bold rounded-full border transition-all ${
                            selectedRole === role
                              ? 'bg-primary text-white border-primary shadow-sm'
                              : 'bg-white text-on-surface border-outline-variant hover:bg-surface-container-low'
                          }`}
                        >
                          {role}
                        </button>
                      ))}
                    </div>
                  )}

                  <div className="space-y-3 pt-1">
                    <div>
                      <span className="text-[12px] font-extrabold text-on-surface block mb-1">
                        {marketIntel.role_name}
                      </span>
                      <div className="flex flex-col gap-1.5 mb-2.5">
                        <div className="flex flex-wrap gap-1.5">
                          <span className="bg-primary/10 text-primary text-[9px] font-bold px-2 py-0.5 rounded">
                            Sources Analysed: {marketIntel.analyzed_sources_count}
                          </span>
                        </div>
                        {marketIntel.source_breakdown && (
                          <div className="text-[10px] text-outline font-medium flex flex-wrap gap-x-2 gap-y-0.5 pl-0.5">
                            {Object.entries(marketIntel.source_breakdown).map(([platform, count]) => {
                              if (count === 0) return null;
                              return (
                                <span key={platform} className="whitespace-nowrap">
                                  {platform}: <strong className="text-on-surface">{count}</strong>
                                </span>
                              );
                            })}
                          </div>
                        )}
                      </div>
                      <p className="text-[12px] leading-relaxed text-on-surface-variant bg-surface-container-lowest p-2.5 rounded-lg border border-outline-variant/30 font-medium">
                        {marketIntel.market_summary}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-[10px] font-bold text-outline uppercase tracking-wider">Must Have Skills</h4>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {marketIntel.must_have_skills.slice(0, 5).map(skill => {
                          const styles = getMatchStyles(skill.match_status);
                          return (
                            <span 
                              key={skill.name} 
                              title={`${skill.name} (${styles.label}) • ${skill.why_this_matters || 'Market expectation'}`}
                              className={`border px-2 py-0.5 rounded-full flex items-center gap-1.5 text-[10px] font-semibold transition-all hover:scale-[1.02] cursor-help ${styles.bgClass}`}
                            >
                              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${styles.dotClass}`} />
                              <span>{skill.name}</span>
                              <span className="text-[8px] opacity-75 font-extrabold uppercase">({skill.demand_signal})</span>
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    {marketIntel.strong_advantage_skills && marketIntel.strong_advantage_skills.length > 0 && (
                      <div>
                        <h4 className="text-[10px] font-bold text-outline uppercase tracking-wider">Strong Advantage</h4>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {marketIntel.strong_advantage_skills.slice(0, 5).map(skill => {
                            const styles = getMatchStyles(skill.match_status);
                            return (
                              <span 
                                key={skill.name} 
                                title={`${skill.name} (${styles.label}) • ${skill.why_this_matters || 'Market expectation'}`}
                                className={`border px-2 py-0.5 rounded-full flex items-center gap-1.5 text-[10px] font-semibold transition-all hover:scale-[1.02] cursor-help ${styles.bgClass}`}
                              >
                                <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${styles.dotClass}`} />
                                <span>{skill.name}</span>
                                <span className="text-[8px] opacity-75 font-extrabold uppercase">({skill.demand_signal})</span>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {marketIntel.emerging_skills && marketIntel.emerging_skills.length > 0 && (
                      <div>
                        <h4 className="text-[10px] font-bold text-outline uppercase tracking-wider">Emerging Tech</h4>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {marketIntel.emerging_skills.slice(0, 5).map(skill => {
                            const styles = getMatchStyles(skill.match_status);
                            return (
                              <span 
                                key={skill.name} 
                                title={`${skill.name} (${styles.label}) • ${skill.why_this_matters || 'Market expectation'}`}
                                className={`border px-2 py-0.5 rounded-full flex items-center gap-1.5 text-[10px] font-semibold transition-all hover:scale-[1.02] cursor-help ${styles.bgClass}`}
                              >
                                <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${styles.dotClass}`} />
                                <span>{skill.name}</span>
                                <span className="text-[8px] opacity-75 font-extrabold uppercase">({skill.demand_signal})</span>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    <div>
                      <h4 className="text-[10px] font-bold text-outline uppercase tracking-wider">Common Tools</h4>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {marketIntel.common_tools.slice(0, 5).map(tool => {
                          const styles = getMatchStyles(tool.match_status);
                          return (
                            <span 
                              key={tool.name} 
                              title={`${tool.name} (${styles.label}) • ${tool.why_this_matters || 'Market expectation'}`}
                              className={`border px-2 py-0.5 rounded-full flex items-center gap-1.5 text-[10px] font-semibold transition-all hover:scale-[1.02] cursor-help ${styles.bgClass}`}
                            >
                              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${styles.dotClass}`} />
                              <span>{tool.name}</span>
                              <span className="text-[8px] opacity-75 font-extrabold uppercase">({tool.demand_signal})</span>
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    {marketIntel.citations && marketIntel.citations.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-outline-variant/30">
                        <details className="group">
                          <summary className="text-[10px] font-bold text-primary uppercase tracking-wider cursor-pointer list-none flex items-center gap-1 hover:text-primary-dark">
                            <Icon name="info" className="text-[14px]" fill />
                            <span>View Source Postings ({marketIntel.citations.length})</span>
                            <Icon name="expand_more" className="text-[14px] group-open:rotate-180 transition-transform" />
                          </summary>
                          <ul className="mt-2 space-y-1.5 pl-2 max-h-32 overflow-y-auto">
                            {marketIntel.citations.map((cit, idx) => (
                              <li key={idx} className="text-[11px] truncate">
                                <a href={cit.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium">
                                  {idx + 1}. {cit.title}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Gap Analysis & Actionable Recommendations */}
              {recResult ? (
                <div className="space-y-5">
                  {/* Factual Gaps */}
                  <div className="p-4 border border-outline-variant/50 rounded-xl bg-surface-container-lowest space-y-3">
                    <div className="flex justify-between items-center border-b pb-2 border-outline-variant/30">
                      <h3 className="text-[11px] font-bold text-outline uppercase tracking-wider flex items-center gap-1.5">
                        <Icon name="analytics" className="text-[15px] text-primary" fill /> Profile Gap Analysis
                      </h3>
                      {status === 'STALE' && (
                        <span className="text-[9px] font-bold text-amber-700 bg-amber-100 px-1.5 py-0.2 rounded uppercase">
                          Stale
                        </span>
                      )}
                    </div>
                    
                    {/* Strengths */}
                    {recResult.gap_analysis?.strengths?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block mb-1">Your Strengths</span>
                        <div className="flex flex-wrap gap-1">
                          {recResult.gap_analysis.strengths.map(s => (
                            <span key={s} className="bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Weak Evidence */}
                    {recResult.gap_analysis?.weak_evidence?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider block mb-1">Weak Evidence</span>
                        <div className="flex flex-wrap gap-1">
                          {recResult.gap_analysis.weak_evidence.map(s => (
                            <span key={s} className="bg-amber-50 text-amber-700 text-[10px] font-semibold border border-amber-100 px-2 py-0.5 rounded-full flex items-center gap-1" title="Skill is claimed in profile but lacks verified project/work evidence.">
                              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {recResult.gap_analysis?.missing_skills?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-rose-800 uppercase tracking-wider block mb-1">Missing Gaps</span>
                        <div className="flex flex-wrap gap-1">
                          {recResult.gap_analysis.missing_skills.map(s => (
                            <span key={s} className="bg-rose-50 text-rose-700 text-[10px] font-semibold border border-rose-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0" />
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actionable Project Recommendations */}
                  <div className="space-y-3">
                    <h3 className="text-[11px] font-bold text-outline uppercase tracking-wider flex items-center gap-1.5">
                      <Icon name="auto_awesome" className="text-[15px] text-primary" fill /> Highest Impact Actions
                    </h3>
                    
                    {recResult.recommendations?.length > 0 ? (
                      <div className="space-y-4">
                        {recResult.recommendations.map((rec, idx) => (
                          <div key={idx} className="p-4 border border-outline-variant/60 rounded-xl bg-white space-y-2.5 shadow-sm transition-all hover:shadow-md">
                            <div className="flex justify-between items-start gap-2">
                              <h4 className="text-[13px] font-extrabold text-on-surface leading-snug">
                                {idx + 1}. {rec.title}
                              </h4>
                            </div>
                            
                            <div className="flex flex-wrap gap-1.5 pt-0.5">
                              <span className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase ${
                                rec.impact === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                                rec.impact === 'MEDIUM' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                              }`}>
                                Impact: {rec.impact}
                              </span>
                              <span className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase ${
                                rec.effort === 'HIGH' ? 'bg-rose-100 text-rose-800' :
                                rec.effort === 'MEDIUM' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                              }`}>
                                Effort: {rec.effort}
                              </span>
                            </div>

                            <p className="text-[11px] text-outline leading-relaxed italic">
                              <strong>Why:</strong> {rec.reason}
                            </p>

                            <p className="text-[12px] text-on-surface-variant leading-relaxed bg-[#fbfbfe] p-2.5 rounded-lg border border-primary/5 font-medium">
                              <strong>Action:</strong> {rec.action}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[12px] text-outline italic">No recommendations found.</p>
                    )}
                  </div>
                </div>
              ) : (
                /* Fallback layout in case data is empty or old string list format */
                <div className="space-y-3 p-4 border border-outline-variant/50 rounded-xl bg-surface-container-lowest">
                  <div className="flex justify-between items-center">
                    <h3 className="text-[11px] font-bold text-outline uppercase tracking-wider flex items-center gap-1.5">
                      <Icon name="lightbulb" className="text-[15px] text-primary" fill /> AI Coaching Tips
                    </h3>
                  </div>
                  <p className="text-[12px] text-outline italic">Complete your profile and run analysis to generate custom recommendations.</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-2">
                <button
                  onClick={generateInsights}
                  className="w-full py-2.5 bg-primary/5 hover:bg-primary/10 text-primary font-bold text-[12px] rounded-xl transition-colors border border-primary/15 flex items-center justify-center gap-2"
                >
                  <Icon name="refresh" className="text-[15px]" />
                  Re-Run Career Analysis
                </button>
              </div>

            </>
          )}

          {/* Active Resume Context Details */}
          <div className="p-4 border border-outline-variant/60 rounded-xl bg-surface-container-lowest space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-[11px] font-bold text-outline uppercase tracking-wider">Active Resume Context</span>
              <span className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-0.5 rounded">PDF</span>
            </div>
            <div className="flex items-center gap-3 bg-[#f8f9fc] p-2.5 rounded-lg border border-outline-variant/30">
              <Icon name="picture_as_pdf" className="text-red-500 text-[28px]" fill />
              <div className="overflow-hidden">
                <p className="text-[12px] font-bold text-on-surface truncate">
                  {profileData.resume_metadata.file_name || "Extracted_Document.pdf"}
                </p>
                <p className="text-[10px] text-outline">
                  Uploaded {profileData.resume_metadata.uploaded_at ? new Date(profileData.resume_metadata.uploaded_at).toLocaleDateString() : "recently"}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                if (window.confirm("Replacing the resume file will overwrite your existing profile details with the new resume data. Would you like to proceed?")) {
                  setProfileExists(false);
                  setActiveStep(1);
                  triggerToast("Please upload a new resume file to replace details.");
                }
              }}
              className="w-full text-center py-2 text-[12px] font-bold text-primary bg-primary/5 hover:bg-primary/10 transition-colors border border-primary/20 rounded-lg"
            >
              Replace Resume File
            </button>
          </div>
          
          {generatedAt && (
            <div className="text-center text-[10px] text-outline italic">
              Insights generated at {new Date(generatedAt).toLocaleString()}
            </div>
          )}
          
        </div>
      )}
    </aside>
  );
}
