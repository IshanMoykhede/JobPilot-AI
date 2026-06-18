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
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      {/* Stepper Card */}
      <div className="bg-surface-container-lowest border border-outline-variant/50 rounded-2xl p-6 shadow-sm">
        <div className="flex justify-between items-center max-w-xl mx-auto">
          {/* Step 1 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 1
                  ? "bg-primary text-on-primary ring-4 ring-primary/20"
                  : activeStep > 1
                  ? "bg-primary text-on-primary"
                  : "bg-surface-container text-outline"
              }`}
            >
              {activeStep > 1 ? <Icon name="check" /> : <span className="font-bold">1</span>}
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 1 ? "text-primary" : "text-outline"}`}>Resume Upload</span>
          </div>

          <div className={`flex-1 h-[2px] mx-2 -mt-6 transition-colors ${activeStep >= 2 ? "bg-primary" : "bg-outline-variant/30"}`} />

          {/* Step 2 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 2
                  ? "bg-primary text-on-primary ring-4 ring-primary/20"
                  : activeStep > 2
                  ? "bg-primary text-on-primary"
                  : "bg-surface-container text-outline"
              }`}
            >
              {activeStep > 2 ? <Icon name="check" /> : <span className="font-bold">2</span>}
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 2 ? "text-primary" : "text-outline"}`}>AI Verification</span>
          </div>

          <div className={`flex-1 h-[2px] mx-2 -mt-6 transition-colors ${activeStep >= 3 ? "bg-primary" : "bg-outline-variant/30"}`} />

          {/* Step 3 */}
          <div className="flex flex-col items-center gap-2 relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                activeStep === 3
                  ? "bg-primary text-on-primary ring-4 ring-primary/20"
                  : "bg-surface-container text-outline"
              }`}
            >
              <span className="font-bold">3</span>
            </div>
            <span className={`text-[12px] font-bold ${activeStep === 3 ? "text-primary" : "text-outline"}`}>Preferences</span>
          </div>
        </div>
      </div>

      {/* STEP 1: UPLOAD RESUME */}
      {activeStep === 1 && (
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-[32px] font-semibold text-on-surface tracking-tight">Create Candidate Context</h2>
            <p className="text-on-surface-variant max-w-xl mx-auto">
              Upload your resume to extract details instantly. Our AI parses work milestones, projects, and skills to tailor your dashboard context.
            </p>
          </div>

          {isUploading ? (
            <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-12 text-center space-y-6 max-w-lg mx-auto shadow-lg">
              <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
                <Icon name="cloud_upload" className="text-[64px] text-primary animate-pulse" />
                <div className="absolute inset-0 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
              </div>
              <div className="space-y-2">
                <h4 className="text-[18px] font-bold">Uploading & Parsing...</h4>
                <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                  <div className="bg-primary h-full transition-all duration-300 rounded-full" style={{ width: `${uploadProgress}%` }} />
                </div>
                <div className="flex justify-between items-center text-[12px] text-outline font-semibold">
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
              className="border-2 border-dashed border-outline-variant hover:border-primary bg-surface-container-lowest hover:bg-primary/5 cursor-pointer rounded-2xl p-16 text-center transition-all group max-w-xl mx-auto relative shadow-sm"
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
                <div className="w-20 h-20 bg-surface-container rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform shadow-inner">
                  <Icon name="cloud_upload" className="text-[40px] text-primary" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-[20px] font-bold text-on-surface">Drag & drop your resume here</h3>
                  <p className="text-on-surface-variant text-[14px]">or <span className="text-primary font-bold hover:underline">browse files</span> from your computer</p>
                  <p className="text-[12px] text-outline">Supports PDF and DOCX formats up to 10MB</p>
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
              className="text-primary hover:underline font-semibold text-[14px]"
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
              <h2 className="text-[28px] font-semibold text-on-surface tracking-tight">Verify Extracted Resume Data</h2>
              <p className="text-on-surface-variant text-[14px]">Review AI parsed items. Edit information to guarantee complete profile details.</p>
            </div>
            <button
              onClick={() => setActiveStep(3)}
              className="bg-primary text-on-primary py-2.5 px-6 rounded-xl font-bold flex items-center gap-1.5 hover:opacity-90 active:scale-[0.98] transition-all"
            >
              Next: Preferences <Icon name="arrow_forward" className="text-[18px]" />
            </button>
          </div>

          {/* Contact Details Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-6 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-3 border-b border-outline-variant/30">
              <Icon name="contact_phone" className="text-primary" /> Contact Details & Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-outline uppercase tracking-wider">Phone Number</label>
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
                  className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-outline uppercase tracking-wider">LinkedIn Profile</label>
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
                  className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-outline uppercase tracking-wider">GitHub URL</label>
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
                  className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[12px] font-bold text-outline uppercase tracking-wider">Portfolio Website</label>
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
                  className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div className="md:col-span-2 space-y-1">
                <label className="text-[12px] font-bold text-outline uppercase tracking-wider">Professional Bio / Summary</label>
                <textarea
                  rows={3}
                  value={profileData.resume_data.summary || ""}
                  onChange={(e) => setProfileData({
                    ...profileData,
                    resume_data: { ...profileData.resume_data, summary: e.target.value }
                  })}
                  placeholder="A quick summary of your professional milestones..."
                  className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
            </div>
          </section>

          {/* Skills Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-3 border-b border-outline-variant/30">
              <Icon name="psychology" className="text-primary" /> Skills
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {profileData.resume_data.skills.map((skill, index) => (
                <div key={index} className="flex items-center gap-1 bg-surface-container py-1.5 px-3 rounded-lg border border-outline-variant/40 hover:bg-surface-container-high transition-colors">
                  <span className="text-[13px] font-semibold">{skill}</span>
                  <button onClick={() => removeSkill(skill)} className="text-on-surface-variant hover:text-error transition-colors flex items-center">
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
                className="flex-1 bg-surface-container-low border border-outline-variant/70 rounded-xl py-2 px-3 text-[14px] outline-none"
              />
              <button onClick={addSkill} className="bg-primary/10 text-primary py-2 px-4 rounded-xl text-[14px] font-bold hover:bg-primary/20 transition-all">Add</button>
            </div>
          </section>

          {/* Experience Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex justify-between items-center pb-3 border-b border-outline-variant/30">
              <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
                <Icon name="work" className="text-primary" /> Work History
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
                  <Icon name="add" className="text-[18px]" /> Add Position
                </button>
              )}
            </div>

            {editingExpId !== null && (
              <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-primary">{editingExpId === 'new' ? "Add Position" : "Edit Position"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input type="text" placeholder="Company" value={expCompany} onChange={(e) => setExpCompany(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Role Title" value={expRole} onChange={(e) => setExpRole(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Start Date" value={expStartDate} onChange={(e) => setExpStartDate(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="End Date" value={expEndDate} onChange={(e) => setExpEndDate(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <textarea rows={3} placeholder="Responsibilities" value={expDescription} onChange={(e) => setExpDescription(e.target.value)} className="md:col-span-2 w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingExpId(null)} className="px-4 py-1.5 border border-outline-variant rounded-lg text-[13px] hover:bg-surface-container-lowest">Cancel</button>
                  <button onClick={saveExperience} className="px-4 py-1.5 bg-primary text-on-primary rounded-lg text-[13px] font-semibold">Save</button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {profileData.resume_data.experience.map((exp) => (
                <div key={exp.id} className="flex justify-between items-start p-4 border border-outline-variant/40 bg-surface-container-lowest rounded-xl">
                  <div>
                    <div className="font-bold text-[15px]">{exp.role}</div>
                    <div className="text-[13px] font-semibold text-primary">{exp.company}</div>
                    <div className="text-[12px] text-outline">{exp.start_date} - {exp.end_date}</div>
                    <p className="text-[13px] text-on-surface-variant mt-1">{exp.description}</p>
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
                      className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-lg"
                    >
                      <Icon name="edit" className="text-[18px]" />
                    </button>
                    <button onClick={() => deleteExperience(exp.id)} className="p-1.5 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-lg">
                      <Icon name="delete" className="text-[18px]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Education Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex justify-between items-center pb-3 border-b border-outline-variant/30">
              <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
                <Icon name="school" className="text-primary" /> Education History
              </h3>
              {editingEduId === null && (
                <button
                  onClick={() => {
                    setEditingEduId('new');
                    setEduInstitution("");
                    setEduDegree("");
                    setEduYear("");
                  }}
                  className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
                >
                  <Icon name="add" className="text-[18px]" /> Add Degree
                </button>
              )}
            </div>

            {editingEduId !== null && (
              <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-primary">{editingEduId === 'new' ? "Add Education" : "Edit Education"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <input type="text" placeholder="Institution" value={eduInstitution} onChange={(e) => setEduInstitution(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Degree" value={eduDegree} onChange={(e) => setEduDegree(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Graduation Year" value={eduYear} onChange={(e) => setEduYear(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingEduId(null)} className="px-4 py-1.5 border border-outline-variant rounded-lg text-[13px] hover:bg-surface-container-lowest">Cancel</button>
                  <button onClick={saveEducation} className="px-4 py-1.5 bg-primary text-on-primary rounded-lg text-[13px] font-semibold">Save</button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {profileData.resume_data.education.map((edu) => (
                <div key={edu.id} className="flex justify-between items-center p-4 border border-outline-variant/40 bg-surface-container-lowest rounded-xl">
                  <div>
                    <div className="font-bold text-[15px]">{edu.degree}</div>
                    <div className="text-[13px] font-semibold text-primary">{edu.institution}</div>
                    <div className="text-[12px] text-outline">Graduated: {edu.year}</div>
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => {
                        setEditingEduId(edu.id);
                        setEduInstitution(edu.institution);
                        setEduDegree(edu.degree);
                        setEduYear(edu.year || "");
                      }}
                      className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-lg"
                    >
                      <Icon name="edit" className="text-[18px]" />
                    </button>
                    <button onClick={() => deleteEducation(edu.id)} className="p-1.5 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-lg">
                      <Icon name="delete" className="text-[18px]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Projects Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex justify-between items-center pb-3 border-b border-outline-variant/30">
              <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2">
                <Icon name="folder_open" className="text-primary" /> Projects
              </h3>
              {editingProjId === null && (
                <button
                  onClick={() => {
                    setEditingProjId('new');
                    setProjTitle("");
                    setProjDescription("");
                    setProjTech("");
                  }}
                  className="text-primary font-bold text-[14px] flex items-center gap-1 hover:underline"
                >
                  <Icon name="add" className="text-[18px]" /> Add Project
                </button>
              )}
            </div>

            {editingProjId !== null && (
              <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-primary">{editingProjId === 'new' ? "Add Project" : "Edit Project"}</h4>
                <div className="grid grid-cols-1 gap-4">
                  <input type="text" placeholder="Project Title" value={projTitle} onChange={(e) => setProjTitle(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Technologies (comma-separated)" value={projTech} onChange={(e) => setProjTech(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <textarea rows={2} placeholder="Project Description" value={projDescription} onChange={(e) => setProjDescription(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingProjId(null)} className="px-4 py-1.5 border border-outline-variant rounded-lg text-[13px] hover:bg-surface-container-lowest">Cancel</button>
                  <button onClick={saveProject} className="px-4 py-1.5 bg-primary text-on-primary rounded-lg text-[13px] font-semibold">Save</button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profileData.resume_data.projects.map((proj) => (
                <div key={proj.id} className="p-4 border border-outline-variant/45 bg-surface-container-lowest rounded-xl flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center">
                      <h4 className="font-bold text-[15px]">{proj.title}</h4>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setEditingProjId(proj.id);
                            setProjTitle(proj.title);
                            setProjDescription(proj.description || "");
                            setProjTech(proj.technologies ? proj.technologies.join(", ") : "");
                          }}
                          className="p-1 text-on-surface-variant hover:text-primary rounded-md"
                        >
                          <Icon name="edit" className="text-[16px]" />
                        </button>
                        <button onClick={() => deleteProject(proj.id)} className="p-1 text-on-surface-variant hover:text-error rounded-md">
                          <Icon name="delete" className="text-[16px]" />
                        </button>
                      </div>
                    </div>
                    <p className="text-[13px] text-on-surface-variant mt-1">{proj.description}</p>
                  </div>
                  {proj.technologies && proj.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-outline-variant/20">
                      {proj.technologies.map((t, i) => (
                        <span key={i} className="bg-surface-container text-[11px] font-semibold px-2 py-0.5 rounded text-outline">{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Certifications Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex justify-between items-center pb-3 border-b border-outline-variant/30">
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
                  <Icon name="add" className="text-[18px]" /> Add Certification
                </button>
              )}
            </div>

            {editingCertId !== null && (
              <div className="p-4 bg-surface-container-low border border-outline-variant/60 rounded-xl space-y-4">
                <h4 className="font-bold text-[14px] text-primary">{editingCertId === 'new' ? "Add Certification" : "Edit Certification"}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input type="text" placeholder="Certification Name" value={certName} onChange={(e) => setCertName(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Issuer (e.g. Google, AWS)" value={certIssuer} onChange={(e) => setCertIssuer(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Year" value={certYear} onChange={(e) => setCertYear(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                  <input type="text" placeholder="Verification URL (optional)" value={certUrl} onChange={(e) => setCertUrl(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-[14px] outline-none" />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setEditingCertId(null)} className="px-4 py-1.5 border border-outline-variant rounded-lg text-[13px] hover:bg-surface-container-lowest">Cancel</button>
                  <button onClick={saveCertification} className="px-4 py-1.5 bg-primary text-on-primary rounded-lg text-[13px] font-semibold">Save</button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(!profileData.resume_data.certifications || profileData.resume_data.certifications.length === 0) ? (
                <p className="text-[13px] text-outline italic col-span-2">No certifications listed.</p>
              ) : (
                profileData.resume_data.certifications.map((cert) => (
                  <div key={cert.id} className="p-4 border border-outline-variant/45 bg-surface-container-lowest rounded-xl flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-[15px]">{cert.name}</h4>
                      <div className="text-[13px] font-semibold text-primary">{cert.issuer} {cert.year && `• ${cert.year}`}</div>
                      {cert.url && (
                        <a href={cert.url} target="_blank" rel="noreferrer" className="text-[12px] text-primary hover:underline flex items-center gap-0.5 mt-1 font-semibold">
                          <Icon name="link" className="text-[14px]" /> Verify Credential
                        </a>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => {
                          setEditingCertId(cert.id);
                          setCertName(cert.name);
                          setCertIssuer(cert.issuer || "");
                          setCertYear(cert.year || "");
                          setCertUrl(cert.url || "");
                        }}
                        className="p-1 text-on-surface-variant hover:text-primary rounded-md"
                      >
                        <Icon name="edit" className="text-[16px]" />
                      </button>
                      <button onClick={() => deleteCertification(cert.id)} className="p-1 text-on-surface-variant hover:text-error rounded-md">
                        <Icon name="delete" className="text-[16px]" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          {/* Co-curricular Activities Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-2 border-b border-outline-variant/30">
              <Icon name="emoji_events" className="text-primary" /> Co-curricular Activities
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {(!profileData.resume_data.co_curricular_activities || profileData.resume_data.co_curricular_activities.length === 0) ? (
                <p className="text-[13px] text-outline italic">No co-curricular activities listed.</p>
              ) : (
                profileData.resume_data.co_curricular_activities.map((act, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 bg-secondary-container/10 text-secondary border border-secondary-container/30 px-3 py-1.5 rounded-lg">
                    <span className="text-[13px] font-bold">{act}</span>
                    <button onClick={() => removeCoCurricular(act)} className="hover:text-error flex items-center"><Icon name="close" className="text-[14px]" /></button>
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
                placeholder="Add activity (e.g. Hackathon participant)"
                className="flex-1 bg-surface-container-low border border-outline-variant/70 rounded-xl py-2 px-3 text-[14px] outline-none"
              />
              <button onClick={addCoCurricular} className="bg-primary/10 text-primary py-2 px-4 rounded-xl text-[14px] font-bold hover:bg-primary/20">Add</button>
            </div>
          </section>
        </div>
      )}

      {/* STEP 3: PREFERENCES */}
      {activeStep === 3 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-[28px] font-semibold text-on-surface tracking-tight">Define Job Search Preferences</h2>
              <p className="text-on-surface-variant text-[14px]">Let AI understand what jobs to find and target for you.</p>
            </div>
            <button
              onClick={() => setActiveStep(2)}
              className="border border-outline-variant bg-surface text-on-surface py-2.5 px-6 rounded-xl font-bold flex items-center gap-1.5 hover:bg-surface-container-low transition-all"
            >
              <Icon name="arrow_back" className="text-[18px]" /> Back
            </button>
          </div>

          {/* Experience Level Dropdown */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-2 border-b border-outline-variant/30">
              <Icon name="grade" className="text-primary" /> Overall Professional Experience
            </h3>
            <div className="max-w-md pt-2">
              <select
                value={profileData.preferences.experience_level || ""}
                onChange={(e) => setProfileData({
                  ...profileData,
                  preferences: { ...profileData.preferences, experience_level: e.target.value }
                })}
                className="w-full bg-surface-container-low border border-outline-variant/70 rounded-xl py-2.5 px-4 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer font-medium"
              >
                <option value="" disabled>Select your experience level</option>
                <option value="Fresher">Fresher (No professional experience)</option>
                <option value="0-2 Years">0-2 Years (Junior)</option>
                <option value="2-5 Years">2-5 Years (Mid-Level)</option>
                <option value="5+ Years">5+ Years (Senior)</option>
              </select>
            </div>
          </section>

          {/* Target Roles Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-2 border-b border-outline-variant/30">
              <Icon name="star" className="text-primary" /> Target Job Roles
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {profileData.preferences.preferred_roles.map((role, idx) => (
                <div key={idx} className="flex items-center gap-1.5 bg-secondary-container/10 text-secondary border border-secondary-container/30 px-3 py-1.5 rounded-lg">
                  <span className="text-[13px] font-bold">{role}</span>
                  <button onClick={() => removeRole(role)} className="hover:text-error flex items-center"><Icon name="close" className="text-[14px]" /></button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 max-w-sm">
              <input
                type="text"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRole())}
                placeholder="Add role and press enter"
                className="flex-1 bg-surface-container-low border border-outline-variant/70 rounded-xl py-2 px-3 text-[14px] outline-none"
              />
              <button onClick={addRole} className="bg-primary/10 text-primary py-2 px-4 rounded-xl text-[14px] font-bold hover:bg-primary/20">Add</button>
            </div>
            <div className="space-y-2 pt-2">
              <label className="text-[12px] font-bold text-outline uppercase tracking-wider block">Suggestions (click to toggle)</label>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Software Engineer",
                  "Backend Developer",
                  "Frontend Developer",
                  "Full Stack Developer",
                  "Python Developer",
                  "Java Developer",
                  "DevOps Engineer"
                ].map((role) => {
                  const isSelected = profileData.preferences.preferred_roles.includes(role);
                  return (
                    <button
                      key={role}
                      type="button"
                      onClick={() => {
                        if (isSelected) {
                          removeRole(role);
                        } else {
                          setProfileData({
                            ...profileData,
                            preferences: {
                              ...profileData.preferences,
                              preferred_roles: [...profileData.preferences.preferred_roles, role]
                            }
                          });
                        }
                      }}
                      className={`text-[12px] font-semibold px-2.5 py-1.5 rounded-lg border transition-all ${
                        isSelected
                          ? "bg-primary/10 text-primary border-primary"
                          : "bg-surface-container hover:bg-surface-container-high text-on-surface-variant border-outline-variant/40"
                      }`}
                    >
                      {role}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          {/* Locations Card */}
          <section className="bg-surface-container-lowest border border-outline-variant/60 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-[18px] font-bold text-on-surface flex items-center gap-2 pb-2 border-b border-outline-variant/30">
              <Icon name="location_on" className="text-primary" /> Target Locations
            </h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {profileData.preferences.preferred_locations.map((loc, idx) => (
                <div key={idx} className="flex items-center gap-1.5 bg-secondary-container/10 text-secondary border border-secondary-container/30 px-3 py-1.5 rounded-lg">
                  <span className="text-[13px] font-bold">{loc}</span>
                  <button onClick={() => removeLocation(loc)} className="hover:text-error flex items-center"><Icon name="close" className="text-[14px]" /></button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 max-w-sm">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                placeholder="Add location and press enter"
                className="flex-1 bg-surface-container-low border border-outline-variant/70 rounded-xl py-2 px-3 text-[14px] outline-none"
              />
              <button onClick={addLocation} className="bg-primary/10 text-primary py-2 px-4 rounded-xl text-[14px] font-bold hover:bg-primary/20">Add</button>
            </div>
            <div className="space-y-2 pt-2">
              <label className="text-[12px] font-bold text-outline uppercase tracking-wider block">Suggestions (click to toggle)</label>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Pune",
                  "Mumbai",
                  "Bangalore",
                  "Hyderabad",
                  "Remote"
                ].map((loc) => {
                  const isSelected = profileData.preferences.preferred_locations.includes(loc);
                  return (
                    <button
                      key={loc}
                      type="button"
                      onClick={() => {
                        if (isSelected) {
                          removeLocation(loc);
                        } else {
                          setProfileData({
                            ...profileData,
                            preferences: {
                              ...profileData.preferences,
                              preferred_locations: [...profileData.preferences.preferred_locations, loc]
                            }
                          });
                        }
                      }}
                      className={`text-[12px] font-semibold px-2.5 py-1.5 rounded-lg border transition-all ${
                        isSelected
                          ? "bg-primary/10 text-primary border-primary"
                          : "bg-surface-container hover:bg-surface-container-high text-on-surface-variant border-outline-variant/40"
                      }`}
                    >
                      {loc}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          {/* Complete */}
          <div className="pt-4 flex justify-between">
            <button onClick={() => setActiveStep(2)} className="px-6 py-3 border border-outline-variant rounded-xl font-bold text-on-surface hover:bg-surface-container-low">Back</button>
            <button onClick={handleCompleteOnboarding} className="bg-primary-container text-on-primary font-bold py-3.5 px-10 rounded-xl shadow-lg hover:brightness-110 flex items-center gap-2">
              Launch Career Engine <Icon name="rocket_launch" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
