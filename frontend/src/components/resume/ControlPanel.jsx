import React, { useState, useEffect, useRef } from 'react';
import Icon from '../common/Icon';

function ControlPanel({ resumeState, isGenerating, waitingForUser, error, onSendMessage, onStartGeneration, onRetry, onCancel }) {
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

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-jp-border-subtle bg-jp-bg-app">
        <h2 className="text-[16px] font-semibold text-jp-text-primary flex items-center gap-2">
          <Icon name="auto_awesome" className="text-jp-accent text-[20px]" />
          Resume Tailoring AI
        </h2>
        <p className="text-[12px] text-jp-text-secondary mt-1">Generating section by section</p>
      </div>
      
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
        <div className="flex-1 overflow-y-auto p-5 space-y-5 hide-scrollbar relative">
        {resumeState?.messages?.map((msg, idx) => {
          // Skip system internal workflow messages unless they are human requests or user replies
          if (msg.role === 'SYSTEM' && msg.message_type !== 'HUMAN_INPUT_REQUEST') return null;
          
          const isUser = msg.role === 'USER' || msg.role === 'user';
          
          return (
            <div key={idx} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} group animate-in slide-in-from-bottom-2 duration-300`}>
              <div className={`max-w-[85%] p-3.5 rounded-2xl text-[13px] shadow-lg ${
                isUser 
                  ? 'bg-gradient-to-br from-jp-accent to-jp-accent-hover text-white rounded-br-sm shadow-jp-accent/20 border border-jp-accent/50' 
                  : 'bg-white/5 backdrop-blur-md border border-white/10 text-gray-200 rounded-bl-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          );
        })}
        {isGenerating && !waitingForUser && (
          <div className="flex items-start animate-in fade-in duration-300">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 p-4 rounded-2xl rounded-bl-sm shadow-lg">
              <span className="flex gap-1.5 items-center">
                <span className="w-2 h-2 bg-jp-accent rounded-full animate-bounce shadow-[0_0_5px_var(--color-jp-accent)]"></span>
                <span className="w-2 h-2 bg-jp-accent rounded-full animate-bounce shadow-[0_0_5px_var(--color-jp-accent)]" style={{ animationDelay: '0.15s' }}></span>
                <span className="w-2 h-2 bg-jp-accent rounded-full animate-bounce shadow-[0_0_5px_var(--color-jp-accent)]" style={{ animationDelay: '0.3s' }}></span>
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      )}

      {/* Input Area */}
      {(resumeState || isGenerating || error) && (
        <div className="p-4 bg-white/[0.02] border-t border-white/5 backdrop-blur-xl flex flex-col gap-3">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3.5 flex items-start gap-3 shadow-lg shadow-red-500/5">
              <Icon name="error" className="text-red-400 text-[18px] mt-0.5 animate-pulse" />
              <div className="flex-1">
                <h4 className="text-red-400 text-[13px] font-semibold mb-1">Generation Error</h4>
                <p className="text-red-300/80 text-[12px] leading-relaxed mb-3">{error}</p>
                <button 
                  onClick={onRetry}
                  className="bg-red-500 hover:bg-red-600 text-white text-[12px] font-medium py-1.5 px-4 rounded-lg transition-colors flex items-center gap-2 shadow-md shadow-red-500/20"
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
              className="w-full bg-red-500/5 hover:bg-red-500/10 text-red-400 border border-red-500/20 text-[12px] font-medium py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              <Icon name="stop" className="text-[16px]" />
              Stop Generation
            </button>
          )}
          <form onSubmit={handleSubmit} className="relative group">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isGenerating && !waitingForUser}
              placeholder={waitingForUser ? "Reply to the AI..." : (isGenerating ? "Agent is working..." : "Message the AI...")}
              className={`w-full py-3 pl-4 pr-12 rounded-xl text-[13px] border focus:outline-none transition-all duration-300 shadow-inner ${
                waitingForUser || !isGenerating
                  ? 'bg-black/20 border-white/10 text-white placeholder-gray-500 focus:border-jp-accent/50 focus:bg-black/40'
                  : 'bg-black/10 border-transparent text-gray-500 cursor-not-allowed'
              }`}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || (isGenerating && !waitingForUser)}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-lg bg-jp-accent text-white disabled:opacity-50 hover:bg-jp-accent-hover transition-all shadow-md shadow-jp-accent/20 group-focus-within:scale-105"
            >
              <Icon name="send" className="text-[14px] ml-0.5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default ControlPanel;
