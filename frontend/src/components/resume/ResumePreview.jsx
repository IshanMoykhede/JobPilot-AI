import React, { useState } from 'react';
import Icon from '../common/Icon';

function ResumePreview({ resumeContent, onEditRequest, isGenerating }) {
  const [editingSection, setEditingSection] = useState(null);
  const [editPrompt, setEditPrompt] = useState('');

  const sections = resumeContent?.sections || [];

  const handleEditSubmit = (e, sectionType) => {
    e.preventDefault();
    if (!editPrompt.trim()) return;
    onEditRequest(sectionType, editPrompt);
    setEditingSection(null);
    setEditPrompt('');
  };

  const renderSectionHeader = (title, sectionType) => {
    const isEditing = editingSection === sectionType;
    return (
      <div className="group relative border-b border-gray-300 pb-1.5 mb-4 mt-8 transition-colors hover:border-gray-400">
        <h2 className="text-[13px] font-bold uppercase tracking-widest text-gray-900">{title}</h2>
        <button 
          onClick={() => setEditingSection(isEditing ? null : sectionType)}
          className={`absolute right-0 top-0 text-[11px] font-semibold text-jp-accent flex items-center gap-1.5 bg-jp-accent/5 hover:bg-jp-accent/10 px-2.5 py-1 rounded-md transition-all duration-300 ${isEditing ? 'opacity-100 scale-100' : 'opacity-0 scale-95 group-hover:opacity-100 group-hover:scale-100'}`}
        >
          <Icon name="edit" className="text-[14px]" />
          {isEditing ? 'Cancel' : 'Edit'}
        </button>
        
        {isEditing && (
          <form 
            onSubmit={(e) => handleEditSubmit(e, sectionType)}
            className="absolute top-full right-0 mt-2 z-50 bg-white/95 backdrop-blur-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-black/5 rounded-xl p-4 w-[320px] origin-top-right animate-in fade-in zoom-in-95 duration-200"
          >
            <div className="flex items-center gap-2 mb-3">
              <Icon name="auto_awesome" className="text-jp-accent text-[16px]" />
              <p className="text-[12px] text-gray-700 font-medium">How should the AI rewrite this?</p>
            </div>
            <div className="flex flex-col gap-2.5">
              <input 
                type="text" 
                value={editPrompt}
                onChange={e => setEditPrompt(e.target.value)}
                autoFocus
                placeholder="e.g. Make it sound more senior..."
                className="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-[13px] focus:border-jp-accent focus:bg-white focus:outline-none focus:ring-2 focus:ring-jp-accent/20 transition-all"
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
      <div className="text-[13px] text-gray-700 leading-relaxed">
        {text}
      </div>
    );
  };

  const renderProjects = (projects) => (
    <div className="space-y-4">
      {projects.map((proj, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-baseline mb-1">
            <h3 className="text-[13px] font-bold text-gray-900">
              {proj.title}
              {proj.github_url && <a href={proj.github_url} className="text-gray-400 ml-2 font-normal text-[11px] hover:text-jp-accent">GitHub</a>}
            </h3>
            <span className="text-[12px] text-gray-600 italic">
              {proj.technologies?.slice(0,4).join(', ')}
            </span>
          </div>
          {proj.description && <p className="text-[12px] text-gray-700 mb-1.5">{proj.description}</p>}
          <ul className="list-disc list-outside ml-4 space-y-1">
            {proj.highlights?.map((highlight, hIdx) => (
              <li key={hIdx} className="text-[12px] text-gray-700 pl-1">{highlight}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderExperience = (experience) => (
    <div className="space-y-4">
      {experience.map((exp, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-baseline mb-1">
            <h3 className="text-[13px] font-bold text-gray-900">{exp.role}</h3>
            <span className="text-[12px] font-medium text-gray-700">
              {exp.start_date || ''} {exp.start_date && exp.end_date ? '-' : ''} {exp.end_date || (exp.currently_working ? 'Present' : '')}
            </span>
          </div>
          <div className="text-[12px] text-gray-600 mb-1.5">{exp.company} {exp.location ? `| ${exp.location}` : ''}</div>
          <ul className="list-disc list-outside ml-4 space-y-1">
            {exp.responsibilities?.map((resp, rIdx) => (
              <li key={rIdx} className="text-[12px] text-gray-700 pl-1">{resp}</li>
            ))}
            {exp.achievements?.map((ach, aIdx) => (
              <li key={`ach-${aIdx}`} className="text-[12px] text-gray-700 pl-1">{ach}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderSkills = (skills) => (
    <div className="space-y-1.5">
      {skills.map((category, idx) => (
        <div key={idx} className="text-[12px] text-gray-700">
          <span className="font-bold text-gray-900">{category.category}: </span>
          {category.skills?.join(', ')}
        </div>
      ))}
    </div>
  );

  const renderEducation = (education) => (
    <div className="space-y-3">
      {education.map((edu, idx) => (
        <div key={idx} className="flex justify-between items-baseline">
          <div>
            <h3 className="text-[13px] font-bold text-gray-900">{edu.institution}</h3>
            <p className="text-[12px] text-gray-700">{edu.degree} {edu.specialization ? `in ${edu.specialization}` : ''}</p>
          </div>
          <div className="text-[12px] font-medium text-gray-700 text-right">
            {edu.end_year || ''}
            {edu.cgpa && <div className="text-gray-500 font-normal">CGPA: {edu.cgpa}</div>}
          </div>
        </div>
      ))}
    </div>
  );

  const renderCertifications = (certs) => (
    <div className="space-y-2">
      {certs.map((cert, idx) => (
        <div key={idx} className="flex justify-between items-baseline">
          <div className="text-[12px] text-gray-700">
            <span className="font-bold text-gray-900">{cert.name}</span> — {cert.issuer}
          </div>
          <div className="text-[12px] text-gray-600">
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
          <div className="flex justify-between items-baseline">
            <h3 className="text-[13px] font-bold text-gray-900">{act.title}</h3>
            <div className="text-[12px] font-medium text-gray-700">{act.start_date && act.end_date ? `${act.start_date} - ${act.end_date}` : act.start_date || act.end_date || ''}</div>
          </div>
          <div className="text-[12px] font-medium text-jp-accent mb-1">{act.organization}</div>
          {act.description && <p className="text-[12px] text-gray-700 mt-1">{act.description}</p>}
        </div>
      ))}
    </div>
  );

  return (
    <div className="bg-white shadow-[0_20px_50px_rgba(0,0,0,0.2)] ring-1 ring-black/5 min-h-[1056px] w-full p-12 font-sans rounded-sm transition-all duration-500 relative group/paper">
      {/* Header Data from Personal Information section */}
      {(() => {
        const personalInfoSection = sections.find(s => s.section_type === 'PERSONAL_INFORMATION');
        if (!personalInfoSection || !personalInfoSection.content) {
          // Fallback if not yet generated or found
          return (
            <div className="text-center mb-6 opacity-50">
              <h1 className="text-[24px] font-bold text-gray-900 uppercase tracking-widest">Candidate Name</h1>
              <div className="text-[12px] text-gray-600 mt-2 flex justify-center items-center gap-3">
                <span>Location</span> • <span>email@example.com</span>
              </div>
            </div>
          );
        }
        
        const info = personalInfoSection.content;
        return (
          <div className="text-center mb-6">
            <h1 className="text-[24px] font-bold text-gray-900 uppercase tracking-widest">{info.full_name}</h1>
            <div className="text-[12px] text-gray-600 mt-2 flex justify-center items-center gap-3">
              {info.location && <span>{info.location}</span>}
              {info.location && <span>•</span>}
              
              {info.email && <span>{info.email}</span>}
              {info.email && (info.phone || info.linkedin || info.portfolio || info.github) && <span>•</span>}
              
              {info.phone && <span>{info.phone}</span>}
              {info.phone && (info.linkedin || info.portfolio || info.github) && <span>•</span>}
              
              {info.linkedin && (
                <a href={info.linkedin.startsWith('http') ? info.linkedin : `https://${info.linkedin}`} target="_blank" rel="noreferrer" className="text-jp-accent hover:underline">
                  {info.linkedin.replace(/^https?:\/\/(www\.)?/, '')}
                </a>
              )}
              {info.linkedin && (info.portfolio || info.github) && <span>•</span>}
              
              {info.github && (
                <a href={info.github.startsWith('http') ? info.github : `https://${info.github}`} target="_blank" rel="noreferrer" className="text-jp-accent hover:underline">
                  {info.github.replace(/^https?:\/\/(www\.)?/, '')}
                </a>
              )}
              {info.github && info.portfolio && <span>•</span>}
              
              {info.portfolio && (
                <a href={info.portfolio.startsWith('http') ? info.portfolio : `https://${info.portfolio}`} target="_blank" rel="noreferrer" className="text-jp-accent hover:underline">
                  {info.portfolio.replace(/^https?:\/\/(www\.)?/, '')}
                </a>
              )}
            </div>
          </div>
        );
      })()}

      {sections.length === 0 && !isGenerating && (
        <div className="flex flex-col items-center justify-center h-[600px] text-gray-400 space-y-6">
          <div className="relative">
            <div className="absolute inset-0 bg-jp-accent/20 blur-xl rounded-full"></div>
            <Icon name="article" className="text-[64px] text-jp-accent/50 relative z-10" />
          </div>
          <div className="text-center">
            <h3 className="text-[18px] font-medium text-gray-800 mb-2">Ready to craft your resume</h3>
            <p className="text-[14px] text-gray-500">Share your target job description with the AI to get started.</p>
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
            <h3 className="text-[18px] font-medium text-gray-800 flex items-center justify-center gap-2">
              AI is drafting your resume
              <span className="flex gap-0.5">
                <span className="animate-bounce">.</span><span className="animate-bounce" style={{ animationDelay: '0.1s' }}>.</span><span className="animate-bounce" style={{ animationDelay: '0.2s' }}>.</span>
              </span>
            </h3>
            <div className="w-[300px] space-y-2 opacity-50">
              <div className="h-2 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-2 bg-gray-200 rounded animate-pulse w-5/6 mx-auto"></div>
              <div className="h-2 bg-gray-200 rounded animate-pulse w-4/6 mx-auto"></div>
            </div>
          </div>
        </div>
      )}

      {/* Render generated sections in standard order */}
      {['SUMMARY', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'EDUCATION', 'CERTIFICATIONS', 'CO_CURRICULAR'].map(sectionType => {
        const section = sections.find(s => s.section_type === sectionType);
        if (!section) return null;

        return (
          <div key={sectionType}>
            {renderSectionHeader(section.display_name || sectionType, sectionType)}
            {sectionType === 'SUMMARY' && renderSummary(section.content)}
            {sectionType === 'EXPERIENCE' && renderExperience(section.content)}
            {sectionType === 'PROJECTS' && renderProjects(section.content)}
            {sectionType === 'SKILLS' && renderSkills(section.content)}
            {sectionType === 'EDUCATION' && renderEducation(section.content)}
            {sectionType === 'CERTIFICATIONS' && renderCertifications(section.content)}
            {sectionType === 'CO_CURRICULAR' && renderCoCurricular(section.content)}
          </div>
        );
      })}
    </div>
  );
}

export default ResumePreview;
