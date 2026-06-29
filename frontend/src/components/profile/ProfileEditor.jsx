import React, { useState } from 'react';
import Icon from '../common/Icon';

export default function ProfileEditor({
  profileData,
  setProfileData,
  user,
  editingSection,
  setEditingSection,
  handleSaveProfileChanges
}) {
  const [newSkill, setNewSkill] = useState("");
  const [newRole, setNewRole] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newCoCurricular, setNewCoCurricular] = useState("");
  const [selectedProjectForModal, setSelectedProjectForModal] = useState(null);

  // Timeline experience edit states
  const [editingExpId, setEditingExpId] = useState(null);
  const [expCompany, setExpCompany] = useState("");
  const [expRole, setExpRole] = useState("");
  const [expStartDate, setExpStartDate] = useState("");
  const [expEndDate, setExpEndDate] = useState("");
  const [expDescription, setExpDescription] = useState("");

  // Certifications edit states
  const [editingCertId, setEditingCertId] = useState(null);
  const [certName, setCertName] = useState("");
  const [certIssuer, setCertIssuer] = useState("");
  const [certYear, setCertYear] = useState("");
  const [certUrl, setCertUrl] = useState("");

  // Skills handlers
  const addSkill = () => {
    if (!newSkill.trim()) return;
    if (profileData.resume_data.skills.includes(newSkill.trim())) {
      setNewSkill("");
      return;
    }
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        skills: [...profileData.resume_data.skills, newSkill.trim()]
      }
    });
    setNewSkill("");
  };

  const removeSkill = (skillToRemove) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        skills: profileData.resume_data.skills.filter(s => s !== skillToRemove)
      }
    });
  };

  // Target Roles handlers
  const addRole = () => {
    if (!newRole.trim()) return;
    if (profileData.preferences.preferred_roles.includes(newRole.trim())) {
      setNewRole("");
      return;
    }
    setProfileData({
      ...profileData,
      preferences: {
        ...profileData.preferences,
        preferred_roles: [...profileData.preferences.preferred_roles, newRole.trim()]
      }
    });
    setNewRole("");
  };

  const removeRole = (roleToRemove) => {
    setProfileData({
      ...profileData,
      preferences: {
        ...profileData.preferences,
        preferred_roles: profileData.preferences.preferred_roles.filter(r => r !== roleToRemove)
      }
    });
  };

  // Locations handlers
  const addLocation = () => {
    if (!newLocation.trim()) return;
    if (profileData.preferences.preferred_locations.includes(newLocation.trim())) {
      setNewLocation("");
      return;
    }
    setProfileData({
      ...profileData,
      preferences: {
        ...profileData.preferences,
        preferred_locations: [...profileData.preferences.preferred_locations, newLocation.trim()]
      }
    });
    setNewLocation("");
  };

  const removeLocation = (locToRemove) => {
    setProfileData({
      ...profileData,
      preferences: {
        ...profileData.preferences,
        preferred_locations: profileData.preferences.preferred_locations.filter(l => l !== locToRemove)
      }
    });
  };

  // Experience handlers
  const saveExperience = () => {
    if (!expCompany || !expRole) return;
    const newExp = {
      id: editingExpId === 'new' ? Date.now() : editingExpId,
      company: expCompany,
      role: expRole,
      start_date: expStartDate,
      end_date: expEndDate,
      description: expDescription
    };

    let updatedExpList = [];
    if (editingExpId === 'new') {
      updatedExpList = [...profileData.resume_data.experience, newExp];
    } else {
      updatedExpList = profileData.resume_data.experience.map(e => e.id === editingExpId ? newExp : e);
    }

    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        experience: updatedExpList
      }
    });

    setEditingExpId(null);
    setExpCompany("");
    setExpRole("");
    setExpStartDate("");
    setExpEndDate("");
    setExpDescription("");
  };

  const startEditExperience = (exp) => {
    setEditingExpId(exp.id);
    setExpCompany(exp.company);
    setExpRole(exp.role);
    setExpStartDate(exp.start_date || "");
    setExpEndDate(exp.end_date || "");
    setExpDescription(exp.description || "");
  };

  const deleteExperience = (id) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        experience: profileData.resume_data.experience.filter(e => e.id !== id)
      }
    });
  };

  // Certification handlers
  const saveCertification = () => {
    if (!certName) return;
    const newCert = {
      id: editingCertId === 'new' ? Date.now() : editingCertId,
      name: certName,
      issuer: certIssuer,
      year: certYear,
      url: certUrl
    };

    let updatedCertList = [];
    if (editingCertId === 'new') {
      updatedCertList = [...(profileData.resume_data.certifications || []), newCert];
    } else {
      updatedCertList = (profileData.resume_data.certifications || []).map(c => c.id === editingCertId ? newCert : c);
    }

    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        certifications: updatedCertList
      }
    });

    setEditingCertId(null);
    setCertName("");
    setCertIssuer("");
    setCertYear("");
    setCertUrl("");
  };

  const deleteCertification = (id) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        certifications: (profileData.resume_data.certifications || []).filter(c => c.id !== id)
      }
    });
  };

  // Co-curricular handlers
  const addCoCurricular = () => {
    if (!newCoCurricular.trim()) return;
    if ((profileData.resume_data.co_curricular_activities || []).includes(newCoCurricular.trim())) {
      setNewCoCurricular("");
      return;
    }
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        co_curricular_activities: [...(profileData.resume_data.co_curricular_activities || []), newCoCurricular.trim()]
      }
    });
    setNewCoCurricular("");
  };

  const removeCoCurricular = (actToRemove) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        co_curricular_activities: (profileData.resume_data.co_curricular_activities || []).filter(a => a !== actToRemove)
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* SECTION 1: Personal Info Card */}
      <section className="jp-card p-6 space-y-6 group">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="person" className="text-jp-accent text-[20px]" /> Personal Information
          </h3>
          {editingSection !== 'personal' ? (
            <button
              onClick={() => setEditingSection('personal')}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="edit" className="text-[16px]" /> Edit Info
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => setEditingSection(null)}
                className="jp-btn jp-btn-secondary jp-btn-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProfileChanges}
                className="jp-btn jp-btn-primary jp-btn-sm"
              >
                Save
              </button>
            </div>
          )}
        </div>

        {editingSection === 'personal' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Phone Number</label>
              <input
                type="text"
                value={profileData.resume_data.contact_info.phone || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: {
                    ...profileData.resume_data,
                    contact_info: { ...profileData.resume_data.contact_info, phone: e.target.value }
                  }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">LinkedIn URL</label>
              <input
                type="text"
                value={profileData.resume_data.contact_info.linkedin_url || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: {
                    ...profileData.resume_data,
                    contact_info: { ...profileData.resume_data.contact_info, linkedin_url: e.target.value }
                  }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">GitHub URL</label>
              <input
                type="text"
                value={profileData.resume_data.contact_info.github_url || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: {
                    ...profileData.resume_data,
                    contact_info: { ...profileData.resume_data.contact_info, github_url: e.target.value }
                  }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Portfolio URL</label>
              <input
                type="text"
                value={profileData.resume_data.contact_info.portfolio_url || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: {
                    ...profileData.resume_data,
                    contact_info: { ...profileData.resume_data.contact_info, portfolio_url: e.target.value }
                  }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              />
            </div>
            <div className="md:col-span-2 space-y-1">
              <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Professional Summary</label>
              <textarea
                rows={3}
                value={profileData.resume_data.summary || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: { ...profileData.resume_data, summary: e.target.value }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-jp-accent flex items-center justify-center font-bold text-[22px] text-white">
                {(user?.name || "A").split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
              </div>
              <div>
                <h4 className="font-semibold text-[20px] text-jp-text-primary">{user?.name || "Candidate"}</h4>
                <p className="text-[13px] text-jp-text-secondary font-medium">{profileData.preferences.experience_level} Experience</p>
                <div className="flex gap-4 mt-1.5">
                  {profileData.resume_data.contact_info.phone && (
                    <span className="text-[12px] text-jp-text-tertiary flex items-center gap-1">
                      <Icon name="phone" className="text-[14px]" /> {profileData.resume_data.contact_info.phone}
                    </span>
                  )}
                  <span className="text-[12px] text-jp-text-tertiary flex items-center gap-1">
                    <Icon name="mail" className="text-[14px]" /> {user?.email}
                  </span>
                </div>
              </div>
            </div>

            {profileData.resume_data.summary && (
              <div className="bg-jp-bg-inset p-4 rounded-xl border border-jp-border-subtle">
                <p className="text-[13px] text-jp-text-secondary leading-relaxed">"{profileData.resume_data.summary}"</p>
              </div>
            )}

            <div className="flex gap-4">
              {profileData.resume_data.contact_info.linkedin_url && (
                <a href={profileData.resume_data.contact_info.linkedin_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-medium text-jp-text-secondary hover:text-jp-accent transition-colors">
                  <Icon name="link" className="text-[15px]" /> LinkedIn
                </a>
              )}
              {profileData.resume_data.contact_info.github_url && (
                <a href={profileData.resume_data.contact_info.github_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-medium text-jp-text-secondary hover:text-jp-accent transition-colors">
                  <Icon name="code" className="text-[15px]" /> GitHub
                </a>
              )}
              {profileData.resume_data.contact_info.portfolio_url && (
                <a href={profileData.resume_data.contact_info.portfolio_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-medium text-jp-text-secondary hover:text-jp-accent transition-colors">
                  <Icon name="language" className="text-[15px]" /> Portfolio
                </a>
              )}
            </div>
          </div>
        )}
      </section>

      {/* SECTION 2: Skills Card */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="psychology" className="text-jp-accent text-[20px]" /> Core Technical Skills
          </h3>
          {editingSection !== 'skills' ? (
            <button
              onClick={() => setEditingSection('skills')}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="edit" className="text-[16px]" /> Manage Skills
            </button>
          ) : (
            <button
              onClick={handleSaveProfileChanges}
              className="jp-btn jp-btn-primary jp-btn-sm"
            >
              Done
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          {profileData.resume_data.skills.map((skill, index) => (
            <div key={index} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg text-[13px] font-medium text-jp-text-primary">
              <span>{skill}</span>
              {editingSection === 'skills' && (
                <button onClick={() => removeSkill(skill)} className="text-jp-text-muted hover:text-jp-error ml-1 flex items-center transition-colors">
                  <Icon name="close" className="text-[14px]" />
                </button>
              )}
            </div>
          ))}
        </div>

        {editingSection === 'skills' && (
          <div className="flex gap-2 max-w-sm pt-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              placeholder="Add skill (e.g. AWS)"
              className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl px-3 py-2 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
            />
            <button onClick={addSkill} className="jp-btn jp-btn-secondary py-2 px-4 rounded-xl text-[13px]">Add</button>
          </div>
        )}
      </section>

      {/* SECTION 3: Work Milestones Timeline */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="work" className="text-jp-accent text-[20px]" /> Work Milestones
          </h3>
          {editingExpId === null && (
            <button
              onClick={() => {
                setEditingExpId('new');
                setExpCompany("");
                setExpRole("");
                setExpStartDate("");
                setExpEndDate("");
                setExpDescription("");
              }}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="add" className="text-[16px]" /> Add Experience
            </button>
          )}
        </div>

        {editingExpId !== null && (
          <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-3">
            <h4 className="font-bold text-[13px] text-jp-accent">{editingExpId === 'new' ? "Add Position" : "Edit Position"}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input type="text" placeholder="Company" value={expCompany} onChange={(e) => setExpCompany(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="Job Title" value={expRole} onChange={(e) => setExpRole(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="Start Date" value={expStartDate} onChange={(e) => setExpStartDate(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="End Date" value={expEndDate} onChange={(e) => setExpEndDate(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <textarea rows={3} placeholder="Responsibilities" value={expDescription} onChange={(e) => setExpDescription(e.target.value)} className="md:col-span-2 bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setEditingExpId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
              <button
                onClick={() => {
                  saveExperience();
                  setTimeout(() => handleSaveProfileChanges(), 50);
                }}
                className="jp-btn jp-btn-primary jp-btn-sm"
              >
                Save
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4 pt-2">
          {profileData.resume_data.experience.map((exp) => (
            <div key={exp.id} className="relative pl-6 border-l-2 border-jp-border-subtle pb-4 last:pb-0">
              <div className="absolute -left-[7px] top-[5px] w-3 h-3 rounded-full bg-jp-accent ring-4 ring-jp-bg-surface" />
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-[15px] text-jp-text-primary">{exp.role}</h4>
                  <div className="text-[13px] font-medium text-jp-text-secondary">{exp.company}</div>
                  <div className="text-[12px] text-jp-text-tertiary mt-0.5">{exp.start_date} - {exp.end_date}</div>
                  <p className="text-[13px] text-jp-text-tertiary leading-relaxed mt-2">{exp.description}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => startEditExperience(exp)} className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors">
                    <Icon name="edit" className="text-[16px]" />
                  </button>
                  <button
                    onClick={() => {
                      deleteExperience(exp.id);
                      setTimeout(() => handleSaveProfileChanges(), 50);
                    }}
                    className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors"
                  >
                    <Icon name="delete" className="text-[16px]" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 4: Education History */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="school" className="text-jp-accent text-[20px]" /> Education History
          </h3>
          <button
            onClick={() => alert("Feature coming soon! Modify education during onboarding or check back later.")}
            className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
          >
            <Icon name="add" className="text-[16px]" /> Add Education
          </button>
        </div>

        {(!profileData?.resume_data?.education || profileData.resume_data.education.length === 0) ? (
          <div className="text-center py-8 bg-jp-bg-inset rounded-xl border border-dashed border-jp-border-subtle">
            <Icon name="school" className="text-[32px] text-jp-text-muted mb-2" />
            <p className="text-[13px] text-jp-text-secondary font-medium">No education details added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {profileData.resume_data.education.map((edu, idx) => (
              <div key={edu.id || idx} className="p-4 border border-jp-border bg-jp-bg-surface rounded-xl flex justify-between items-start group">
                <div>
                  <h4 className="font-semibold text-[15px] text-jp-text-primary">{edu.degree}</h4>
                  <div className="text-[13px] font-medium text-jp-text-secondary mt-0.5">{edu.institution}</div>
                  {edu.year && <div className="text-[12px] text-jp-text-tertiary mt-1">Graduation Year: {edu.year}</div>}
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => alert("Feature coming soon!")} className="p-1 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-md transition-colors">
                    <Icon name="edit" className="text-[14px]" />
                  </button>
                  <button onClick={() => alert("Feature coming soon!")} className="p-1 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-md transition-colors">
                    <Icon name="delete" className="text-[14px]" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* SECTION 5: Featured Projects */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="folder_open" className="text-jp-accent text-[20px]" /> Featured Projects
          </h3>
          <button
            onClick={() => alert("Feature coming soon! Modify projects during onboarding or check back later.")}
            className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
          >
            <Icon name="add" className="text-[16px]" /> Add Project
          </button>
        </div>

        {(!profileData?.resume_data?.projects || profileData.resume_data.projects.length === 0) ? (
          <div className="text-center py-8 bg-jp-bg-inset rounded-xl border border-dashed border-jp-border-subtle">
            <Icon name="folder" className="text-[32px] text-jp-text-muted mb-2" />
            <p className="text-[13px] text-jp-text-secondary font-medium">No projects added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {profileData.resume_data.projects.map((proj, idx) => (
              <div 
                key={proj.id || idx} 
                onClick={() => setSelectedProjectForModal(proj)}
                className="p-5 border border-jp-border bg-jp-bg-surface rounded-xl flex flex-col justify-between hover:border-jp-accent/40 transition-colors group relative cursor-pointer"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <Icon name="folder" className="text-jp-accent text-[20px]" />
                      <h4 className="font-semibold text-[15px] text-jp-text-primary group-hover:text-jp-accent transition-colors">{proj.title}</h4>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          alert("Feature coming soon!");
                        }} 
                        className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors"
                      >
                        <Icon name="edit" className="text-[14px]" />
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          alert("Feature coming soon!");
                        }} 
                        className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors"
                      >
                        <Icon name="delete" className="text-[14px]" />
                      </button>
                    </div>
                  </div>
                  <p className="text-[13px] text-jp-text-tertiary leading-relaxed mt-3">
                    {proj.description && proj.description.length > 120 ? (
                      <>
                        {proj.description.slice(0, 120)}...{" "}
                        <span className="text-jp-accent font-medium hover:underline inline-block">
                          Read more
                        </span>
                      </>
                    ) : (
                      proj.description
                    )}
                  </p>
                </div>
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-4 pt-4 border-t border-jp-border-subtle">
                    {proj.technologies.map((tech, i) => (
                      <span key={i} className="bg-jp-bg-inset border border-jp-border text-[11px] font-medium px-2 py-0.5 rounded-lg text-jp-text-secondary">{tech}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* SECTION 6: Certifications */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="verified" className="text-jp-accent text-[20px]" /> Certifications
          </h3>
          {editingCertId === null && (
            <button
              onClick={() => {
                setEditingCertId('new');
                setCertName("");
                setCertIssuer("");
                setCertYear("");
                setCertUrl("");
              }}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="add" className="text-[16px]" /> Add Certification
            </button>
          )}
        </div>

        {editingCertId !== null && (
          <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-3">
            <h4 className="font-bold text-[13px] text-jp-accent">{editingCertId === 'new' ? "Add Certification" : "Edit Certification"}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input type="text" placeholder="Certification Name" value={certName} onChange={(e) => setCertName(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="Issuer (e.g. AWS, Google)" value={certIssuer} onChange={(e) => setCertIssuer(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="Year" value={certYear} onChange={(e) => setCertYear(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
              <input type="text" placeholder="Verification URL" value={certUrl} onChange={(e) => setCertUrl(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setEditingCertId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
              <button
                onClick={() => {
                  saveCertification();
                  setTimeout(() => handleSaveProfileChanges(), 50);
                }}
                className="jp-btn jp-btn-primary jp-btn-sm"
              >
                Save
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {(!profileData?.resume_data?.certifications || profileData.resume_data.certifications.length === 0) ? (
            <div className="text-center py-8 bg-jp-bg-inset rounded-xl border border-dashed border-jp-border-subtle col-span-2">
              <Icon name="verified" className="text-[32px] text-jp-text-muted mb-2" />
              <p className="text-[13px] text-jp-text-secondary font-medium">No certifications listed yet.</p>
            </div>
          ) : (
            profileData.resume_data.certifications.map((cert) => (
              <div key={cert.id} className="p-4 border border-jp-border bg-jp-bg-surface rounded-xl flex justify-between items-start group">
                <div>
                  <h4 className="font-semibold text-[15px] text-jp-text-primary">{cert.name}</h4>
                  <div className="text-[13px] font-medium text-jp-text-secondary mt-0.5">{cert.issuer} {cert.year && `• ${cert.year}`}</div>
                  {cert.url && (
                    <a href={cert.url} target="_blank" rel="noreferrer" className="text-[12px] text-jp-accent hover:text-jp-accent-hover transition-colors flex items-center gap-1 mt-2 font-medium">
                      <Icon name="link" className="text-[14px]" /> Verify Credential
                    </a>
                  )}
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => {
                      setEditingCertId(cert.id);
                      setCertName(cert.name);
                      setCertIssuer(cert.issuer || "");
                      setCertYear(cert.year || "");
                      setCertUrl(cert.url || "");
                    }} 
                    className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors"
                  >
                    <Icon name="edit" className="text-[14px]" />
                  </button>
                  <button 
                    onClick={() => {
                      deleteCertification(cert.id);
                      setTimeout(() => handleSaveProfileChanges(), 50);
                    }} 
                    className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors"
                  >
                    <Icon name="delete" className="text-[14px]" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* SECTION 7: Co-curricular Activities */}
      <section className="jp-card p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="emoji_events" className="text-jp-accent text-[20px]" /> Co-curricular Activities
          </h3>
          {editingSection !== 'co_curricular' ? (
            <button
              onClick={() => setEditingSection('co_curricular')}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="edit" className="text-[16px]" /> Manage Activities
            </button>
          ) : (
            <button
              onClick={handleSaveProfileChanges}
              className="jp-btn jp-btn-primary jp-btn-sm"
            >
              Done
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          {(!profileData?.resume_data?.co_curricular_activities || profileData.resume_data.co_curricular_activities.length === 0) ? (
            <p className="text-[13px] text-jp-text-tertiary">No co-curricular activities listed yet.</p>
          ) : (
            profileData.resume_data.co_curricular_activities.map((act, index) => (
              <div key={index} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg text-[13px] font-medium text-jp-text-primary">
                <span>{act}</span>
                {editingSection === 'co_curricular' && (
                  <button onClick={() => removeCoCurricular(act)} className="text-jp-text-muted hover:text-jp-error ml-1 flex items-center transition-colors">
                    <Icon name="close" className="text-[14px]" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        {editingSection === 'co_curricular' && (
          <div className="flex gap-2 max-w-sm pt-2">
            <input
              type="text"
              value={newCoCurricular}
              onChange={(e) => setNewCoCurricular(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCoCurricular())}
              placeholder="Add activity (e.g. Hackathon winner)"
              className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl px-3 py-2 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
            />
            <button onClick={() => { addCoCurricular(); setTimeout(() => handleSaveProfileChanges(), 50); }} className="jp-btn jp-btn-secondary py-2 px-4 rounded-xl text-[13px]">Add</button>
          </div>
        )}
      </section>

      {/* SECTION 8: Preferences Card */}
      <section className="jp-card p-6 space-y-6">
        <div className="flex justify-between items-center pb-2 border-b border-jp-border-subtle">
          <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
            <Icon name="star" className="text-jp-accent text-[20px]" /> Search Preferences
          </h3>
          {editingSection !== 'preferences' ? (
            <button
              onClick={() => setEditingSection('preferences')}
              className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
            >
              <Icon name="edit" className="text-[16px]" /> Edit Preferences
            </button>
          ) : (
            <div className="flex gap-2">
              <button onClick={() => setEditingSection(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
              <button onClick={handleSaveProfileChanges} className="jp-btn jp-btn-primary jp-btn-sm">Save</button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Preferred Roles */}
          <div className="space-y-3">
            <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Target Roles</label>
            <div className="flex flex-wrap gap-2">
              {profileData.preferences.preferred_roles.map((role, idx) => (
                <div key={idx} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg text-[13px] font-medium text-jp-text-primary">
                  <span>{role}</span>
                  {editingSection === 'preferences' && (
                    <button onClick={() => removeRole(role)} className="text-jp-text-muted hover:text-jp-error ml-1 transition-colors">
                      <Icon name="close" className="text-[14px]" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            {editingSection === 'preferences' && (
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRole())}
                  placeholder="e.g. Frontend Engineer"
                  className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl px-3 py-2 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
                />
                <button onClick={addRole} className="jp-btn jp-btn-secondary py-2 px-3 rounded-xl text-[13px]">Add</button>
              </div>
            )}
          </div>

          {/* Preferred Locations */}
          <div className="space-y-3">
            <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Locations</label>
            <div className="flex flex-wrap gap-2">
              {profileData.preferences.preferred_locations.map((loc, idx) => (
                <div key={idx} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg text-[13px] font-medium text-jp-text-primary">
                  <span>{loc}</span>
                  {editingSection === 'preferences' && (
                    <button onClick={() => removeLocation(loc)} className="text-jp-text-muted hover:text-jp-error ml-1 transition-colors">
                      <Icon name="close" className="text-[14px]" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            {editingSection === 'preferences' && (
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                  placeholder="e.g. Remote, New York"
                  className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl px-3 py-2 text-[13px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
                />
                <button onClick={addLocation} className="jp-btn jp-btn-secondary py-2 px-3 rounded-xl text-[13px]">Add</button>
              </div>
            )}
          </div>

          {/* Experience Level */}
          <div className="space-y-3 md:col-span-2 pt-2">
            <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Experience Level</label>
            {editingSection === 'preferences' ? (
              <select
                value={profileData.preferences.experience_level || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  preferences: { ...profileData.preferences, experience_level: e.target.value }
                })}
                className="w-full max-w-sm bg-jp-bg-inset border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent focus:outline-none transition-colors"
              >
                <option value="">Select Level...</option>
                <option value="Fresher">Fresher (0 Years)</option>
                <option value="0-2 Years">Entry Level (0-2 Years)</option>
                <option value="2-5 Years">Mid Level (2-5 Years)</option>
                <option value="5+ Years">Senior Level (5+ Years)</option>
              </select>
            ) : (
              <div className="text-[14px] font-medium text-jp-text-primary">
                {profileData.preferences.experience_level || <span className="text-jp-text-tertiary">Not specified</span>}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Project Detail Modal */}
      {selectedProjectForModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-jp-bg-surface border border-jp-border w-full max-w-2xl rounded-2xl p-8 relative shadow-2xl">
            <button 
              onClick={() => setSelectedProjectForModal(null)} 
              className="absolute top-6 right-6 p-2 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-full transition-colors"
            >
              <Icon name="close" className="text-[20px]" />
            </button>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-jp-bg-inset border border-jp-border flex items-center justify-center text-jp-accent">
                <Icon name="folder" className="text-[24px]" />
              </div>
              <div>
                <h2 className="text-[22px] font-bold text-jp-text-primary tracking-tight">{selectedProjectForModal.title}</h2>
              </div>
            </div>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider mb-2">Description</h4>
                <p className="text-[14px] text-jp-text-primary leading-relaxed whitespace-pre-wrap bg-jp-bg-inset p-4 rounded-xl border border-jp-border-subtle">
                  {selectedProjectForModal.description || "No description provided."}
                </p>
              </div>

              {selectedProjectForModal.technologies && selectedProjectForModal.technologies.length > 0 && (
                <div>
                  <h4 className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider mb-3">Technologies Used</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedProjectForModal.technologies.map((t, i) => (
                      <span key={i} className="bg-jp-bg-inset border border-jp-border text-[12px] font-medium px-3 py-1 rounded-lg text-jp-text-primary">{t}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
