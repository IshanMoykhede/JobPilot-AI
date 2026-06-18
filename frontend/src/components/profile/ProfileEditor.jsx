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
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-6 shadow-sm relative group">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="person" className="text-primary" /> Personal Information
          </h3>
          {editingSection !== 'personal' ? (
            <button
              onClick={() => setEditingSection('personal')}
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="edit" className="text-[16px]" /> Edit Info
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => setEditingSection(null)}
                className="px-3 py-1 border border-outline-variant text-[13px] rounded-lg hover:bg-surface-container"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProfileChanges}
                className="px-3 py-1 bg-primary text-on-primary text-[13px] font-semibold rounded-lg hover:opacity-90"
              >
                Save
              </button>
            </div>
          )}
        </div>

        {editingSection === 'personal' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-outline">Phone Number</label>
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
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2.5 text-[14px] outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-outline">LinkedIn URL</label>
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
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2.5 text-[14px] outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-outline">GitHub URL</label>
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
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2.5 text-[14px] outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-outline">Portfolio URL</label>
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
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2.5 text-[14px] outline-none"
              />
            </div>
            <div className="md:col-span-2 space-y-1">
              <label className="text-[12px] font-bold text-outline">Professional Summary</label>
              <textarea
                rows={3}
                value={profileData.resume_data.summary || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  resume_data: { ...profileData.resume_data, summary: e.target.value }
                })}
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2.5 text-[14px] outline-none"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-[22px]">
                {(user?.name || "A").split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
              </div>
              <div>
                <h4 className="font-bold text-[20px] text-on-surface">{user?.name || "Candidate"}</h4>
                <p className="text-[13px] text-on-surface-variant font-medium">{profileData.preferences.experience_level} Experience</p>
                <div className="flex gap-4 mt-1">
                  {profileData.resume_data.contact_info.phone && (
                    <span className="text-[12px] text-outline flex items-center gap-1">
                      <Icon name="phone" className="text-[15px]" /> {profileData.resume_data.contact_info.phone}
                    </span>
                  )}
                  <span className="text-[12px] text-outline flex items-center gap-1">
                    <Icon name="mail" className="text-[15px]" /> {user?.email}
                  </span>
                </div>
              </div>
            </div>

            {profileData.resume_data.summary && (
              <div className="bg-surface-container-low/50 p-4 rounded-xl border border-outline-variant/30">
                <p className="text-[13px] text-on-surface-variant leading-relaxed italic">"{profileData.resume_data.summary}"</p>
              </div>
            )}

            <div className="flex gap-2">
              {profileData.resume_data.contact_info.linkedin_url && (
                <a href={profileData.resume_data.contact_info.linkedin_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-semibold text-primary hover:underline">
                  <Icon name="link" className="text-[15px]" /> LinkedIn
                </a>
              )}
              {profileData.resume_data.contact_info.github_url && (
                <a href={profileData.resume_data.contact_info.github_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-semibold text-primary hover:underline ml-4">
                  <Icon name="code" className="text-[15px]" /> GitHub
                </a>
              )}
              {profileData.resume_data.contact_info.portfolio_url && (
                <a href={profileData.resume_data.contact_info.portfolio_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[13px] font-semibold text-primary hover:underline ml-4">
                  <Icon name="language" className="text-[15px]" /> Portfolio
                </a>
              )}
            </div>
          </div>
        )}
      </section>

      {/* SECTION 2: Skills Card */}
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="psychology" className="text-primary" /> Core Technical Skills
          </h3>
          {editingSection !== 'skills' ? (
            <button
              onClick={() => setEditingSection('skills')}
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="edit" className="text-[16px]" /> Manage Skills
            </button>
          ) : (
            <button
              onClick={handleSaveProfileChanges}
              className="px-3 py-1 bg-primary text-on-primary text-[13px] font-semibold rounded-lg hover:opacity-90"
            >
              Done
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          {profileData.resume_data.skills.map((skill, index) => (
            <div key={index} className="flex items-center gap-1 bg-secondary-container/5 text-secondary border border-secondary-container/20 py-1.5 px-3 rounded-lg text-[13px] font-semibold">
              <span>{skill}</span>
              {editingSection === 'skills' && (
                <button onClick={() => removeSkill(skill)} className="text-on-surface-variant hover:text-error ml-1 flex items-center">
                  <Icon name="close" className="text-[14px]" />
                </button>
              )}
            </div>
          ))}
        </div>

        {editingSection === 'skills' && (
          <div className="flex gap-2 max-w-xs pt-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              placeholder="Add skill (e.g. AWS)"
              className="flex-1 bg-surface-container border border-outline-variant rounded-lg px-3 py-1.5 text-[13px] outline-none"
            />
            <button onClick={addSkill} className="bg-primary/10 text-primary px-3 py-1.5 rounded-lg text-[13px] font-bold hover:bg-primary/20">Add</button>
          </div>
        )}
      </section>

      {/* SECTION 3: Work Milestones Timeline */}
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="work" className="text-primary" /> Work Milestones
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
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="add" className="text-[16px]" /> Add Experience
            </button>
          )}
        </div>

        {editingExpId !== null && (
          <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-3">
            <h4 className="font-bold text-[13px] text-primary">{editingExpId === 'new' ? "Add Position" : "Edit Position"}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input type="text" placeholder="Company" value={expCompany} onChange={(e) => setExpCompany(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="Job Title" value={expRole} onChange={(e) => setExpRole(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="Start Date" value={expStartDate} onChange={(e) => setExpStartDate(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="End Date" value={expEndDate} onChange={(e) => setExpEndDate(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <textarea rows={3} placeholder="Responsibilities" value={expDescription} onChange={(e) => setExpDescription(e.target.value)} className="md:col-span-2 bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <button onClick={() => setEditingExpId(null)} className="px-3 py-1 border border-outline-variant rounded-lg text-[12px]">Cancel</button>
              <button
                onClick={() => {
                  saveExperience();
                  setTimeout(() => handleSaveProfileChanges(), 50);
                }}
                className="px-3 py-1 bg-primary text-on-primary rounded-lg text-[12px] font-semibold"
              >
                Save
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4 pt-2">
          {profileData.resume_data.experience.map((exp) => (
            <div key={exp.id} className="relative pl-6 border-l-2 border-primary/20 pb-4 last:pb-0">
              <div className="absolute -left-[7px] top-[5px] w-3 h-3 rounded-full bg-primary" />
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[15px] text-on-surface">{exp.role}</h4>
                  <div className="text-[13px] font-semibold text-primary">{exp.company}</div>
                  <div className="text-[12px] text-outline font-medium mt-0.5">{exp.start_date} - {exp.end_date}</div>
                  <p className="text-[13px] text-on-surface-variant leading-relaxed mt-2">{exp.description}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => startEditExperience(exp)} className="p-1 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-md">
                    <Icon name="edit" className="text-[16px]" />
                  </button>
                  <button
                    onClick={() => {
                      deleteExperience(exp.id);
                      setTimeout(() => handleSaveProfileChanges(), 50);
                    }}
                    className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-md"
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
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="school" className="text-primary" /> Education History
          </h3>
          <button
            onClick={() => alert("Feature coming soon! Modify education during onboarding or check back later.")}
            className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
          >
            <Icon name="add" className="text-[16px]" /> Add Education
          </button>
        </div>

        {(!profileData?.resume_data?.education || profileData.resume_data.education.length === 0) ? (
          <div className="text-center py-6 bg-surface-container-low/20 rounded-xl border border-dashed border-outline-variant/50">
            <Icon name="school" className="text-[32px] text-outline/60 mb-2" />
            <p className="text-[13px] text-on-surface-variant font-medium">No education details added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {profileData.resume_data.education.map((edu, idx) => (
              <div key={edu.id || idx} className="p-4 border border-outline-variant/40 bg-surface-container-low/30 rounded-xl flex justify-between items-start hover:shadow-md transition-all group">
                <div>
                  <h4 className="font-bold text-[15px] text-on-surface">{edu.degree}</h4>
                  <div className="text-[13px] font-semibold text-primary mt-0.5">{edu.institution}</div>
                  {edu.year && <div className="text-[12px] text-outline font-medium mt-1">Graduation Year: {edu.year}</div>}
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => alert("Feature coming soon!")} className="p-1 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-md">
                    <Icon name="edit" className="text-[14px]" />
                  </button>
                  <button onClick={() => alert("Feature coming soon!")} className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-md">
                    <Icon name="delete" className="text-[14px]" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* SECTION 5: Featured Projects */}
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="folder_open" className="text-primary" /> Featured Projects
          </h3>
          <button
            onClick={() => alert("Feature coming soon! Modify projects during onboarding or check back later.")}
            className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
          >
            <Icon name="add" className="text-[16px]" /> Add Project
          </button>
        </div>

        {(!profileData?.resume_data?.projects || profileData.resume_data.projects.length === 0) ? (
          <div className="text-center py-6 bg-surface-container-low/20 rounded-xl border border-dashed border-outline-variant/50">
            <Icon name="folder" className="text-[32px] text-outline/60 mb-2" />
            <p className="text-[13px] text-on-surface-variant font-medium">No projects added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {profileData.resume_data.projects.map((proj, idx) => (
              <div 
                key={proj.id || idx} 
                onClick={() => setSelectedProjectForModal(proj)}
                className="p-4 border border-outline-variant/40 bg-surface-container-low/30 rounded-xl flex flex-col justify-between hover:shadow-md hover:border-primary/40 transition-all group relative cursor-pointer"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <Icon name="folder" className="text-primary text-[20px]" />
                      <h4 className="font-bold text-[15px] text-on-surface group-hover:text-primary transition-colors">{proj.title}</h4>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          alert("Feature coming soon!");
                        }} 
                        className="p-1 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-md"
                      >
                        <Icon name="edit" className="text-[14px]" />
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          alert("Feature coming soon!");
                        }} 
                        className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-md"
                      >
                        <Icon name="delete" className="text-[14px]" />
                      </button>
                    </div>
                  </div>
                  <p className="text-[13px] text-on-surface-variant leading-relaxed mt-2">
                    {proj.description && proj.description.length > 120 ? (
                      <>
                        {proj.description.slice(0, 120)}...{" "}
                        <span className="text-primary font-semibold hover:underline inline-block">
                          Read more
                        </span>
                      </>
                    ) : (
                      proj.description
                    )}
                  </p>
                </div>
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-outline-variant/20">
                    {proj.technologies.map((tech, i) => (
                      <span key={i} className="bg-surface-container text-[11px] font-semibold px-2 py-0.5 rounded text-outline">{tech}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* SECTION 6: Certifications */}
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="verified" className="text-primary" /> Certifications
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
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="add" className="text-[16px]" /> Add Certification
            </button>
          )}
        </div>

        {editingCertId !== null && (
          <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-3">
            <h4 className="font-bold text-[13px] text-primary">{editingCertId === 'new' ? "Add Certification" : "Edit Certification"}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input type="text" placeholder="Certification Name" value={certName} onChange={(e) => setCertName(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="Issuer (e.g. AWS, Google)" value={certIssuer} onChange={(e) => setCertIssuer(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="Year" value={certYear} onChange={(e) => setCertYear(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
              <input type="text" placeholder="Verification URL" value={certUrl} onChange={(e) => setCertUrl(e.target.value)} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[13px] outline-none" />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <button onClick={() => setEditingCertId(null)} className="px-3 py-1 border border-outline-variant rounded-lg text-[12px]">Cancel</button>
              <button
                onClick={() => {
                  saveCertification();
                  setTimeout(() => handleSaveProfileChanges(), 50);
                }}
                className="px-3 py-1 bg-primary text-on-primary rounded-lg text-[12px] font-semibold"
              >
                Save
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {(!profileData?.resume_data?.certifications || profileData.resume_data.certifications.length === 0) ? (
            <div className="text-center py-6 bg-surface-container-low/20 rounded-xl border border-dashed border-outline-variant/50 col-span-2">
              <Icon name="verified" className="text-[32px] text-outline/60 mb-2" />
              <p className="text-[13px] text-on-surface-variant font-medium">No certifications listed yet.</p>
            </div>
          ) : (
            profileData.resume_data.certifications.map((cert) => (
              <div key={cert.id} className="p-4 border border-outline-variant/40 bg-surface-container-low/30 rounded-xl flex justify-between items-start hover:shadow-md transition-all group">
                <div>
                  <h4 className="font-bold text-[15px] text-on-surface">{cert.name}</h4>
                  <div className="text-[13px] font-semibold text-primary mt-0.5">{cert.issuer} {cert.year && `• ${cert.year}`}</div>
                  {cert.url && (
                    <a href={cert.url} target="_blank" rel="noreferrer" className="text-[12px] text-primary hover:underline flex items-center gap-0.5 mt-1.5 font-semibold">
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
                    className="p-1 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-md"
                  >
                    <Icon name="edit" className="text-[14px]" />
                  </button>
                  <button 
                    onClick={() => {
                      deleteCertification(cert.id);
                      setTimeout(() => handleSaveProfileChanges(), 50);
                    }} 
                    className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-md"
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
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="emoji_events" className="text-primary" /> Co-curricular Activities
          </h3>
          {editingSection !== 'co_curricular' ? (
            <button
              onClick={() => setEditingSection('co_curricular')}
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="edit" className="text-[16px]" /> Manage Activities
            </button>
          ) : (
            <button
              onClick={handleSaveProfileChanges}
              className="px-3 py-1 bg-primary text-on-primary text-[13px] font-semibold rounded-lg hover:opacity-90"
            >
              Done
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          {(!profileData?.resume_data?.co_curricular_activities || profileData.resume_data.co_curricular_activities.length === 0) ? (
            <p className="text-[13px] text-outline italic">No co-curricular activities listed yet.</p>
          ) : (
            profileData.resume_data.co_curricular_activities.map((act, index) => (
              <div key={index} className="flex items-center gap-1 bg-secondary-container/5 text-secondary border border-secondary-container/20 py-1.5 px-3 rounded-lg text-[13px] font-semibold">
                <span>{act}</span>
                {editingSection === 'co_curricular' && (
                  <button onClick={() => removeCoCurricular(act)} className="text-on-surface-variant hover:text-error ml-1 flex items-center">
                    <Icon name="close" className="text-[14px]" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        {editingSection === 'co_curricular' && (
          <div className="flex gap-2 max-w-xs pt-2">
            <input
              type="text"
              value={newCoCurricular}
              onChange={(e) => setNewCoCurricular(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCoCurricular())}
              placeholder="Add activity (e.g. Hackathon winner)"
              className="flex-1 bg-surface-container border border-outline-variant rounded-lg px-3 py-1.5 text-[13px] outline-none"
            />
            <button onClick={() => { addCoCurricular(); setTimeout(() => handleSaveProfileChanges(), 50); }} className="bg-primary/10 text-primary px-3 py-1.5 rounded-lg text-[13px] font-bold hover:bg-primary/20">Add</button>
          </div>
        )}
      </section>

      {/* SECTION 8: Preferences Card */}
      <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant/20">
          <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
            <Icon name="star" className="text-primary" /> Search Preferences
          </h3>
          {editingSection !== 'preferences' ? (
            <button
              onClick={() => setEditingSection('preferences')}
              className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
            >
              <Icon name="edit" className="text-[16px]" /> Edit Preferences
            </button>
          ) : (
            <button
              onClick={handleSaveProfileChanges}
              className="px-3 py-1 bg-primary text-on-primary text-[13px] font-semibold rounded-lg hover:opacity-90"
            >
              Save Options
            </button>
          )}
        </div>

        {editingSection === 'preferences' ? (
          <div className="space-y-4 pt-2">
            <div className="space-y-1">
              <label className="text-[12px] font-bold text-outline">Experience Segment</label>
              <select
                value={profileData.preferences.experience_level}
                onChange={(e) => setProfileData({
                  ...profileData,
                  preferences: { ...profileData.preferences, experience_level: e.target.value }
                })}
                className="w-full bg-surface-container border border-outline-variant rounded-lg p-2 text-[14px] outline-none"
              >
                <option value="Fresher">Fresher (No professional experience)</option>
                <option value="0-2 Years">Junior (0-2 Years)</option>
                <option value="2-5 Years">Mid-Level (2-5 Years)</option>
                <option value="5+ Years">Senior (5+ Years)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[12px] font-bold text-outline">Target Roles</label>
              <div className="flex flex-wrap gap-2">
                {profileData.preferences.preferred_roles.map((r, i) => (
                  <span key={i} className="flex items-center gap-1 bg-surface-container px-2.5 py-1 rounded-lg text-[12px] font-bold">
                    {r} <button onClick={() => removeRole(r)}><Icon name="close" className="text-[13px] text-error" /></button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2 max-w-xs">
                <input
                  type="text"
                  placeholder="Add Role"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRole())}
                  className="flex-1 bg-surface-container border border-outline-variant rounded-lg px-2 py-1 text-[13px] outline-none"
                />
                <button onClick={addRole} className="bg-primary/10 text-primary px-3 py-1 rounded-lg text-[13px] font-bold">Add</button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[12px] font-bold text-outline">Preferred Job Locations</label>
              <div className="flex flex-wrap gap-2">
                {profileData.preferences.preferred_locations.map((l, i) => (
                  <span key={i} className="flex items-center gap-1 bg-surface-container px-2.5 py-1 rounded-lg text-[12px] font-bold">
                    {l} <button onClick={() => removeLocation(l)}><Icon name="close" className="text-[13px] text-error" /></button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2 max-w-xs">
                <input
                  type="text"
                  placeholder="Add Location"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                  className="flex-1 bg-surface-container border border-outline-variant rounded-lg px-2 py-1 text-[13px] outline-none"
                />
                <button onClick={addLocation} className="bg-primary/10 text-primary px-3 py-1 rounded-lg text-[13px] font-bold">Add</button>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <span className="text-[12px] font-bold text-outline block uppercase tracking-wider">Preferred Roles</span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {profileData.preferences.preferred_roles.map((role, idx) => (
                  <span key={idx} className="bg-secondary-container/10 text-secondary border border-secondary-container/20 text-[12px] font-bold px-2.5 py-1 rounded-lg">
                    {role}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-[12px] font-bold text-outline block uppercase tracking-wider">Preferred Locations</span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {profileData.preferences.preferred_locations.map((loc, idx) => (
                  <span key={idx} className="bg-secondary-container/10 text-secondary border border-secondary-container/20 text-[12px] font-bold px-2.5 py-1 rounded-lg">
                    {loc}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Floating Modal for Project Details */}
      {selectedProjectForModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 transition-all"
          onClick={() => setSelectedProjectForModal(null)}
        >
          <div 
            className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl max-w-xl w-full p-6 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-start pb-4 border-b border-outline-variant/20 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-primary/10 rounded-lg text-primary">
                  <Icon name="folder" className="text-[22px]" />
                </div>
                <div>
                  <h4 className="font-bold text-[18px] text-on-surface">{selectedProjectForModal.title}</h4>
                  <span className="text-[11px] font-semibold text-outline">Project Details</span>
                </div>
              </div>
              <button 
                onClick={() => setSelectedProjectForModal(null)} 
                className="p-1.5 hover:bg-surface-container rounded-full text-on-surface-variant hover:text-on-surface transition-colors"
              >
                <Icon name="close" className="text-[20px]" />
              </button>
            </div>

            {/* Body */}
            <div className="space-y-4">
              <div>
                <span className="text-[11px] font-bold text-outline block uppercase tracking-wider mb-1">Description</span>
                <p className="text-[14px] text-on-surface-variant leading-relaxed whitespace-pre-wrap">
                  {selectedProjectForModal.description}
                </p>
              </div>

              {selectedProjectForModal.technologies && selectedProjectForModal.technologies.length > 0 && (
                <div className="pt-4 border-t border-outline-variant/10">
                  <span className="text-[11px] font-bold text-outline block uppercase tracking-wider mb-2">Technologies Used</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedProjectForModal.technologies.map((tech, i) => (
                      <span key={i} className="bg-surface-container text-[12px] font-semibold px-2.5 py-1 rounded text-outline">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-outline-variant/20">
              <button 
                onClick={() => setSelectedProjectForModal(null)}
                className="px-4 py-2 border border-outline-variant text-[13px] font-semibold rounded-lg hover:bg-surface-container text-on-surface transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
