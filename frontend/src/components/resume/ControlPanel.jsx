import React, { useState, useEffect, useRef } from 'react';
import Icon from '../common/Icon';

function ControlPanel({ resumeState, isGenerating, waitingForUser, error, onSendMessage, onStartGeneration, onRetry, onCancel, onDownloadPdf }) {
  const [inputText, setInputText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [userQuery, setUserQuery] = useState('');
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [resumeState?.messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const getSectionStatus = (sectionName) => {
    if (!resumeState) return 'pending';
    
    // If it's the currently generating section
    if (resumeState.current_section === sectionName) return 'generating';
    
    // Check if it exists in the compiled content
    if (resumeState.resume_content?.sections?.some(s => s.section_type === sectionName)) {
      return 'completed';
    }
    
    return 'pending';
  };

  const SECTIONS = [
    { id: 'SUMMARY', label: 'Summary' },
    { id: 'PROJECTS', label: 'Projects' },
    { id: 'EXPERIENCE', label: 'Experience' },
    { id: 'SKILLS', label: 'Skills' },
    { id: 'EDUCATION', label: 'Education' },
    { id: 'CERTIFICATIONS', label: 'Certifications' },
  ];

  const renderStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <Icon name="check_circle" className="text-[16px] text-jp-success" />;
      case 'generating': return <Icon name="autorenew" className="text-[16px] text-jp-accent animate-spin" />;
      default: return <div className="w-[16px] h-[16px] rounded-full border-2 border-jp-border-subtle" />;
    }
  };

  const allSectionsDone = resumeState && (!resumeState.pending_sections || resumeState.pending_sections.length === 0);

  return (
    <div className="h-full flex flex-col">
      {/* Pending Sections Badges */}
      {(resumeState || isGenerating) && (
        <div className="p-5 bg-white/[0.02] border-b border-white/10 backdrop-blur-md shadow-sm z-10 relative shrink-0">
          <div className="flex items-center gap-2.5 mb-3.5">
            <Icon name="assignment" className="text-[16px] text-indigo-400" />
            <h3 className="text-[13px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-purple-300 tracking-wider uppercase">Pending Sections</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {resumeState?.pending_sections?.map((section, idx) => (
              <span key={idx} className="bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[11px] font-bold tracking-wider uppercase px-2.5 py-1.5 rounded-lg shadow-[0_0_10px_rgba(99,102,241,0.1)] transition-all duration-300 hover:bg-indigo-500/20 hover:border-indigo-500/50 hover:shadow-[0_0_15px_rgba(99,102,241,0.2)]">
                {section.replace('_', ' ')}
              </span>
            ))}
            {allSectionsDone && (
              <span className="text-emerald-400 text-[12px] font-bold tracking-wider uppercase flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg shadow-[0_0_15px_rgba(52,211,153,0.1)]">
                <Icon name="check_circle" className="text-[16px]" /> All Sections Drafted!
              </span>
            )}
          </div>
          {/* Download PDF Button */}
          {allSectionsDone && onDownloadPdf && (
            <button
              onClick={onDownloadPdf}
              className="mt-4 w-full py-3 flex items-center justify-center gap-2.5 rounded-2xl text-[13px] font-bold tracking-wide uppercase bg-gradient-to-r from-indigo-500 to-purple-600 text-white border border-white/10 shadow-[0_0_25px_rgba(99,102,241,0.3)] hover:shadow-[0_0_40px_rgba(99,102,241,0.5)] hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 cursor-pointer"
            >
              <Icon name="download" className="text-[18px]" />
              Download Resume PDF
            </button>
          )}
        </div>
      )}

      {/* Setup View if not started */}
      {!resumeState && !isGenerating && (
        <div className="flex-1 p-5 flex flex-col justify-start overflow-y-auto">
          <div className="mb-6">
            <h3 className="text-[15px] font-semibold text-jp-text-primary mb-2">User Query (Instructions)</h3>
            <p className="text-[12px] text-jp-text-secondary mb-3 leading-relaxed">
              Tell the AI how you want to tailor the resume (e.g. emphasize backend skills, keep it under 1 page).
            </p>
            <textarea
              className="w-full h-24 p-3 rounded-lg border border-jp-border-subtle bg-jp-bg-app text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none resize-none"
              placeholder="e.g. Please tailor my resume for a backend role and focus on my AWS experience..."
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
            />
          </div>
          <div className="mb-6">
            <h3 className="text-[15px] font-semibold text-jp-text-primary mb-2">Target Job Description</h3>
            <p className="text-[12px] text-jp-text-secondary mb-3 leading-relaxed">
              Paste the job description or role you want to target. The AI will perfectly tailor your resume to match these requirements.
            </p>
            <textarea
              className="w-full h-40 p-3 rounded-lg border border-jp-border-subtle bg-jp-bg-app text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none resize-none"
              placeholder="e.g. Seeking a Senior Backend Engineer with experience in Node.js, Python, and AWS..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>
          <button 
            onClick={() => onStartGeneration(userQuery, jobDescription)}
            disabled={!jobDescription.trim()}
            className="w-full jp-btn jp-btn-primary flex justify-center py-2.5 shadow-md shadow-jp-accent/20 disabled:opacity-50"
          >
            Start Generation
          </button>
        </div>
      )}



      {/* Chat History (Only show once started) */}
      {(resumeState || isGenerating) && (
        <div className="flex-1 overflow-y-auto p-6 space-y-6 hide-scrollbar relative">
        {resumeState?.messages?.map((msg, idx) => {
          // Skip system internal workflow messages unless they are human requests or user replies
          if (msg.role === 'SYSTEM' && msg.message_type !== 'HUMAN_INPUT_REQUEST') return null;
          
          const isUser = msg.role === 'USER' || msg.role === 'user';
          
          return (
            <div key={idx} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} group animate-in slide-in-from-bottom-3 duration-500 ease-out`}>
              <div className={`max-w-[85%] p-4 rounded-[20px] text-[13.5px] font-medium leading-relaxed shadow-xl ${
                isUser 
                  ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-br-sm shadow-indigo-500/20 border border-white/10' 
                  : 'bg-white/10 backdrop-blur-xl border border-white/20 text-slate-100 rounded-bl-sm shadow-black/10'
              }`}>
                {msg.content}
              </div>
            </div>
          );
        })}
        {isGenerating && !waitingForUser && (
          <div className="flex items-start animate-in fade-in duration-500">
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 p-4.5 rounded-[20px] rounded-bl-sm shadow-xl flex items-center gap-2">
              <span className="text-[12px] font-semibold text-indigo-300 uppercase tracking-widest mr-1">AI Thinking</span>
              <span className="flex gap-1.5 items-center">
                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-[bounce_1s_infinite] shadow-[0_0_8px_rgba(129,140,248,0.6)]"></span>
                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-[bounce_1s_infinite] shadow-[0_0_8px_rgba(129,140,248,0.6)]" style={{ animationDelay: '0.15s' }}></span>
                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-[bounce_1s_infinite] shadow-[0_0_8px_rgba(129,140,248,0.6)]" style={{ animationDelay: '0.3s' }}></span>
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      )}

      {/* Input Area */}
      {(resumeState || isGenerating || error) && (
        <div className="p-5 bg-white/[0.03] border-t border-white/10 backdrop-blur-2xl flex flex-col gap-3 shadow-[0_-10px_40px_rgba(0,0,0,0.2)] z-10 relative">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3 shadow-lg shadow-red-500/5 backdrop-blur-md">
              <Icon name="error" className="text-red-400 text-[20px] mt-0.5 animate-pulse" />
              <div className="flex-1">
                <h4 className="text-red-400 text-[13px] font-bold tracking-wide uppercase mb-1">Generation Error</h4>
                <p className="text-red-300/90 text-[12.5px] leading-relaxed mb-3 font-medium">{error}</p>
                <button 
                  onClick={onRetry}
                  className="bg-red-500 hover:bg-red-600 text-white text-[12px] font-bold tracking-wide uppercase py-2 px-5 rounded-xl transition-all duration-300 flex items-center gap-2 shadow-[0_0_15px_rgba(239,68,68,0.3)] hover:shadow-[0_0_25px_rgba(239,68,68,0.5)]"
                >
                  <Icon name="refresh" className="text-[14px]" />
                  Retry Generation
                </button>
              </div>
            </div>
          )}
          {isGenerating && !waitingForUser && onCancel && (
            <button 
              type="button"
              onClick={onCancel}
              className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-[12px] font-bold tracking-wide uppercase py-3 rounded-2xl transition-all duration-300 flex items-center justify-center gap-2"
            >
              <Icon name="stop" className="text-[16px]" />
              Stop Generation
            </button>
          )}
          <form onSubmit={handleSubmit} className="relative group/input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isGenerating && !waitingForUser}
              placeholder={waitingForUser ? "Reply to the AI..." : (isGenerating ? "Agent is working..." : "Message the AI...")}
              className={`w-full py-4 pl-5 pr-14 rounded-[20px] text-[13.5px] border-2 focus:outline-none transition-all duration-500 shadow-inner font-medium ${
                waitingForUser || !isGenerating
                  ? 'bg-black/40 border-white/10 text-white placeholder-gray-400 focus:border-indigo-500/60 focus:bg-black/60 focus:shadow-[0_0_20px_rgba(99,102,241,0.15)]'
                  : 'bg-black/20 border-transparent text-gray-600 cursor-not-allowed'
              }`}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || (isGenerating && !waitingForUser)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center rounded-[14px] bg-gradient-to-br from-indigo-500 to-purple-600 text-white disabled:opacity-40 disabled:grayscale transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.4)] hover:shadow-[0_0_25px_rgba(99,102,241,0.7)] hover:scale-105 active:scale-95"
            >
              <Icon name="send" className="text-[16px] ml-1" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default ControlPanel;
