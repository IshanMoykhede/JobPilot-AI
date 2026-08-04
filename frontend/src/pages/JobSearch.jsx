import React, { useState, useEffect, useRef } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";
import Icon from "../components/common/Icon";
import SkillTag from "../components/common/SkillTag";
import CircularProgress from "../components/common/CircularProgress";
import { useAuth } from "../context/AuthContext";
import { startJobSearchStream, fetchSearchHistory, fetchSearchResults, resumeJobSearchStream, deleteJobSearch, renameJobSearch } from "../services/jobsApi";
import { useToast } from "../components/common/Toast";

import JobCard from "../components/search-results/JobCard";

const DEFAULT_STEPS = [
  { id: '__start__', title: 'Initialization', desc: 'Starting AI agent...', icon: 'rocket_launch', status: 'pending' },
  { id: 'query_optimizer_node', title: 'Optimization', desc: 'Refining your query...', icon: 'psychology', status: 'pending' },
  { id: 'job_retrieval_node', title: 'Retrieval', desc: 'Fetching matching jobs...', icon: 'travel_explore', status: 'pending' },
  { id: 'job_knowledge_generator_node', title: 'Extraction', desc: 'Structuring requirements...', icon: 'schema', status: 'pending' },
  { id: 'embedding_store_node', title: 'Embeddings', desc: 'Vectorizing job data...', icon: 'blur_on', status: 'pending' },
  { id: 'semantic_matching_node', title: 'Matching', desc: 'Searching semantic space...', icon: 'hub', status: 'pending' },
  { id: 'scorer_node', title: 'Scoring', desc: 'Calculating final scores...', icon: 'score', status: 'pending' },
];

export default function JobSearch() {
  const { user } = useAuth();
  const toast = useToast();
  const [searchParams] = useSearchParams();
  
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);
  const [mode, setMode] = useState("idle"); // idle, loading, results
  const [steps, setSteps] = useState([...DEFAULT_STEPS]);
  const [results, setResults] = useState(null);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [historySidebarCollapsed, setHistorySidebarCollapsed] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const navigate = useNavigate();
  const [generatingJobId, setGeneratingJobId] = useState(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const jobsPerPage = 5;

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.history-dropdown')) {
        setOpenDropdownId(null);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Load history on mount
  useEffect(() => {
    if (user) {
      loadHistory();
    }
    
    // Auto-start search if passed via query params
    const q = searchParams.get("q");
    if (q && user) {
      setQuery(q);
      handleSearch(q);
    }
  }, [user]);

  const loadHistory = async () => {
    try {
      const hist = await fetchSearchHistory();
      setHistory(hist);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteSearch = async (e, threadId) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this search?")) return;
    try {
      await deleteJobSearch(threadId);
      toast.success("Search deleted");
      if (activeThreadId === threadId) {
        setMode("idle");
        setActiveThreadId(null);
        setResults(null);
      }
      loadHistory();
    } catch (err) {
      toast.error("Failed to delete search");
    }
    setOpenDropdownId(null);
  };

  const handleRenameSubmit = async (e, threadId) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      try {
        await renameJobSearch(threadId, editName);
        setEditingId(null);
        toast.success("Search renamed");
        loadHistory();
      } catch (err) {
        toast.error("Failed to rename search");
      }
    } else if (e.key === 'Escape') {
      setEditingId(null);
    }
  };

  const processStream = async (res) => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // Keep incomplete chunk

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.replace('data: ', '');
          let data;
          try {
            data = JSON.parse(dataStr);
          } catch (e) {
            console.error("JSON parse error:", e);
            continue; // Skip malformed JSON
          }
          
          if (data.node === "DONE") {
            // Done! Fetch the actual results
            await loadResults(data.thread_id);
            loadHistory(); // Refresh history
            return;
          } else if (data.node === "ERROR") {
            if (data.thread_id) setActiveThreadId(data.thread_id);
            throw new Error(data.detail);
          } else {
            // Mark previous active step as completed
            setSteps(prev => {
              const newSteps = [...prev];
              const activeIdx = newSteps.findIndex(s => s.status === 'active');
              if (activeIdx >= 0) newSteps[activeIdx].status = 'completed';
              
              // Mark current node as active
              const nodeIdx = newSteps.findIndex(s => s.id === data.node);
              if (nodeIdx >= 0) newSteps[nodeIdx].status = 'active';
              
              return newSteps;
            });
          }
        }
      }
    }
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim() || !user) return;
    
    setMode("loading");
    setSteps(DEFAULT_STEPS.map(s => ({ ...s, status: 'pending' })));
    setResults(null);
    setActiveThreadId(null);
    
    // Mark first step as active immediately
    updateStepStatus('__start__', 'active');

    try {
      const res = await startJobSearchStream(searchQuery);
      await processStream(res);
    } catch (e) {
      toast.error(e.message || "An error occurred");
      setSteps(prev => prev.map(s => s.status === 'active' ? { ...s, status: 'failed' } : s));
      setMode("failed");
    }
  };

  const handleGenerateResume = async (jobId, jobTitle) => {
    if (!jobId) {
      toast.error("Job details missing, cannot generate resume.");
      return;
    }

    setGeneratingJobId(jobId);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // 1. Start Session
      const startRes = await fetch(`${API_BASE_URL}/api/v2/resume/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          title: `Tailored Resume for ${jobTitle}`,
          job_id: jobId
        })
      });

      if (!startRes.ok) throw new Error("Failed to initialize resume session.");
      const { resume_id } = await startRes.json();

      // 3. Navigate
      navigate(`/resumes/edit/${resume_id}`);
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Error generating resume");
    } finally {
      setGeneratingJobId(null);
    }
  };

  const handleResume = async (threadId) => {
    if (!threadId || !user) return;
    
    setMode("loading");
    // Change any 'failed' step back to 'active'
    setSteps(prev => prev.map(s => s.status === 'failed' ? { ...s, status: 'active' } : s));

    try {
      const res = await resumeJobSearchStream(threadId);
      await processStream(res);
    } catch (e) {
      toast.error(e.message || "An error occurred");
      setSteps(prev => prev.map(s => s.status === 'active' ? { ...s, status: 'failed' } : s));
      setMode("failed");
    }
  };

  const loadResults = async (threadId) => {
    try {
      setMode("loading"); // just in case it was loading from history click
      const res = await fetchSearchResults(threadId);
      setResults(res);
      setCurrentPage(1);
      setActiveThreadId(threadId);
      setMode("results");
    } catch (e) {
      toast.error("Failed to load results");
      setMode("idle");
    }
  };

  const handleHistoryClick = (h) => {
    setActiveThreadId(h.id);
    if (h.status === "COMPLETED") {
      loadResults(h.id);
    } else {
      // It failed previously (or is stuck). Show the failed state so they can click Retry.
      setSteps(DEFAULT_STEPS.map((s, idx) => ({ ...s, status: idx === 0 ? 'failed' : 'pending' })));
      setMode("failed");
    }
  };

  const updateStepStatus = (id, status) => {
    setSteps(prev => prev.map(s => s.id === id ? { ...s, status } : s));
  };

  // Pagination Logic
  const indexOfLastJob = currentPage * jobsPerPage;
  const indexOfFirstJob = indexOfLastJob - jobsPerPage;
  const currentJobs = results?.jobs ? results.jobs.slice(indexOfFirstJob, indexOfLastJob) : [];
  const totalPages = results?.jobs ? Math.ceil(results.jobs.length / jobsPerPage) : 0;

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    const container = document.getElementById('results-container');
    if (container) container.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "AI Job Search" },
    ]}>
      <div className="h-full flex overflow-hidden w-full">
        
        {/* Sidebar: Search History */}
        <aside className={`${historySidebarCollapsed ? 'w-0 overflow-hidden opacity-0 border-transparent px-0' : 'w-[300px] border-r border-jp-border-subtle/50 opacity-100'} bg-jp-bg-app/40 backdrop-blur-2xl flex-col hidden lg:flex relative z-20 shadow-[1px_0_24px_rgba(0,0,0,0.2)] transition-all duration-300 ease-in-out`}>
          
          {/* Subtle glow in sidebar */}
          <div className="absolute top-0 left-0 w-full h-40 bg-gradient-to-b from-jp-accent/5 to-transparent pointer-events-none"></div>

          <div className="p-6 border-b border-jp-border-subtle/50 relative z-10 flex items-center justify-between min-w-[300px]">
            <h2 className="text-[11px] font-bold text-jp-text-secondary flex items-center gap-2 uppercase tracking-widest">
              <Icon name="history" className="text-[14px] text-jp-accent" />
              Recent Searches
            </h2>
            <button 
              onClick={() => setHistorySidebarCollapsed(true)} 
              className="w-6 h-6 rounded-md hover:bg-jp-bg-raised/50 flex items-center justify-center text-jp-text-muted hover:text-jp-text-primary transition-colors"
              title="Close Sidebar"
            >
              <Icon name="close" className="text-[14px]" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto relative z-10 scrollbar-hide py-2">
            {history.length === 0 ? (
              <div className="p-8 flex flex-col items-center justify-center text-center opacity-60 mt-10">
                <Icon name="inbox" className="text-[32px] text-jp-text-muted mb-3" />
                <p className="text-[12px] text-jp-text-tertiary">No past searches found.</p>
              </div>
            ) : (
              <div className="px-3 space-y-1 min-w-[276px]">
                {history.map(h => {
                  const isActive = activeThreadId === h.id;
                  return (
                    <div
                      key={h.id}
                      onClick={() => handleHistoryClick(h)}
                      className={`w-full text-left px-4 py-3.5 rounded-xl transition-all duration-300 flex flex-col gap-1.5 relative group cursor-pointer
                        ${isActive ? 'bg-jp-accent/10 border border-jp-accent/20 shadow-sm' : 'hover:bg-jp-bg-surface border border-transparent'}
                      `}
                    >
                      <div className="flex items-start justify-between gap-2">
                        {editingId === h.id ? (
                          <input 
                            autoFocus
                            value={editName}
                            onChange={(e) => setEditName(e.target.value)}
                            onKeyDown={(e) => handleRenameSubmit(e, h.id)}
                            onClick={(e) => e.stopPropagation()}
                            onBlur={() => setEditingId(null)}
                            className="bg-jp-bg-raised border border-jp-accent rounded px-2 py-0.5 text-[13px] font-semibold text-jp-text-primary w-full outline-none focus:ring-1 focus:ring-jp-accent shadow-[0_0_8px_var(--color-jp-accent-glow)]"
                          />
                        ) : (
                          <span className={`text-[13px] font-semibold truncate block flex-1 ${isActive ? 'text-jp-accent-text' : 'text-jp-text-primary group-hover:text-jp-accent-text transition-colors'}`}>
                            {h.original_query}
                          </span>
                        )}

                        {/* 3-Dot Menu */}
                        <div className="relative history-dropdown shrink-0">
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenDropdownId(openDropdownId === h.id ? null : h.id);
                            }}
                            className={`w-5 h-5 rounded hover:bg-jp-bg-raised flex items-center justify-center text-jp-text-muted hover:text-jp-text-primary transition-colors ${openDropdownId === h.id ? 'opacity-100 bg-jp-bg-raised' : 'opacity-0 group-hover:opacity-100'}`}
                          >
                            <Icon name="more_vert" className="text-[14px]" />
                          </button>
                          
                          {/* Dropdown popup */}
                          {openDropdownId === h.id && (
                            <div className="absolute right-0 top-6 w-28 bg-jp-bg-surface border border-jp-border-subtle rounded-lg shadow-xl z-50 overflow-hidden animate-fade-in-up origin-top-right">
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setEditName(h.original_query);
                                  setEditingId(h.id);
                                  setOpenDropdownId(null);
                                }}
                                className="w-full text-left px-3 py-2 text-[12px] text-jp-text-primary hover:bg-jp-bg-raised hover:text-jp-accent transition-colors flex items-center gap-2"
                              >
                                <Icon name="edit" className="text-[14px]" /> Rename
                              </button>
                              <button 
                                onClick={(e) => handleDeleteSearch(e, h.id)}
                                className="w-full text-left px-3 py-2 text-[12px] text-jp-error hover:bg-jp-error-muted transition-colors flex items-center gap-2"
                              >
                                <Icon name="delete" className="text-[14px]" /> Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-between mt-0.5">
                        <span className="text-[11px] font-medium text-jp-text-muted">{new Date(h.created_at).toLocaleDateString()}</span>
                        {h.status === "COMPLETED" ? (
                          <div className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-jp-success shadow-[0_0_8px_var(--color-jp-success-glow)]"></span>
                            <span className="text-[10px] font-semibold text-jp-success-text uppercase tracking-wider">Ready</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-jp-warning shadow-[0_0_8px_var(--color-jp-warning-glow)]"></span>
                            <span className="text-[10px] font-semibold text-jp-warning-text uppercase tracking-wider">{h.status}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col relative">

          {/* Expand Sidebar Floating Button */}
          {historySidebarCollapsed && (
            <button 
              onClick={() => setHistorySidebarCollapsed(false)}
              className="absolute left-4 top-4 z-50 w-10 h-10 rounded-xl bg-jp-bg-surface/80 backdrop-blur-md border border-jp-border-subtle shadow-md flex items-center justify-center text-jp-text-primary hover:text-jp-accent hover:border-jp-accent transition-all hover:scale-105 hidden lg:flex animate-fade-in"
              title="Show Recent Searches"
            >
              <Icon name="history" className="text-[20px]" />
            </button>
          )}
          
          {/* Header Search Bar (Morphs to Hero when Idle) */}
          <div className={`shrink-0 z-10 transition-all duration-700 ease-in-out flex flex-col ${
            mode === "idle" 
              ? "flex-1 items-center justify-center p-6 lg:p-10 relative" 
              : "p-6 lg:p-10 border-b border-jp-border-subtle bg-jp-bg-surface/80 backdrop-blur-xl sticky top-0"
          }`}>
            
            {/* Background decorative blob (Idle Only) */}
            {mode === "idle" && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-jp-accent/10 blur-[120px] rounded-full pointer-events-none"></div>
            )}

            {/* Hero Content (Idle Only) */}
            {mode === "idle" && (
              <div className="flex flex-col items-center justify-center text-center max-w-2xl mx-auto mb-10 animate-fade-in relative w-full z-10">
                <div className="relative w-28 h-28 mb-8 group">
                  <div className="absolute inset-0 bg-jp-accent/40 rounded-[2rem] blur-2xl group-hover:bg-jp-accent/60 transition-colors animate-pulse-subtle"></div>
                  <div className="absolute inset-0 bg-gradient-to-br from-jp-accent via-jp-info to-jp-accent rounded-[2rem] opacity-20 blur-md"></div>
                  <div className="relative w-full h-full rounded-[2rem] bg-gradient-to-br from-white/10 to-white/5 border border-white/20 backdrop-blur-xl shadow-[0_0_40px_rgba(99,102,241,0.2)] flex items-center justify-center transform group-hover:scale-105 group-hover:-translate-y-1 transition-all duration-500">
                    <Icon name="travel_explore" className="text-[48px] text-white drop-shadow-lg group-hover:rotate-12 transition-transform duration-500" />
                  </div>
                </div>
                
                <h2 className="text-4xl lg:text-5xl font-bold tracking-tight mb-5 drop-shadow-sm">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-jp-accent-text to-jp-text-secondary">
                    Discover your next opportunity
                  </span>
                </h2>
                <p className="text-[16px] lg:text-[17px] text-jp-text-tertiary leading-relaxed max-w-lg mx-auto font-medium">
                  JobPilot AI will search the web, analyze job descriptions, and semantically match them against your unique candidate profile.
                </p>
              </div>
            )}

            <form 
              onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
              className={`relative mx-auto group transition-all duration-700 w-full z-10 ${mode === "idle" ? "max-w-2xl" : "max-w-4xl"}`}
            >
              {/* Animated glow behind the search bar */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-jp-accent via-jp-info to-jp-accent rounded-[1.25rem] blur opacity-20 group-hover:opacity-40 group-focus-within:opacity-70 group-focus-within:blur-md transition-all duration-500"></div>
              
              <div className="relative flex items-center bg-[#0a0a0c]/90 backdrop-blur-2xl border border-white/10 hover:border-white/20 focus-within:border-jp-accent/50 focus-within:ring-4 focus-within:ring-jp-accent/20 transition-all duration-300 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
                <Icon name="auto_awesome" className="absolute left-6 text-[22px] text-jp-accent group-focus-within:text-jp-info transition-colors group-focus-within:animate-pulse-subtle" />
                <input
                  type="text"
                  placeholder="What kind of role are you looking for? (e.g. Remote Next.js Developer in Europe)"
                  className="w-full pl-14 pr-[120px] py-5 lg:py-6 bg-transparent text-[16px] text-jp-text-primary placeholder:text-jp-text-muted focus:outline-none focus:ring-0"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={mode === "loading" || mode === "failed"}
                />
                <button 
                  type="submit" 
                  disabled={mode === "loading" || mode === "failed" || !query.trim()}
                  className="absolute right-2.5 h-[calc(100%-20px)] px-7 rounded-xl bg-gradient-to-r from-jp-accent to-jp-accent-strong text-white font-bold text-[14px] shadow-[0_0_20px_var(--color-jp-accent-glow)] hover:shadow-[0_0_30px_var(--color-jp-accent-glow)] hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none tracking-wide"
                >
                  {mode === "loading" ? "Searching..." : "Search"}
                </button>
              </div>
            </form>

            {/* Suggestions (Idle Only) */}
            {mode === "idle" && (
              <div className="flex flex-wrap justify-center gap-3 mt-10 animate-fade-in w-full max-w-2xl mx-auto z-10">
                {["DevOps in Pune", "Remote Frontend Developer", "Cloud Architect"].map(tag => (
                  <button
                    key={tag}
                    onClick={() => { setQuery(tag); handleSearch(tag); }}
                    className="px-5 py-2.5 text-[13px] font-semibold tracking-wide rounded-full border border-jp-border-subtle bg-white/5 backdrop-blur-md text-jp-text-secondary hover:text-white hover:border-jp-accent/50 hover:bg-jp-accent/20 transition-all shadow-sm hover:shadow-[0_0_12px_var(--color-jp-accent-glow)] hover:-translate-y-0.5"
                  >
                    ✨ {tag}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Dynamic Body (Only visible when not idle) */}
          {mode !== "idle" && (
            <div className="flex-1 overflow-y-auto p-6 lg:p-8 relative z-0">

            {/* STATE 2: LOADING or FAILED (Cinematic Pipeline) */}
            {(mode === "loading" || mode === "failed") && (
              <div className="max-w-3xl mx-auto py-12 animate-fade-in">
                
                {/* Header Area */}
                <div className="flex flex-col items-center text-center mb-12 relative">
                  <div className={`absolute -inset-4 rounded-full blur-3xl opacity-20 ${mode === "failed" ? "bg-jp-error" : "bg-jp-accent animate-pulse-slow"}`}></div>
                  <div className="relative">
                    <div className="w-16 h-16 rounded-2xl bg-jp-bg-raised border border-jp-border-subtle shadow-xl flex items-center justify-center mb-4">
                      <Icon name={mode === "failed" ? "error" : "memory"} className={`text-[32px] ${mode === "failed" ? "text-jp-error" : "text-jp-accent animate-pulse"}`} />
                    </div>
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight text-jp-text-primary">
                    {mode === "failed" ? "Agent Encountered an Error" : "Agent is analyzing the web..."}
                  </h2>
                  <p className="text-[14px] text-jp-text-muted mt-2 max-w-md">
                    {mode === "failed" ? "The pipeline has safely paused execution." : "LangGraph pipeline initialized. Processing steps sequentially."}
                  </p>
                </div>
                
                {/* Glowing Pipeline */}
                <div className="relative p-6 lg:p-8 rounded-3xl bg-jp-bg-surface/50 backdrop-blur-xl border border-jp-border-subtle shadow-[0_8px_32px_rgba(0,0,0,0.4)] overflow-hidden">
                  {/* Subtle background glow inside terminal */}
                  <div className="absolute top-0 right-0 w-64 h-64 bg-jp-info/10 blur-[100px] rounded-full pointer-events-none"></div>

                  <div className="space-y-0 relative before:absolute before:left-[2.1rem] before:top-4 before:bottom-4 before:w-0.5 before:bg-gradient-to-b before:from-jp-accent/50 before:via-jp-border-subtle before:to-transparent">
                    {steps.map((step, idx) => {
                      const isActive = step.status === 'active';
                      const isCompleted = step.status === 'completed';
                      const isPending = step.status === 'pending';
                      const isFailed = step.status === 'failed';
                      
                      return (
                        <div key={step.id} className={`relative flex gap-6 p-4 rounded-2xl transition-all duration-500 ${isActive ? 'bg-jp-accent/5 scale-[1.02] origin-left' : 'hover:bg-jp-bg-raised/30'} ${isPending ? 'opacity-40' : 'opacity-100'}`}>
                          
                          {/* Glowing Icon Node */}
                          <div className="relative z-10 shrink-0 mt-1">
                            {isActive && (
                              <div className="absolute inset-0 bg-jp-accent blur-md rounded-full opacity-60 animate-pulse"></div>
                            )}
                            <div className={`relative flex items-center justify-center w-11 h-11 rounded-full border-2 bg-jp-bg-raised shadow-md transition-all duration-300
                              ${isCompleted ? 'border-jp-success text-jp-success-text bg-jp-success/10' : 
                                isFailed ? 'border-jp-error text-jp-error-text bg-jp-error/10 shadow-[0_0_12px_var(--color-jp-error-glow)]' : 
                                isActive ? 'border-jp-accent text-jp-accent-text bg-jp-accent/10 shadow-[0_0_12px_var(--color-jp-accent-glow)]' : 
                                'border-jp-border text-jp-text-muted'}
                            `}>
                              <Icon name={isCompleted ? "check" : isFailed ? "close" : step.icon} className={`text-[18px] ${isActive && !isFailed && !isCompleted ? 'animate-spin-slow' : ''}`} />
                            </div>
                          </div>
                          
                          {/* Content Box */}
                          <div className="flex-1 pt-1">
                            <h3 className={`text-[15px] font-bold tracking-wide mb-1 flex items-center gap-2
                              ${isCompleted ? 'text-jp-success-text' : isFailed ? 'text-jp-error-text' : isActive ? 'text-jp-accent-text' : 'text-jp-text-primary'}`}>
                              {step.title}
                              {isActive && <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-jp-accent text-white uppercase tracking-wider animate-pulse-subtle">RUNNING</span>}
                            </h3>
                            <p className="text-[13px] text-jp-text-tertiary leading-relaxed">
                              {step.desc}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Retry UI when failed */}
                {mode === "failed" && (
                  <div className="mt-12 p-6 rounded-xl border border-jp-error/30 bg-jp-error-muted/20 flex flex-col items-center text-center animate-fade-in">
                    <Icon name="warning" className="text-[32px] text-jp-error mb-3" />
                    <h3 className="text-lg font-semibold text-jp-text-primary mb-2">Execution Halted</h3>
                    <p className="text-sm text-jp-text-muted mb-6">The pipeline has safely paused. Your previously completed steps are saved in the database.</p>
                    <button
                      onClick={() => handleResume(activeThreadId)}
                      className="px-6 py-2.5 rounded-lg bg-jp-accent text-white font-medium shadow-sm hover:bg-jp-accent-hover focus:ring-2 focus:ring-jp-accent transition-all flex items-center gap-2"
                    >
                      <Icon name="refresh" className="text-[18px]" />
                      Retry Failed Step
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* STATE 3: RESULTS */}
            {mode === "results" && results && (
              <div className="animate-fade-in space-y-6">
                <div className="flex items-end justify-between">
                  <div>
                    <h1 className="text-xl font-semibold text-jp-text-primary mb-1">
                      Results for "{results.query}"
                    </h1>
                    <p className="text-[13px] text-jp-text-tertiary">
                      Found {results.jobs?.length || 0} top matching roles.
                    </p>
                  </div>
                </div>

                <div id="results-container" className="max-w-5xl space-y-5 pb-8 pt-4">
                  {currentJobs.map((job) => (
                    <JobCard 
                      key={job.job_match_score_id} 
                      job={job} 
                      onGenerateResume={() => handleGenerateResume(job.job_id, job.title)}
                      isGenerating={generatingJobId === job.job_id}
                    />
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="max-w-5xl flex items-center justify-between py-6 border-t border-jp-border-subtle mt-4 mb-12">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-5 py-2.5 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-jp-text-primary text-[13px] font-semibold hover:bg-jp-bg-raised hover:border-jp-accent/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <Icon name="chevron_left" className="text-[16px]" /> Previous
                    </button>
                    <span className="text-[13px] font-medium text-jp-text-tertiary">
                      Page <strong className="text-jp-text-primary">{currentPage}</strong> of <strong className="text-jp-text-primary">{totalPages}</strong>
                    </span>
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="px-5 py-2.5 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-jp-text-primary text-[13px] font-semibold hover:bg-jp-bg-raised hover:border-jp-accent/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      Next <Icon name="chevron_right" className="text-[16px]" />
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}