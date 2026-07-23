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
      <div className="group relative border-b-2 border-gray-800 pb-1 mb-3 mt-6">
        <h2 className="text-[14px] font-bold uppercase tracking-wider text-gray-900">{title}</h2>
        <button 
          onClick={() => setEditingSection(isEditing ? null : sectionType)}
          className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity text-[11px] font-medium text-jp-accent flex items-center gap-1 bg-jp-accent/10 px-2 py-0.5 rounded"
        >
          <Icon name="edit" className="text-[12px]" />
          Edit
        </button>
        
        {isEditing && (
          <form 
            onSubmit={(e) => handleEditSubmit(e, sectionType)}
            className="absolute top-full left-0 right-0 mt-2 z-10 bg-white shadow-xl border border-jp-border rounded-lg p-3"
          >
            <p className="text-[11px] text-gray-500 mb-2 font-normal normal-case">What would you like to change about this section?</p>
            <div className="flex gap-2">
              <input 
                type="text" 
                value={editPrompt}
                onChange={e => setEditPrompt(e.target.value)}
                autoFocus
                placeholder="e.g. Make it sound more senior..."
                className="flex-1 border border-jp-border-subtle rounded px-2 py-1.5 text-[12px] focus:border-jp-accent focus:outline-none"
              />
              <button 
                type="submit"
                disabled={isGenerating}
                className="bg-jp-accent text-white px-3 py-1.5 rounded text-[12px] font-medium hover:bg-jp-accent-hover disabled:opacity-50"
              >
                Update
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

  return (
    <div className="bg-white shadow-sm border border-gray-200 min-h-[1056px] w-full p-10 font-sans">
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
        <div className="flex flex-col items-center justify-center h-[400px] text-gray-400 space-y-4">
          <Icon name="article" className="text-[48px] opacity-20" />
          <p className="text-[14px]">Click Generate to build your resume.</p>
        </div>
      )}

      {/* Render generated sections in standard order */}
      {['SUMMARY', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'EDUCATION', 'CERTIFICATIONS'].map(sectionType => {
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
          </div>
        );
      })}
    </div>
  );
}

export default ResumePreview;
