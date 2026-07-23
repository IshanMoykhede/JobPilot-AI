import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';
import CircularProgress from '../components/common/CircularProgress';

function Resumes() {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/resume`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setResumes(data);
        }
      } catch (err) {
        console.error("Failed to fetch resumes:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResumes();
  }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this resume? All generated content will be permanently removed.")) {
      return;
    }
    
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/resume/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (res.ok) {
        setResumes(prev => prev.filter(r => r.id !== id));
      } else {
        alert("Failed to delete resume");
      }
    } catch (err) {
      console.error("Error deleting resume:", err);
      alert("Error deleting resume");
    }
  };

  const handleRename = async (e, id) => {
    e.stopPropagation();
    if (!editTitle.trim()) {
        setEditingId(null);
        return;
    }
    
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/resume/${id}/title`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ title: editTitle })
      });
      if (res.ok) {
        setResumes(prev => prev.map(r => r.id === id ? { ...r, title: editTitle } : r));
        setEditingId(null);
      } else {
        alert("Failed to rename resume");
      }
    } catch (err) {
      console.error("Error renaming resume:", err);
      alert("Error renaming resume");
    }
  };

  const getStatusDisplay = (status) => {
    switch (status) {
      case 'COMPLETED':
        return { icon: 'check_circle', color: 'text-jp-success', text: 'Completed', pulse: false };
      case 'FAILED':
        return { icon: 'error', color: 'text-red-500', text: 'Failed', pulse: false };
      case 'GENERATING':
        return { icon: 'autorenew', color: 'text-jp-accent', text: 'Generating', pulse: true };
      default:
        return { icon: 'description', color: 'text-jp-text-tertiary', text: status, pulse: false };
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

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
              {isLoading ? (
                <div className="col-span-full flex justify-center py-12">
                  <CircularProgress size={40} />
                </div>
              ) : (
                resumes.map((resume) => {
                  const statusInfo = getStatusDisplay(resume.status);
                  
                  return (
                    <div 
                      key={resume.id} 
                      onClick={() => navigate(`/resumes/edit/${resume.id}`)}
                      className="jp-card-interactive p-5 flex flex-col relative group cursor-pointer border hover:border-jp-accent transition-colors"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="w-10 h-10 rounded-lg bg-jp-bg-raised flex items-center justify-center shrink-0">
                          <Icon name="description" className="text-[20px] text-jp-text-tertiary" />
                        </div>
                        <span className={`jp-badge flex items-center gap-1 ${
                          resume.status === 'COMPLETED' ? 'jp-badge-success' : 
                          resume.status === 'FAILED' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 
                          'jp-badge-accent'
                        }`}>
                          <Icon name={statusInfo.icon} className={`text-[12px] ${statusInfo.pulse ? 'animate-spin' : ''}`} />
                          {statusInfo.text}
                        </span>
                      </div>
                      
                      <div className="flex-1 mb-5">
                        {editingId === resume.id ? (
                          <div 
                            className="flex items-center gap-2 mb-1" 
                            onClick={(e) => e.stopPropagation()}
                          >
                            <input 
                                type="text"
                                value={editTitle}
                                onChange={(e) => setEditTitle(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleRename(e, resume.id);
                                    if (e.key === 'Escape') setEditingId(null);
                                }}
                                autoFocus
                                className="flex-1 bg-jp-bg-app border border-jp-accent rounded-md px-2 py-1 text-[14px] text-jp-text-primary focus:outline-none"
                            />
                            <button 
                                onClick={(e) => handleRename(e, resume.id)}
                                className="text-jp-success hover:text-green-400 p-1 rounded-md bg-jp-bg-app border border-jp-border"
                            >
                                <Icon name="check" className="text-[16px]" />
                            </button>
                            <button 
                                onClick={() => setEditingId(null)}
                                className="text-jp-text-muted hover:text-white p-1 rounded-md bg-jp-bg-app border border-jp-border"
                            >
                                <Icon name="close" className="text-[16px]" />
                            </button>
                          </div>
                        ) : (
                          <h3 className="text-[15px] font-semibold text-jp-text-primary mb-1 line-clamp-1">{resume.title}</h3>
                        )}
                        <p className="text-[12px] text-jp-text-muted mt-3 flex items-center gap-1.5">
                          <Icon name="schedule" className="text-[14px]" />
                          Last updated: {formatDate(resume.updated_at)}
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t border-jp-border-subtle">
                        <div className="flex gap-1 ml-auto">
                          <button 
                            className="jp-btn-icon jp-btn-ghost hover:text-jp-accent" 
                            title="Rename"
                            onClick={(e) => {
                                e.stopPropagation();
                                setEditTitle(resume.title);
                                setEditingId(resume.id);
                            }}
                          >
                            <Icon name="edit" className="text-[18px]" />
                          </button>
                          <button 
                            className="jp-btn-icon jp-btn-ghost hover:text-red-500" 
                            title="Delete"
                            onClick={(e) => handleDelete(e, resume.id)}
                          >
                            <Icon name="delete" className="text-[18px]" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}

              {/* Generate New Card */}
              <button 
                onClick={() => navigate('/resumes/edit/new')}
                className="jp-card border-dashed border-2 border-jp-border-subtle hover:border-jp-accent hover:bg-jp-accent-muted/20 flex flex-col items-center justify-center min-h-[220px] group transition-all"
              >
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
                  <span className="text-[14px] font-semibold text-jp-text-primary">{resumes.length}</span>
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
