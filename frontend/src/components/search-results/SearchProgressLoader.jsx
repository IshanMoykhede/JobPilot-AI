import React, { useState, useEffect, useRef } from 'react';
import Icon from '../common/Icon';

const PIPELINE_STAGES = [
  { step: 0, label: "Initializing workspace...", icon: "rocket_launch", color: "text-violet-400" },
  { step: 1, label: "Scouring the internet for jobs...", icon: "travel_explore", color: "text-blue-400" },
  { step: 2, label: "Extracting structured job requirements...", icon: "psychology", color: "text-cyan-400" },
  { step: 3, label: "Running semantic embeddings...", icon: "hub", color: "text-emerald-400" },
  { step: 4, label: "Calculating match scores...", icon: "compare_arrows", color: "text-amber-400" },
  { step: 5, label: "Drafting candidate guidance...", icon: "auto_awesome", color: "text-pink-400" },
  { step: 6, label: "Your results are ready!", icon: "check_circle", color: "text-green-400" },
];

export default function SearchProgressLoader({ workspaceId, onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [currentLabel, setCurrentLabel] = useState(PIPELINE_STAGES[0].label);
  const [currentIcon, setCurrentIcon] = useState(PIPELINE_STAGES[0].icon);
  const [isComplete, setIsComplete] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const [jobsFetched, setJobsFetched] = useState(0);
  const pollingRef = useRef(null);

  useEffect(() => {
    if (!workspaceId) return;

    const poll = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`http://localhost:8000/jobs/workspace/${workspaceId}/status`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) return;
        const data = await res.json();

        setCurrentStep(data.step);
        setCurrentLabel(data.label);
        setCurrentIcon(data.icon);
        setJobsFetched(data.jobs_fetched || 0);

        if (data.is_complete) {
          setIsComplete(true);
          clearInterval(pollingRef.current);
          setTimeout(() => onComplete && onComplete(), 1200);
        }
        if (data.is_failed) {
          setIsFailed(true);
          clearInterval(pollingRef.current);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    poll();
    pollingRef.current = setInterval(poll, 3000);
    return () => clearInterval(pollingRef.current);
  }, [workspaceId, onComplete]);

  const progressPercent = Math.max(5, (currentStep / 6) * 100);

  return (
    <div className="flex flex-col items-center justify-center pt-24 px-4">
      {/* Glowing orb background */}
      <div className="relative mb-10">
        <div className="absolute inset-0 w-32 h-32 rounded-full bg-jp-accent/20 blur-3xl animate-pulse" style={{ left: '-2rem', top: '-2rem' }}></div>
        
        {/* Brain icon with spinning ring */}
        <div className="relative w-24 h-24">
          <svg className="absolute inset-0 w-full h-full animate-spin" style={{ animationDuration: '3s' }} viewBox="0 0 100 100">
            <defs>
              <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--color-jp-accent)" stopOpacity="1" />
                <stop offset="100%" stopColor="var(--color-jp-accent)" stopOpacity="0.1" />
              </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="46" fill="none" stroke="url(#progressGrad)" strokeWidth="3" strokeLinecap="round" strokeDasharray="220 70" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className={`w-16 h-16 rounded-2xl bg-jp-bg-surface/80 backdrop-blur-xl border border-jp-border flex items-center justify-center shadow-2xl transition-all duration-500`}>
              <Icon name={currentIcon} className={`text-[28px] ${isComplete ? 'text-green-400' : isFailed ? 'text-red-400' : 'text-jp-accent'} transition-colors duration-500`} />
            </div>
          </div>
        </div>
      </div>

      {/* Stage label */}
      <h3 className="text-[20px] font-bold text-jp-text-primary mb-2 text-center">
        {isComplete ? '✨ Analysis Complete' : isFailed ? 'Pipeline Failed' : 'Analyzing Job Market'}
      </h3>
      <p className="text-[15px] text-jp-accent font-semibold mb-1 text-center min-h-[24px] transition-all duration-300">
        {currentLabel}
      </p>
      {jobsFetched > 0 && !isComplete && (
        <p className="text-[12px] text-jp-text-tertiary mb-4">{jobsFetched} jobs discovered</p>
      )}

      {/* Progress bar */}
      <div className="w-80 mt-6">
        <div className="relative h-2 bg-jp-bg-raised rounded-full overflow-hidden border border-jp-border-subtle/50">
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-1000 ease-out"
            style={{
              width: `${progressPercent}%`,
              background: isComplete
                ? 'linear-gradient(90deg, #22c55e, #4ade80)'
                : isFailed
                  ? 'linear-gradient(90deg, #ef4444, #f87171)'
                  : 'linear-gradient(90deg, var(--color-jp-accent), #818cf8)',
            }}
          />
          {/* Shimmer effect */}
          {!isComplete && !isFailed && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
          )}
        </div>
      </div>

      {/* Pipeline steps timeline */}
      <div className="mt-10 w-full max-w-md">
        <div className="space-y-1">
          {PIPELINE_STAGES.slice(1, 6).map((stage, idx) => {
            const stageStep = stage.step;
            const isDone = currentStep > stageStep;
            const isActive = currentStep === stageStep;
            return (
              <div
                key={stage.step}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-500 ${
                  isActive ? 'bg-jp-accent/10 border border-jp-accent/30 shadow-lg shadow-jp-accent/5' :
                  isDone ? 'opacity-60' : 'opacity-30'
                }`}
              >
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-all duration-500 ${
                  isDone ? 'bg-green-400/20' : isActive ? 'bg-jp-accent/20' : 'bg-jp-bg-raised'
                }`}>
                  {isDone ? (
                    <Icon name="check" className="text-[16px] text-green-400" />
                  ) : (
                    <Icon name={stage.icon} className={`text-[16px] ${isActive ? stage.color : 'text-jp-text-muted'}`} />
                  )}
                </div>
                <span className={`text-[13px] font-medium transition-colors duration-300 ${
                  isActive ? 'text-jp-text-primary' : isDone ? 'text-jp-text-secondary' : 'text-jp-text-muted'
                }`}>
                  {stage.label}
                </span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-jp-accent animate-pulse" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
