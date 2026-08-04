import React, { useState } from 'react';
import Icon from '../common/Icon';

function ResumePreview({ resumeContent, onEditRequest, onVersionChange, isGenerating }) {
  const [editingSection, setEditingSection] = useState(null);
  const [editPrompt, setEditPrompt] = useState('');

  if (!resumeContent) return null;

  const sections = resumeContent.sections || [];

  const handleEditSubmit = (e, sectionType) => {
    e.preventDefault();
    if (!editPrompt.trim()) return;
    onEditRequest(sectionType, editPrompt);
    setEditingSection(null);
    setEditPrompt('');
  };

  const renderSectionHeader = (title, sectionType, sectionKey, currentIndex, totalVersions) => {
    const isEditing = editingSection === sectionType;
    return (
      <div className="group/header relative border-b-2 border-slate-900 pb-1.5 mb-2 mt-2 flex items-center justify-between">
        <h2 className="text-[14px] font-black uppercase tracking-[0.25em] text-slate-900">{title}</h2>
        
        <div className="flex items-center gap-3">
          {/* Version Switcher */}
          <div className="flex items-center gap-1.5 bg-slate-100 rounded-md px-1.5 py-0.5 text-[11px] font-semibold text-slate-600 transition-opacity duration-300 opacity-0 group-hover/header:opacity-100">
              <button 
                onClick={() => onVersionChange && onVersionChange(sectionKey, currentIndex - 2)}
                disabled={currentIndex <= 1}
                className="hover:text-jp-accent disabled:opacity-30 disabled:hover:text-slate-600 p-0.5 transition-colors"
                title="Previous Draft"
              >
                <Icon name="chevron_left" className="text-[14px]" />
              </button>
              <span>v{currentIndex} / {totalVersions}</span>
              <button 
                onClick={() => onVersionChange && onVersionChange(sectionKey, currentIndex)}
                disabled={currentIndex >= totalVersions}
                className="hover:text-jp-accent disabled:opacity-30 disabled:hover:text-slate-600 p-0.5 transition-colors"
                title="Next Draft"
              >
                <Icon name="chevron_right" className="text-[14px]" />
              </button>
            </div>
          <button 
            onClick={() => setEditingSection(isEditing ? null : sectionType)}
            className={`text-[11px] font-semibold text-jp-accent flex items-center gap-1 bg-jp-accent/5 hover:bg-jp-accent/15 px-2.5 py-1 rounded-md transition-all duration-300 ${isEditing ? 'opacity-100 scale-100' : 'opacity-0 scale-95 group-hover/header:opacity-100 group-hover/header:scale-100'}`}
          >
            <Icon name="edit" className="text-[14px]" />
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>
        
        {isEditing && (
          <form 
            onSubmit={(e) => handleEditSubmit(e, sectionType)}
            className="absolute top-full right-0 mt-2 z-50 bg-white/95 backdrop-blur-xl shadow-[0_12px_40px_rgb(0,0,0,0.15)] border border-slate-200 rounded-xl p-4 w-[320px] origin-top-right animate-in fade-in zoom-in-95 duration-200"
          >
            <div className="flex items-center gap-2 mb-3">
              <Icon name="auto_awesome" className="text-jp-accent text-[16px]" />
              <p className="text-[12px] text-slate-700 font-medium">How should the AI rewrite this?</p>
            </div>
            <div className="flex flex-col gap-2.5">
              <input 
                type="text" 
                value={editPrompt}
                onChange={e => setEditPrompt(e.target.value)}
                autoFocus
                placeholder="e.g. Make it sound more senior..."
                className="w-full border border-slate-200 bg-slate-50 rounded-lg px-3 py-2 text-[13px] focus:border-jp-accent focus:bg-white focus:outline-none focus:ring-2 focus:ring-jp-accent/20 transition-all"
              />
              <button 
                type="submit"
                disabled={isGenerating || !editPrompt.trim()}
                className="w-full bg-jp-accent text-white px-4 py-2 rounded-lg text-[13px] font-semibold shadow-md shadow-jp-accent/20 hover:bg-jp-accent-hover hover:shadow-lg disabled:opacity-50 transition-all flex justify-center items-center gap-2"
              >
                Apply Changes
              </button>
            </div>
          </form>
        )}
      </div>
    );
  };

  const renderSummary = (summaryData) => {
    const text = typeof summaryData === 'string' ? summaryData : summaryData?.content || '';
    return (
      <div className="text-[13.5px] text-slate-700 leading-relaxed font-medium">
        {text}
      </div>
    );
  };

  const renderProjects = (projects) => (
    <div className="space-y-3">
      {projects.map((proj, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-baseline mb-0.5">
            <h3 className="text-[14px] font-bold text-slate-900">
              {proj.title}
              {proj.github_url && <a href={proj.github_url} className="text-slate-400 ml-2 font-medium text-[11px] hover:text-jp-accent transition-colors">GitHub</a>}
            </h3>
            <span className="text-[12px] text-slate-500 font-medium italic">
              {proj.technologies?.slice(0,4).join(', ')}
            </span>
          </div>
          {proj.description && <p className="text-[13px] text-slate-600 mb-1">{proj.description}</p>}
          <ul className="list-disc list-outside ml-4 space-y-0.5">
            {proj.highlights?.map((highlight, hIdx) => (
              <li key={hIdx} className="text-[13px] text-slate-700 pl-1 leading-relaxed">{highlight}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderExperience = (experience) => (
    <div className="space-y-3">
      {experience.map((exp, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-baseline mb-0.5">
            <h3 className="text-[14px] font-bold text-slate-900">{exp.role}</h3>
            <span className="text-[12.5px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md">
              {exp.start_date || ''} {exp.start_date && exp.end_date ? '-' : ''} {exp.end_date || (exp.currently_working ? 'Present' : '')}
            </span>
          </div>
          <div className="text-[13px] text-jp-accent font-medium mb-1.5">{exp.company} {exp.location ? <span className="text-slate-400">| {exp.location}</span> : ''}</div>
          <ul className="list-disc list-outside ml-4 space-y-0.5">
            {exp.responsibilities?.map((resp, rIdx) => (
              <li key={rIdx} className="text-[13px] text-slate-700 pl-1 leading-relaxed">{resp}</li>
            ))}
            {exp.achievements?.map((ach, aIdx) => (
              <li key={`ach-${aIdx}`} className="text-[13px] text-slate-700 pl-1 leading-relaxed">{ach}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderSkills = (skills) => (
    <div className="space-y-2">
      {skills.map((category, idx) => (
        <div key={idx} className="text-[13px] text-slate-700 leading-relaxed">
          <span className="font-bold text-slate-900 mr-1.5">{category.category}:</span>
          <span className="font-medium text-slate-600">{category.skills?.join(', ')}</span>
        </div>
      ))}
    </div>
  );

  const renderEducation = (education) => (
    <div className="space-y-2">
      {education.map((edu, idx) => (
        <div key={idx} className="flex justify-between items-start">
          <div>
            <h3 className="text-[14px] font-bold text-slate-900 mb-0.5">{edu.institution}</h3>
            <p className="text-[13px] text-slate-600 font-medium">{edu.degree} {edu.specialization ? <span className="text-slate-400 font-normal">in {edu.specialization}</span> : ''}</p>
          </div>
          <div className="text-[12.5px] font-semibold text-slate-600 text-right">
            {edu.end_year || ''}
            {edu.cgpa && <div className="text-slate-500 font-medium mt-0.5">CGPA: {edu.cgpa}</div>}
          </div>
        </div>
      ))}
    </div>
  );

  const renderCertifications = (certs) => (
    <div className="space-y-1.5">
      {certs.map((cert, idx) => (
        <div key={idx} className="flex justify-between items-baseline">
          <div className="text-[13px] text-slate-700">
            <span className="font-bold text-slate-900">{cert.name}</span> <span className="text-slate-400 mx-1">—</span> <span className="font-medium">{cert.issuer}</span>
          </div>
          <div className="text-[12.5px] font-semibold text-slate-500 bg-slate-50 px-2 py-0.5 rounded">
            {cert.issue_date || ''}
          </div>
        </div>
      ))}
    </div>
  );

  const renderCoCurricular = (activities) => (
    <div className="space-y-3">
      {activities.map((act, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-baseline mb-0.5">
            <h3 className="text-[14px] font-bold text-slate-900">{act.title}</h3>
            <div className="text-[12.5px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md">{act.start_date && act.end_date ? `${act.start_date} - ${act.end_date}` : act.start_date || act.end_date || ''}</div>
          </div>
          <div className="text-[13px] font-medium text-jp-accent mb-1">{act.organization}</div>
          {act.description && <p className="text-[13px] text-slate-700 leading-relaxed">{act.description}</p>}
        </div>
      ))}
    </div>
  );

  return (
    <div className="bg-white shadow-[0_30px_80px_rgba(0,0,0,0.12)] ring-1 ring-slate-900/5 min-h-[1056px] w-full p-12 lg:p-16 font-sans rounded-2xl transition-all duration-700 relative group/paper overflow-hidden">
      {/* Decorative top border */}
      <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-0 group-hover/paper:opacity-100 transition-opacity duration-700" />
      
      {/* Header Data from Personal Information section */}
      {(() => {
        const personalInfoSection = sections.find(s => s.section_type === 'PERSONAL_INFORMATION');
        if (!personalInfoSection || !personalInfoSection.content) {
          return (
            <div className="text-center mb-8 opacity-40">
              <h1 className="text-[28px] font-extrabold text-slate-800 uppercase tracking-widest mb-1">Candidate Name</h1>
              <div className="text-[13px] text-slate-500 flex justify-center items-center gap-3">
                <span>Location</span> • <span>email@example.com</span>
              </div>
            </div>
          );
        }
        
        const info = personalInfoSection.content;
        return (
          <div className="text-center mb-6 pb-3 border-b-2 border-slate-100">
            <h1 className="text-[34px] font-black text-slate-900 uppercase tracking-[0.1em] mb-2 leading-none">{info.full_name}</h1>
            <div className="text-[13px] font-medium text-slate-600 flex flex-wrap justify-center items-center gap-x-3 gap-y-1.5">
              {info.location && <span>{info.location}</span>}
              {info.location && <span className="text-indigo-300 mx-0.5">•</span>}
              
              {info.email && <a href={`mailto:${info.email}`} className="hover:text-indigo-600 transition-colors">{info.email}</a>}
              {info.email && (info.phone || info.linkedin || info.portfolio || info.github) && <span className="text-indigo-300 mx-0.5">•</span>}
              
              {info.phone && <span>{info.phone}</span>}
              {info.phone && (info.linkedin || info.portfolio || info.github) && <span className="text-indigo-300 mx-0.5">•</span>}
              
              {info.linkedin && (
                <a href={info.linkedin.startsWith('http') ? info.linkedin : `https://${info.linkedin}`} target="_blank" rel="noreferrer" className="hover:text-indigo-600 transition-colors">
                  {info.linkedin.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}
                </a>
              )}
              {info.linkedin && (info.portfolio || info.github) && <span className="text-indigo-300 mx-0.5">•</span>}
              
              {info.github && (
                <a href={info.github.startsWith('http') ? info.github : `https://${info.github}`} target="_blank" rel="noreferrer" className="hover:text-indigo-600 transition-colors">
                  {info.github.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}
                </a>
              )}
              {info.github && info.portfolio && <span className="text-indigo-300 mx-0.5">•</span>}
              
              {info.portfolio && (
                <a href={info.portfolio.startsWith('http') ? info.portfolio : `https://${info.portfolio}`} target="_blank" rel="noreferrer" className="hover:text-indigo-600 transition-colors">
                  {info.portfolio.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}
                </a>
              )}
            </div>
          </div>
        );
      })()}

      {sections.length === 0 && !isGenerating && (
        <div className="flex flex-col items-center justify-center h-[600px] text-slate-400 space-y-6">
          <div className="relative">
            <div className="absolute inset-0 bg-jp-accent/10 blur-2xl rounded-full"></div>
            <Icon name="article" className="text-[64px] text-jp-accent/40 relative z-10" />
          </div>
          <div className="text-center">
            <h3 className="text-[18px] font-semibold text-slate-700 mb-2">Ready to craft your resume</h3>
            <p className="text-[14px] text-slate-500">Share your target job description with the AI to get started.</p>
          </div>
        </div>
      )}

      {sections.length === 0 && isGenerating && (
        <div className="flex flex-col items-center justify-center h-[600px] space-y-8 animate-in fade-in duration-700">
          <div className="relative flex items-center justify-center">
            <div className="absolute w-32 h-32 border-4 border-jp-accent/20 rounded-full animate-[spin_3s_linear_infinite]"></div>
            <div className="absolute w-24 h-24 border-4 border-t-jp-accent border-r-transparent border-b-transparent border-l-transparent rounded-full animate-[spin_1.5s_linear_infinite]"></div>
            <Icon name="auto_awesome" className="text-[32px] text-jp-accent animate-pulse relative z-10" />
          </div>
          <div className="text-center space-y-3">
            <h3 className="text-[18px] font-medium text-slate-800 flex items-center justify-center gap-2">
              AI is drafting your resume
              <span className="flex gap-0.5">
                <span className="animate-bounce text-jp-accent">.</span><span className="animate-bounce text-jp-accent" style={{ animationDelay: '0.1s' }}>.</span><span className="animate-bounce text-jp-accent" style={{ animationDelay: '0.2s' }}>.</span>
              </span>
            </h3>
            <div className="w-[300px] space-y-2 opacity-40">
              <div className="h-2 bg-slate-200 rounded animate-pulse"></div>
              <div className="h-2 bg-slate-200 rounded animate-pulse w-5/6 mx-auto"></div>
              <div className="h-2 bg-slate-200 rounded animate-pulse w-4/6 mx-auto"></div>
            </div>
          </div>
        </div>
      )}

      {/* Render generated sections in standard order */}
      {['SUMMARY', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'EDUCATION', 'CERTIFICATIONS', 'CO_CURRICULAR'].map(sectionType => {
        const typeSections = sections.filter(s => s.section_type === sectionType);
        if (typeSections.length === 0) return null;

        return typeSections.map((section, idx) => (
          <div key={`${sectionType}-${idx}`} className="mb-4 last:mb-0 group/section hover:bg-slate-50/50 -mx-4 px-4 py-2 rounded-xl transition-colors duration-300">
            {renderSectionHeader(
              section.display_name || sectionType, 
              sectionType, 
              section.sectionKey, 
              section.currentIndex, 
              section.totalVersions
            )}
            <div className="pl-1">
              {sectionType === 'SUMMARY' && renderSummary(section.content)}
              {sectionType === 'EXPERIENCE' && renderExperience(section.content)}
              {sectionType === 'PROJECTS' && renderProjects(section.content)}
              {sectionType === 'SKILLS' && renderSkills(section.content)}
              {sectionType === 'EDUCATION' && renderEducation(section.content)}
              {sectionType === 'CERTIFICATIONS' && renderCertifications(section.content)}
              {sectionType === 'CO_CURRICULAR' && renderCoCurricular(section.content)}
            </div>
          </div>
        ));
      })}
    </div>
  );
}

export default ResumePreview;
