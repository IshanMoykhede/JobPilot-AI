import React, { useState } from 'react';
import Icon from '../common/Icon';

export default function OnboardingWizard({
  activeStep,
  setActiveStep,
  isUploading,
  uploadProgress,
  uploadingStepText,
  profileData,
  setProfileData,
  handleResumeUpload,
  handleCompleteOnboarding,
  triggerToast,
  user
}) {
  const [newSkill, setNewSkill] = useState("");
  const [newRole, setNewRole] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newCoCurricular, setNewCoCurricular] = useState("");

  // Experience edit states
  const [editingExpId, setEditingExpId] = useState(null);
  const [expCompany, setExpCompany] = useState("");
  const [expRole, setExpRole] = useState("");
  const [expStartDate, setExpStartDate] = useState("");
  const [expEndDate, setExpEndDate] = useState("");
  const [expDescription, setExpDescription] = useState("");

  // Education edit states
  const [editingEduId, setEditingEduId] = useState(null);
  const [eduInstitution, setEduInstitution] = useState("");
  const [eduDegree, setEduDegree] = useState("");
  const [eduYear, setEduYear] = useState("");

  // Project edit states
  const [editingProjId, setEditingProjId] = useState(null);
  const [projTitle, setProjTitle] = useState("");
  const [projDescription, setProjDescription] = useState("");
  const [projTech, setProjTech] = useState("");

  // Certifications edit states
  const [editingCertId, setEditingCertId] = useState(null);
  const [certName, setCertName] = useState("");
  const [certIssuer, setCertIssuer] = useState("");
  const [certYear, setCertYear] = useState("");
  const [certUrl, setCertUrl] = useState("");

  // Skill Handlers
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

  // Roles Handlers
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

  // Location Handlers
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

  const deleteExperience = (id) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        experience: profileData.resume_data.experience.filter(e => e.id !== id)
      }
    });
  };

  // Education handlers
  const saveEducation = () => {
    if (!eduInstitution || !eduDegree) return;
    const newEdu = {
      id: editingEduId === 'new' ? Date.now() : editingEduId,
      institution: eduInstitution,
      degree: eduDegree,
      year: eduYear
    };

    let updatedEduList = [];
    if (editingEduId === 'new') {
      updatedEduList = [...profileData.resume_data.education, newEdu];
    } else {
      updatedEduList = profileData.resume_data.education.map(e => e.id === editingEduId ? newEdu : e);
    }

    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        education: updatedEduList
      }
    });

    setEditingEduId(null);
    setEduInstitution("");
    setEduDegree("");
    setEduYear("");
  };

  const deleteEducation = (id) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        education: profileData.resume_data.education.filter(e => e.id !== id)
      }
    });
  };

  // Project handlers
  const saveProject = () => {
    if (!projTitle) return;
    const techArray = projTech ? projTech.split(",").map(t => t.trim()).filter(Boolean) : [];
    const newProj = {
      id: editingProjId === 'new' ? Date.now() : editingProjId,
      title: projTitle,
      description: projDescription,
      technologies: techArray
    };

    let updatedProjList = [];
    if (editingProjId === 'new') {
      updatedProjList = [...profileData.resume_data.projects, newProj];
    } else {
      updatedProjList = profileData.resume_data.projects.map(p => p.id === editingProjId ? newProj : p);
    }

    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        projects: updatedProjList
      }
    });

    setEditingProjId(null);
    setProjTitle("");
    setProjDescription("");
    setProjTech("");
  };

  const deleteProject = (id) => {
    setProfileData({
      ...profileData,
      resume_data: {
        ...profileData.resume_data,
        projects: profileData.resume_data.projects.filter(p => p.id !== id)
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
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Stepper Card */}
      <div className="jp-card p-6">
        <div className="flex justify-between items-center max-w-xl mx-auto">
          {/* Step 1 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 1
                  ? "bg-jp-accent text-white ring-4 ring-jp-accent/20"
                  : activeStep > 1
                  ? "bg-jp-accent text-white"
                  : "bg-jp-bg-surface text-jp-text-muted border border-jp-border"
              }`}
            >
              {activeStep > 1 ? <Icon name="check" /> : <span className="font-bold">1</span>}
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 1 ? "text-jp-accent" : "text-jp-text-muted"}`}>Resume Upload</span>
          </div>

          <div className={`flex-1 h-[2px] mx-2 -mt-6 transition-colors ${activeStep >= 2 ? "bg-jp-accent" : "bg-jp-border-subtle"}`} />

          {/* Step 2 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 2
                  ? "bg-jp-accent text-white ring-4 ring-jp-accent/20"
                  : activeStep > 2
                  ? "bg-jp-accent text-white"
                  : "bg-jp-bg-surface text-jp-text-muted border border-jp-border"
              }`}
            >
              {activeStep > 2 ? <Icon name="check" /> : <span className="font-bold">2</span>}
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 2 ? "text-jp-accent" : "text-jp-text-muted"}`}>AI Verification</span>
          </div>

          <div className={`flex-1 h-[2px] mx-2 -mt-6 transition-colors ${activeStep >= 3 ? "bg-jp-accent" : "bg-jp-border-subtle"}`} />

          {/* Step 3 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 3
                  ? "bg-jp-accent text-white ring-4 ring-jp-accent/20"
                  : "bg-jp-bg-surface text-jp-text-muted border border-jp-border"
              }`}
            >
              <span className="font-bold">3</span>
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 3 ? "text-jp-accent" : "text-jp-text-muted"}`}>Preferences</span>
          </div>
        </div>
      </div>

      {/* STEP 1: UPLOAD RESUME */}
      {activeStep === 1 && (
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-[32px] font-semibold text-jp-text-primary tracking-tight">Create Candidate Context</h2>
            <p className="text-jp-text-secondary max-w-xl mx-auto">
              Upload your resume to extract details instantly. Our AI parses work milestones, projects, and skills to tailor your dashboard context.
            </p>
          </div>

          {isUploading ? (
            <div className="jp-card p-12 text-center space-y-6 max-w-lg mx-auto shadow-lg">
              <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
                <Icon name="cloud_upload" className="text-[64px] text-jp-accent animate-pulse" />
                <div className="absolute inset-0 rounded-full border-4 border-jp-accent/20 border-t-jp-accent animate-spin" />
              </div>
              <div className="space-y-2">
                <h4 className="text-[18px] font-bold text-jp-text-primary">Uploading & Parsing...</h4>
                <div className="w-full bg-jp-bg-inset h-2 rounded-full overflow-hidden">
                  <div className="bg-jp-accent h-full transition-all duration-300 rounded-full" style={{ width: `${uploadProgress}%` }} />
                </div>
                <div className="flex justify-between items-center text-[12px] text-jp-text-muted font-semibold">
                  <span>{uploadingStepText}</span>
                  <span>{uploadProgress}%</span>
                </div>
              </div>
            </div>
          ) : (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files.length > 0) handleResumeUpload(e.dataTransfer.files[0]);
              }}
              className="border-2 border-dashed border-jp-border hover:border-jp-accent bg-jp-bg-surface hover:bg-jp-bg-inset cursor-pointer rounded-2xl p-16 text-center transition-all group max-w-xl mx-auto relative"
            >
              <input
                type="file"
                id="resumeFile"
                className="hidden"
                accept=".pdf,.docx"
                onChange={(e) => {
                  if (e.target.files.length > 0) handleResumeUpload(e.target.files[0]);
                }}
              />
              <label htmlFor="resumeFile" className="cursor-pointer space-y-6 block">
                <div className="w-20 h-20 bg-jp-bg-inset border border-jp-border rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <Icon name="cloud_upload" className="text-[40px] text-jp-accent" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-[20px] font-bold text-jp-text-primary">Drag & drop your resume here</h3>
                  <p className="text-jp-text-secondary text-[14px]">or <span className="text-jp-accent font-medium hover:underline">browse files</span> from your computer</p>
                  <p className="text-[12px] text-jp-text-muted">Supports PDF and DOCX formats up to 10MB</p>
                </div>
              </label>
            </div>
          )}

          <div className="text-center">
            <button
              onClick={() => {
                setActiveStep(2);
                triggerToast("Starting setup with manual profile details.");
              }}
              className="text-jp-text-muted hover:text-jp-text-primary font-medium text-[14px] transition-colors hover:underline"
            >
              Skip resume upload & type details manually
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: VERIFY AND EDIT DATA */}
      {activeStep === 2 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-[28px] font-semibold text-jp-text-primary tracking-tight">Verify Extracted Resume Data</h2>
              <p className="text-jp-text-secondary text-[14px]">Review AI parsed items. Edit information to guarantee complete profile details.</p>
            </div>
            <button
              onClick={() => setActiveStep(3)}
              className="jp-btn jp-btn-primary py-2.5 px-6 rounded-xl text-[14px]"
            >
              Next: Preferences <Icon name="arrow_forward" className="text-[18px]" />
            </button>
          </div>

          {/* Contact Details Card */}
          <section className="jp-card p-6 space-y-6">
            <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2 pb-3 border-b border-jp-border-subtle">
              <Icon name="contact_phone" className="text-jp-accent" /> Contact Details & Summary
            </h3>
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
                  placeholder="+1 (555) 000-0000"
                  className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-2.5 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">LinkedIn Profile</label>
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
                  placeholder="https://linkedin.com/in/username"
                  className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-2.5 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
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
                  placeholder="https://github.com/username"
                  className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-2.5 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Portfolio Website</label>
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
                  placeholder="https://myportfolio.com"
                  className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-2.5 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
              </div>
              <div className="md:col-span-2 space-y-1">
                <label className="text-[12px] font-bold text-jp-text-secondary uppercase tracking-wider">Professional Bio / Summary</label>
                <textarea
                  rows={3}
                  value={profileData.resume_data.summary || ""}
                  onChange={(e) => setProfileData({
                    ...profileData,
                    resume_data: { ...profileData.resume_data, summary: e.target.value }
                  })}
                  placeholder="A quick summary of your professional milestones..."
                  className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-2.5 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
              </div>
            </div>
          </section>

          {/* Skills Card */}
          <section className="jp-card p-6 space-y-4">
            <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2 pb-3 border-b border-jp-border-subtle">
              <Icon name="psychology" className="text-jp-accent" /> Skills
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {profileData.resume_data.skills.map((skill, index) => (
                <div key={index} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg hover:bg-jp-bg-inset transition-colors">
                  <span className="text-[13px] font-medium text-jp-text-primary">{skill}</span>
                  <button onClick={() => removeSkill(skill)} className="text-jp-text-muted hover:text-jp-error transition-colors flex items-center">
                    <Icon name="close" className="text-[14px]" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 max-w-sm">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Type skill and hit enter"
                className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl py-2 px-3 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
              />
              <button onClick={addSkill} className="jp-btn jp-btn-secondary py-2 px-4 rounded-xl text-[14px]">Add</button>
            </div>
          </section>

          {/* Experience Card */}
          <section className="jp-card p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-jp-border-subtle">
              <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
                <Icon name="work" className="text-jp-accent" /> Work History
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
                  <Icon name="add" className="text-[16px]" /> Add Position
                </button>
              )}
            </div>

            {editingExpId !== null && (
              <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-jp-accent">{editingExpId === 'new' ? "Add Position" : "Edit Position"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input type="text" placeholder="Company" value={expCompany} onChange={(e) => setExpCompany(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Role Title" value={expRole} onChange={(e) => setExpRole(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Start Date" value={expStartDate} onChange={(e) => setExpStartDate(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="End Date" value={expEndDate} onChange={(e) => setExpEndDate(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <textarea rows={3} placeholder="Responsibilities" value={expDescription} onChange={(e) => setExpDescription(e.target.value)} className="md:col-span-2 w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingExpId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
                  <button onClick={saveExperience} className="jp-btn jp-btn-primary jp-btn-sm">Save</button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {profileData.resume_data.experience.map((exp) => (
                <div key={exp.id} className="flex justify-between items-start p-4 border border-jp-border bg-jp-bg-surface rounded-xl">
                  <div>
                    <div className="font-semibold text-[15px] text-jp-text-primary">{exp.role}</div>
                    <div className="text-[13px] font-medium text-jp-text-secondary">{exp.company}</div>
                    <div className="text-[12px] text-jp-text-tertiary mt-0.5">{exp.start_date} - {exp.end_date}</div>
                    <p className="text-[13px] text-jp-text-tertiary mt-2 leading-relaxed">{exp.description}</p>
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => {
                        setEditingExpId(exp.id);
                        setExpCompany(exp.company);
                        setExpRole(exp.role);
                        setExpStartDate(exp.start_date || "");
                        setExpEndDate(exp.end_date || "");
                        setExpDescription(exp.description || "");
                      }}
                      className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors"
                    >
                      <Icon name="edit" className="text-[16px]" />
                    </button>
                    <button onClick={() => deleteExperience(exp.id)} className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors">
                      <Icon name="delete" className="text-[16px]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Education Card */}
          <section className="jp-card p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-jp-border-subtle">
              <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
                <Icon name="school" className="text-jp-accent" /> Education History
              </h3>
              {editingEduId === null && (
                <button
                  onClick={() => {
                    setEditingEduId('new');
                    setEduInstitution("");
                    setEduDegree("");
                    setEduYear("");
                  }}
                  className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
                >
                  <Icon name="add" className="text-[16px]" /> Add Degree
                </button>
              )}
            </div>

            {editingEduId !== null && (
              <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-jp-accent">{editingEduId === 'new' ? "Add Education" : "Edit Education"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <input type="text" placeholder="Institution" value={eduInstitution} onChange={(e) => setEduInstitution(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Degree" value={eduDegree} onChange={(e) => setEduDegree(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Graduation Year" value={eduYear} onChange={(e) => setEduYear(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingEduId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
                  <button onClick={saveEducation} className="jp-btn jp-btn-primary jp-btn-sm">Save</button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {profileData.resume_data.education.map((edu) => (
                <div key={edu.id} className="flex justify-between items-center p-4 border border-jp-border bg-jp-bg-surface rounded-xl">
                  <div>
                    <div className="font-semibold text-[15px] text-jp-text-primary">{edu.degree}</div>
                    <div className="text-[13px] font-medium text-jp-text-secondary">{edu.institution}</div>
                    <div className="text-[12px] text-jp-text-tertiary">Graduated: {edu.year}</div>
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => {
                        setEditingEduId(edu.id);
                        setEduInstitution(edu.institution);
                        setEduDegree(edu.degree);
                        setEduYear(edu.year || "");
                      }}
                      className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors"
                    >
                      <Icon name="edit" className="text-[16px]" />
                    </button>
                    <button onClick={() => deleteEducation(edu.id)} className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors">
                      <Icon name="delete" className="text-[16px]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Projects Card */}
          <section className="jp-card p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-jp-border-subtle">
              <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
                <Icon name="folder_open" className="text-jp-accent" /> Projects
              </h3>
              {editingProjId === null && (
                <button
                  onClick={() => {
                    setEditingProjId('new');
                    setProjTitle("");
                    setProjDescription("");
                    setProjTech("");
                  }}
                  className="text-jp-accent font-semibold text-[13px] flex items-center gap-1 hover:text-jp-accent-hover transition-colors"
                >
                  <Icon name="add" className="text-[16px]" /> Add Project
                </button>
              )}
            </div>

            {editingProjId !== null && (
              <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-jp-accent">{editingProjId === 'new' ? "Add Project" : "Edit Project"}</h4>
                <div className="grid grid-cols-1 gap-4">
                  <input type="text" placeholder="Project Title" value={projTitle} onChange={(e) => setProjTitle(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Technologies (comma-separated)" value={projTech} onChange={(e) => setProjTech(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <textarea rows={2} placeholder="Project Description" value={projDescription} onChange={(e) => setProjDescription(e.target.value)} className="w-full bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingProjId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
                  <button onClick={saveProject} className="jp-btn jp-btn-primary jp-btn-sm">Save</button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profileData.resume_data.projects.map((proj) => (
                <div key={proj.id} className="p-4 border border-jp-border bg-jp-bg-surface rounded-xl flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center">
                      <h4 className="font-semibold text-[15px] text-jp-text-primary">{proj.title}</h4>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setEditingProjId(proj.id);
                            setProjTitle(proj.title);
                            setProjDescription(proj.description || "");
                            setProjTech(proj.technologies ? proj.technologies.join(", ") : "");
                          }}
                          className="p-1.5 text-jp-text-muted hover:text-jp-text-primary hover:bg-jp-bg-inset rounded-lg transition-colors"
                        >
                          <Icon name="edit" className="text-[16px]" />
                        </button>
                        <button onClick={() => deleteProject(proj.id)} className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors">
                          <Icon name="delete" className="text-[16px]" />
                        </button>
                      </div>
                    </div>
                    <p className="text-[13px] text-jp-text-tertiary mt-2">{proj.description}</p>
                  </div>
                  {proj.technologies && proj.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-4 pt-4 border-t border-jp-border-subtle">
                      {proj.technologies.map((t, i) => (
                        <span key={i} className="bg-jp-bg-inset border border-jp-border text-[11px] font-medium px-2 py-0.5 rounded-lg text-jp-text-secondary">{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Certifications Card */}
          <section className="jp-card p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-jp-border-subtle">
              <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2">
                <Icon name="verified" className="text-jp-accent" /> Certifications
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
              <div className="p-4 bg-jp-bg-inset border border-jp-border rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-jp-accent">{editingCertId === 'new' ? "Add Certification" : "Edit Certification"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input type="text" placeholder="Certification Name" value={certName} onChange={(e) => setCertName(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Issuer (e.g. AWS, Google)" value={certIssuer} onChange={(e) => setCertIssuer(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Year" value={certYear} onChange={(e) => setCertYear(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                  <input type="text" placeholder="Verification URL" value={certUrl} onChange={(e) => setCertUrl(e.target.value)} className="bg-jp-bg-raised border border-jp-border rounded-xl p-2.5 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingCertId(null)} className="jp-btn jp-btn-secondary jp-btn-sm">Cancel</button>
                  <button onClick={saveCertification} className="jp-btn jp-btn-primary jp-btn-sm">Save</button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
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
                        <Icon name="edit" className="text-[16px]" />
                      </button>
                      <button 
                        onClick={() => deleteCertification(cert.id)} 
                        className="p-1.5 text-jp-text-muted hover:text-jp-error hover:bg-jp-error-muted/20 rounded-lg transition-colors"
                      >
                        <Icon name="delete" className="text-[16px]" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          {/* Co-curricular Activities */}
          <section className="jp-card p-6 space-y-4">
            <h3 className="text-[18px] font-bold text-jp-text-primary flex items-center gap-2 pb-3 border-b border-jp-border-subtle">
              <Icon name="emoji_events" className="text-jp-accent" /> Co-curricular Activities
            </h3>
            
            <div className="flex flex-wrap gap-2 mb-3">
              {(!profileData?.resume_data?.co_curricular_activities || profileData.resume_data.co_curricular_activities.length === 0) ? (
                <p className="text-[13px] text-jp-text-tertiary">No co-curricular activities listed yet.</p>
              ) : (
                profileData.resume_data.co_curricular_activities.map((act, index) => (
                  <div key={index} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg hover:bg-jp-bg-inset transition-colors">
                    <span className="text-[13px] font-medium text-jp-text-primary">{act}</span>
                    <button onClick={() => removeCoCurricular(act)} className="text-jp-text-muted hover:text-jp-error transition-colors flex items-center ml-1">
                      <Icon name="close" className="text-[14px]" />
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="flex gap-2 max-w-sm">
              <input
                type="text"
                value={newCoCurricular}
                onChange={(e) => setNewCoCurricular(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCoCurricular())}
                placeholder="Add activity (e.g. Hackathon winner)"
                className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl py-2 px-3 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
              />
              <button onClick={addCoCurricular} className="jp-btn jp-btn-secondary py-2 px-4 rounded-xl text-[14px]">Add</button>
            </div>
          </section>

        </div>
      )}

      {/* STEP 3: PREFERENCES & COMPLETE */}
      {activeStep === 3 && (
        <div className="space-y-6">
          <div className="text-center space-y-2 mb-8">
            <h2 className="text-[32px] font-semibold text-jp-text-primary tracking-tight">Set Career Preferences</h2>
            <p className="text-jp-text-secondary max-w-xl mx-auto">
              Define your target roles and locations so the AI agent can find the most relevant opportunities and optimize your ATS score accurately.
            </p>
          </div>

          <div className="jp-card p-8 max-w-2xl mx-auto space-y-8">
            {/* Preferred Roles */}
            <div className="space-y-3">
              <label className="text-[13px] font-bold text-jp-text-secondary uppercase tracking-wider">Target Roles <span className="text-jp-error">*</span></label>
              <div className="flex flex-wrap gap-2">
                {profileData.preferences.preferred_roles.map((role, idx) => (
                  <div key={idx} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg">
                    <span className="text-[13px] font-medium text-jp-text-primary">{role}</span>
                    <button onClick={() => removeRole(role)} className="text-jp-text-muted hover:text-jp-error ml-1 transition-colors">
                      <Icon name="close" className="text-[14px]" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRole())}
                  placeholder="e.g. Frontend Engineer, Product Manager"
                  className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl py-3 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
                <button onClick={addRole} className="jp-btn jp-btn-secondary py-3 px-6 rounded-xl">Add</button>
              </div>
            </div>

            {/* Preferred Locations */}
            <div className="space-y-3">
              <label className="text-[13px] font-bold text-jp-text-secondary uppercase tracking-wider">Target Locations <span className="text-jp-error">*</span></label>
              <div className="flex flex-wrap gap-2">
                {profileData.preferences.preferred_locations.map((loc, idx) => (
                  <div key={idx} className="flex items-center gap-1 bg-jp-bg-surface border border-jp-border py-1.5 px-3 rounded-lg">
                    <span className="text-[13px] font-medium text-jp-text-primary">{loc}</span>
                    <button onClick={() => removeLocation(loc)} className="text-jp-text-muted hover:text-jp-error ml-1 transition-colors">
                      <Icon name="close" className="text-[14px]" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                  placeholder="e.g. Remote, San Francisco, London"
                  className="flex-1 bg-jp-bg-inset border border-jp-border rounded-xl py-3 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
                />
                <button onClick={addLocation} className="jp-btn jp-btn-secondary py-3 px-6 rounded-xl">Add</button>
              </div>
            </div>

            {/* Experience Level */}
            <div className="space-y-3">
              <label className="text-[13px] font-bold text-jp-text-secondary uppercase tracking-wider">Experience Level <span className="text-jp-error">*</span></label>
              <select
                value={profileData.preferences.experience_level || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  preferences: { ...profileData.preferences, experience_level: e.target.value }
                })}
                className="w-full bg-jp-bg-inset border border-jp-border rounded-xl py-3 px-4 text-[14px] text-jp-text-primary focus:border-jp-accent outline-none transition-colors"
              >
                <option value="">Select your experience level...</option>
                <option value="Fresher">Fresher (0 Years)</option>
                <option value="0-2 Years">Entry Level (0-2 Years)</option>
                <option value="2-5 Years">Mid Level (2-5 Years)</option>
                <option value="5+ Years">Senior Level (5+ Years)</option>
              </select>
            </div>

            <div className="pt-6 border-t border-jp-border-subtle flex justify-between items-center">
              <button
                onClick={() => setActiveStep(2)}
                className="jp-btn jp-btn-secondary py-3 px-6 rounded-xl"
              >
                Back
              </button>
              <button
                onClick={handleCompleteOnboarding}
                className="jp-btn jp-btn-primary py-3 px-8 rounded-xl font-bold flex items-center gap-2"
              >
                Complete Profile <Icon name="check_circle" className="text-[18px]" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
