import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/common/Toast';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';

// Modular imports
import { extractStructuredText } from '../services/pdfExtractor';
import OnboardingWizard from '../components/profile/OnboardingWizard';
import ProfileEditor from '../components/profile/ProfileEditor';

const WORKFLOW_STEPS = [
  { key: "parsing", title: "Resume Parser", subtitle: "Parsing resume structure", icon: "assignment" },
  { key: "intelligence", title: "Intelligence Agents", subtitle: "Extracting projects & experience", icon: "hub" },
  { key: "fusion", title: "Knowledge Fusion", subtitle: "Fusing competency map", icon: "code" },
  { key: "evidence", title: "Evidence Engine V2", subtitle: "Evaluating seniorities", icon: "fact_check" },
  { key: "synthesis", title: "Identity Synthesizer", subtitle: "Creating profile identity", icon: "psychology" },
  { key: "persistence", title: "Postgres Sync", subtitle: "Finalizing transaction", icon: "save" }
];

function Profile() {
  const { user, token, setHasProfile } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  // Page States
  const [profileExists, setProfileExists] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [completedStages, setCompletedStages] = useState([]);
  const [onboardingMessage, setOnboardingMessage] = useState("");
  const [activeStep, setActiveStep] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadingStepText, setUploadingStepText] = useState("");
  
  // Section Edit State
  const [editingSection, setEditingSection] = useState(null);

  // AI Insights State
  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  // Profile Context Data Schema
  const [profileData, setProfileData] = useState({
    resume_data: {
      contact_info: { phone: "", linkedin_url: "", github_url: "", portfolio_url: "" },
      summary: "",
      skills: [],
      experience: [],
      education: [],
      projects: [],
      certifications: [],
      co_curricular_activities: []
    },
    preferences: {
      preferred_roles: [],
      preferred_locations: [],
      experience_level: ""
    },
    resume_metadata: {
      file_name: "",
      uploaded_at: ""
    }
  });

  // Load profile on mount
  useEffect(() => {
    const loadProfile = async () => {
      if (!token) return;
      setLoading(true);
      try {
        const res = await fetch('http://localhost:8000/profile/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setProfileData(data.profile_json);
          setProfileExists(true);
        } else if (res.status === 404) {
          setProfileExists(false);
          localStorage.removeItem("jobpilot_candidate_profile");
        } else {
          throw new Error("Profile API not completed");
        }
      } catch (e) {
        // Fallback to localStorage only if offline/network error
        const localProfile = localStorage.getItem("jobpilot_candidate_profile");
        if (localProfile) {
          setProfileData(JSON.parse(localProfile));
          setProfileExists(true);
        } else {
          setProfileExists(false);
        }
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [token]);

  const fetchInsights = async () => {
    if (!token) return;
    setLoadingInsights(true);
    try {
      const res = await fetch('http://localhost:8000/profile/insights', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      }
    } catch (err) {
      console.error("Error fetching insights:", err);
    } finally {
      setLoadingInsights(false);
    }
  };

  const generateInsights = async () => {
    if (!token) return;
    setLoadingInsights(true);
    try {
      const res = await fetch('http://localhost:8000/profile/insights/generate', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
        toast.success("AI career insights updated!");
      } else {
        const errData = await res.json();
        toast.error(errData.detail || "Failed to generate insights.");
      }
    } catch (err) {
      console.error("Error generating insights:", err);
      toast.error("Error connecting to server to generate insights.");
    } finally {
      setLoadingInsights(false);
    }
  };

  useEffect(() => {
    if (profileExists) {
      fetchInsights();
    }
  }, [profileExists, token]);

  const calculateStrength = () => {
    let score = 0;
    const rData = profileData?.resume_data;
    const prefs = profileData?.preferences;

    if (rData?.contact_info?.phone) score += 5;
    if (rData?.contact_info?.linkedin_url || rData?.contact_info?.github_url) score += 5;
    if (rData?.summary && rData.summary.length > 20) score += 10;
    if (rData?.skills && rData.skills.length > 0) score += 15;
    if (rData?.experience && rData.experience.length > 0) score += 15;
    if (rData?.education && rData.education.length > 0) score += 10;
    if (rData?.projects && rData.projects.length > 0) score += 10;
    if (rData?.certifications && rData.certifications.length > 0) score += 10;
    if (rData?.co_curricular_activities && rData.co_curricular_activities.length > 0) score += 10;
    if (prefs?.preferred_roles && prefs.preferred_roles.length > 0) score += 10;

    return Math.min(score, 100);
  };

  const handleResumeUpload = (file) => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadingStepText("Uploading resume...");

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target.result;
        const pdfjsLib = window.pdfjsLib;
        if (!pdfjsLib) throw new Error("PDF.js library not loaded yet.");
        
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        
        setUploadingStepText("Scanning document structure...");
        setUploadProgress(30);

        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        
        setUploadingStepText("Extracting clean text...");
        setUploadProgress(50);

        const pagesText = await extractStructuredText(pdf);
        const fullText = pagesText.map(p => p.text).join("\n\n");

        setUploadProgress(70);
        setUploadingStepText("AI Resume Parsing...");
        setUploadProgress(80);

        try {
          const res = await fetch("http://localhost:8000/profile/parse-resume", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ resume_text: fullText })
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Failed to parse resume.");
          }

          const resumeData = await res.json();
          
          const addIds = (arr, offset) => (arr || []).map((item, idx) => ({ ...item, id: Date.now() + offset + idx }));
          
          if (resumeData.experience) resumeData.experience = addIds(resumeData.experience, 10);
          if (resumeData.education) resumeData.education = addIds(resumeData.education, 20);
          if (resumeData.projects) resumeData.projects = addIds(resumeData.projects, 30);
          if (resumeData.certifications) resumeData.certifications = addIds(resumeData.certifications, 40);

          setProfileData({
            resume_data: {
              ...resumeData,
              contact_info: resumeData.contact_info || { phone: "", linkedin_url: "", github_url: "", portfolio_url: "" },
              skills: resumeData.skills || [],
              co_curricular_activities: resumeData.co_curricular_activities || []
            },
            preferences: {
              preferred_roles: resumeData.preferred_roles || [],
              preferred_locations: resumeData.preferred_locations || [],
              experience_level: ""
            },
            resume_metadata: {
              file_name: file.name,
              uploaded_at: new Date().toISOString()
            }
          });

          setUploadProgress(100);
          setUploadingStepText("AI parsing completed!");
          
          setTimeout(() => {
            setIsUploading(false);
            setActiveStep(2);
            toast.success("Resume successfully parsed by AI!");
          }, 800);

        } catch (apiErr) {
          console.warn("Backend parser failed. Falling back to mock details.", apiErr);
          
          const cleanName = (user?.name || "Alex Chen").toLowerCase().replace(/\s+/g, "");

          setProfileData({
            resume_data: {
              contact_info: {
                phone: "+1 (555) 304-2831",
                linkedin_url: `https://linkedin.com/in/${cleanName}`,
                github_url: `https://github.com/${cleanName}`,
                portfolio_url: `https://${cleanName}.dev`
              },
              summary: `Innovative and results-driven software professional with 5+ years of experience specializing in building scalable applications, orchestrating cloud architecture, and automating CI/CD pipelines.`,
              skills: ["React", "Node.js", "AWS", "Docker", "Kubernetes", "Python", "SQL", "Terraform", "CI/CD"],
              experience: [
                {
                  id: Date.now() + 1,
                  company: "CloudScale Solutions",
                  role: "Senior DevOps Engineer",
                  start_date: "2022-03",
                  end_date: "Present",
                  description: "Led AWS migration project, decreasing hosting costs by 30%. Built automated infrastructure using Terraform and streamlined deployments with GitHub Actions."
                }
              ],
              education: [
                {
                  id: Date.now() + 3,
                  institution: "State University",
                  degree: "B.S. in Computer Science",
                  year: "2019"
                }
              ],
              projects: [],
              certifications: [],
              co_curricular_activities: []
            },
            preferences: {
              preferred_roles: ["DevOps Engineer", "Software Engineer"],
              preferred_locations: ["Remote"],
              experience_level: "2-5 Years"
            },
            resume_metadata: {
              file_name: file.name,
              uploaded_at: new Date().toISOString()
            }
          });

          setUploadProgress(100);
          setUploadingStepText("Demo loading complete!");

          setTimeout(() => {
            setIsUploading(false);
            setActiveStep(2);
            toast.info("Using mock data for demo (backend unreachable).");
          }, 850);
        }

      } catch (err) {
        console.error("Failed to parse PDF on frontend:", err);
        setUploadingStepText("Parsing failed. Proceeding manually...");
        setTimeout(() => {
          setIsUploading(false);
          setActiveStep(2);
          toast.error("Failed to parse PDF. Please verify details manually.");
        }, 1500);
      }
    };
    reader.onerror = (err) => {
      setIsUploading(false);
      toast.error("File reading error. Please try again.");
    };
    reader.readAsArrayBuffer(file);
  };

  const handleCompleteOnboarding = async () => {
    if (!profileData.preferences.preferred_roles?.length) {
      toast.warning("Please add at least one preferred role.");
      setActiveStep(3);
      return;
    }
    if (!profileData.preferences.preferred_locations?.length) {
      toast.warning("Please add at least one preferred location.");
      setActiveStep(3);
      return;
    }
    if (!profileData.preferences.experience_level) {
      toast.warning("Please select your experience level.");
      setActiveStep(3);
      return;
    }

    setLoading(true);
    setIsSyncing(true);
    setActiveStage("parsing");
    setCompletedStages([]);
    setOnboardingMessage("Initializing connection...");
    
    const clean = (arr) => (arr || []).map(({ id, ...rest }) => rest);
    const payload = {
      resume_data: {
        ...profileData.resume_data,
        experience: clean(profileData.resume_data.experience),
        education: clean(profileData.resume_data.education),
        projects: clean(profileData.resume_data.projects),
        certifications: clean(profileData.resume_data.certifications)
      },
      preferences: profileData.preferences,
      resume_metadata: profileData.resume_metadata
    };

    try {
      const res = await fetch("http://localhost:8000/profile/complete-onboarding-stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Failed to complete onboarding.");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const stageOrder = ["parsing", "intelligence", "fusion", "evidence", "synthesis", "persistence"];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop(); // save incomplete line

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const rawData = line.substring(6);
            if (!rawData.trim()) continue;
            
            let eventData;
            try {
              eventData = JSON.parse(rawData);
            } catch (err) {
              console.error("Failed to parse SSE JSON:", rawData);
              continue;
            }

            if (eventData.status === "processing") {
              const currentStage = eventData.stage;
              setActiveStage(currentStage);
              setOnboardingMessage(eventData.message);
              
              // Automatically mark previous stages as completed
              const stageIndex = stageOrder.indexOf(currentStage);
              if (stageIndex > 0) {
                setCompletedStages(stageOrder.slice(0, stageIndex));
              }
            } else if (eventData.status === "success") {
              setCompletedStages(stageOrder);
              localStorage.setItem("jobpilot_candidate_profile", JSON.stringify(payload));
              localStorage.setItem("jobpilot_has_profile", "true");
              toast.success("Career context saved! Welcome to your JobPilot dashboard.");
              setHasProfile(true);
              setProfileExists(true);
              navigate('/dashboard');
              return;
            } else if (eventData.status === "error") {
              throw new Error(eventData.message || "An error occurred during onboarding.");
            }
          }
        }
      }
    } catch (err) {
      toast.error(err.message || "Error saving profile. Please try again.");
    } finally {
      setLoading(false);
      setIsSyncing(false);
      setActiveStage(null);
    }
  };

  const handleSaveProfileChanges = async () => {
    const clean = (arr) => (arr || []).map(({ id, ...rest }) => rest);
    const payload = {
      resume_data: {
        ...profileData.resume_data,
        experience: clean(profileData.resume_data.experience),
        education: clean(profileData.resume_data.education),
        projects: clean(profileData.resume_data.projects),
        certifications: clean(profileData.resume_data.certifications)
      },
      preferences: profileData.preferences,
      resume_metadata: profileData.resume_metadata
    };

    setLoading(true);
    setIsSyncing(true);
    setActiveStage("parsing");
    setCompletedStages([]);
    setOnboardingMessage("Updating profile...");
    try {
      const res = await fetch("http://localhost:8000/profile/complete-onboarding-stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Failed to update profile on backend");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const stageOrder = ["parsing", "intelligence", "fusion", "evidence", "synthesis", "persistence"];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const rawData = line.substring(6);
            if (!rawData.trim()) continue;

            let eventData;
            try {
              eventData = JSON.parse(rawData);
            } catch (err) {
              continue;
            }

            if (eventData.status === "processing") {
              const currentStage = eventData.stage;
              setActiveStage(currentStage);
              setOnboardingMessage(eventData.message);
              
              const stageIndex = stageOrder.indexOf(currentStage);
              if (stageIndex > 0) {
                setCompletedStages(stageOrder.slice(0, stageIndex));
              }
            } else if (eventData.status === "success") {
              setCompletedStages(stageOrder);
              localStorage.setItem("jobpilot_candidate_profile", JSON.stringify(payload));
              setEditingSection(null);
              toast.success("Profile section updated successfully!");
              fetchInsights();
              return;
            } else if (eventData.status === "error") {
              throw new Error(eventData.message || "An error occurred updating profile.");
            }
          }
        }
      }
    } catch (err) {
      toast.error(err.message || "Failed to update profile.");
    } finally {
      setLoading(false);
      setIsSyncing(false);
      setActiveStage(null);
    }
  };

  if (isSyncing) {
    const stageOrder = ["parsing", "intelligence", "fusion", "evidence", "synthesis", "persistence"];
    const progressPercent = Math.min(100, Math.round(((completedStages.length) / stageOrder.length) * 100));

    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#09090b] text-[#fafafa] p-8 relative overflow-hidden select-none">
        {/* Ambient Glows */}
        <div className="absolute top-[10%] left-[10%] w-[350px] h-[350px] bg-jp-accent/5 rounded-full blur-[130px] pointer-events-none animate-pulse" />
        <div className="absolute bottom-[10%] right-[10%] w-[350px] h-[350px] bg-jp-success/5 rounded-full blur-[130px] pointer-events-none" />

        <div className="w-full max-w-6xl space-y-12 relative z-10">
          {/* Header */}
          <div className="text-center space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-jp-accent/30 bg-jp-accent/5 text-[11px] font-bold text-jp-accent uppercase tracking-wider mb-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-jp-accent opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-jp-accent"></span>
              </span>
              Live Pipeline
            </div>
            <h1 className="text-4xl font-extrabold text-white tracking-tight sm:text-5xl">
              Intelligent Agent <span className="bg-gradient-to-r from-jp-accent to-jp-success bg-clip-text text-transparent">Workflow</span>
            </h1>
            <p className="text-sm text-jp-text-secondary max-w-2xl mx-auto leading-relaxed">
              Visualizing the neural orchestration of your recruitment co-pilot. Every detail is structured, analyzed, and synthesized through our multi-agent architecture in real-time.
            </p>
          </div>

          {/* Horizontal Step Flow Diagram */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 md:gap-4 px-4 py-8 bg-[#121214]/40 border border-jp-border/50 rounded-3xl backdrop-blur-xl relative overflow-hidden shadow-2xl">
            {WORKFLOW_STEPS.map((step, idx) => {
              const isCompleted = completedStages.includes(step.key);
              const isActive = activeStage === step.key;

              let statusLabel = "IDLE";
              if (isCompleted) statusLabel = "COMPLETED";
              else if (isActive) statusLabel = "PROCESSING...";

              return (
                <React.Fragment key={step.key}>
                  {/* Step Card */}
                  <div className={`flex-1 w-full md:max-w-[165px] bg-[#121214] border rounded-2xl p-5 flex flex-col items-center justify-between gap-4 text-center transition-all duration-300 relative ${
                    isActive ? 'border-jp-accent shadow-[0_0_20px_rgba(var(--jp-accent-rgb),0.15)] ring-1 ring-jp-accent scale-[1.03]' :
                    isCompleted ? 'border-jp-success/50 bg-[#121214]/80' :
                    'border-[#1e1e24] opacity-50'
                  }`}>
                    {/* Icon Container */}
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 ${
                      isCompleted ? 'bg-jp-success/10 text-jp-success border border-jp-success/20' :
                      isActive ? 'bg-jp-accent/15 text-jp-accent border border-jp-accent/30 animate-pulse' :
                      'bg-[#1c1c1f] text-jp-text-muted border border-jp-border'
                    }`}>
                      {isCompleted ? (
                        <Icon name="check_circle" className="text-[20px]" />
                      ) : (
                        <Icon name={step.icon} className="text-[20px]" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="space-y-1">
                      <p className={`text-[13px] font-bold tracking-tight transition-colors ${
                        isActive ? 'text-white' :
                        isCompleted ? 'text-jp-text-primary' :
                        'text-jp-text-muted'
                      }`}>
                        {step.title}
                      </p>
                      <p className="text-[10px] text-jp-text-secondary leading-snug line-clamp-2 h-7">
                        {step.subtitle}
                      </p>
                    </div>

                    {/* Status indicator */}
                    <div className={`text-[9px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      isCompleted ? 'bg-jp-success/10 text-jp-success border border-jp-success/25' :
                      isActive ? 'bg-jp-accent/15 text-jp-accent border border-jp-accent/25 animate-pulse' :
                      'bg-[#1c1c1f] text-jp-text-muted border border-jp-border'
                    }`}>
                      {statusLabel}
                    </div>
                  </div>

                  {/* Horizontal Connector Line (Except last step) */}
                  {idx < WORKFLOW_STEPS.length - 1 && (
                    <div className="hidden md:block h-0.5 flex-1 min-w-[20px] bg-jp-border/30 relative">
                      <div 
                        className="absolute inset-0 bg-gradient-to-r from-jp-accent to-jp-success transition-all duration-500"
                        style={{ width: isCompleted ? "100%" : isActive ? "50%" : "0%" }}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Active Status Banner */}
          <div className="bg-[#121214]/60 border border-jp-border rounded-2xl p-5 flex items-center justify-between max-w-2xl mx-auto shadow-md">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-jp-accent/10 border border-jp-accent/20 flex items-center justify-center">
                <Icon name="terminal" className="text-jp-accent animate-pulse" />
              </div>
              <div className="space-y-1">
                <p className="text-[11px] font-extrabold uppercase text-jp-accent tracking-wider leading-none">Status Feed</p>
                <p className="text-[13px] text-jp-text-primary font-medium tracking-tight">
                  {onboardingMessage || "Starting pipelines..."}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-[12px] font-bold text-jp-text-secondary">{progressPercent}%</span>
              <div className="w-24 h-1.5 bg-[#1c1c1f] rounded-full overflow-hidden border border-jp-border">
                <div 
                  className="h-full bg-gradient-to-r from-jp-accent to-jp-success transition-all duration-500" 
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-jp-bg-app">
        <Icon name="progress_activity" className="text-[40px] text-jp-accent animate-spin" />
        <p className="mt-4 text-[14px] text-jp-text-secondary font-medium">Loading profile data...</p>
      </div>
    );
  }

  return (
    <AppShell breadcrumbs={[{ label: "Profile" }]}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto h-full">
        {profileExists === false ? (
          <div className="max-w-3xl mx-auto">
            <OnboardingWizard
              activeStep={activeStep}
              setActiveStep={setActiveStep}
              isUploading={isUploading}
              uploadProgress={uploadProgress}
              uploadingStepText={uploadingStepText}
              profileData={profileData}
              setProfileData={setProfileData}
              handleResumeUpload={handleResumeUpload}
              handleCompleteOnboarding={handleCompleteOnboarding}
              triggerToast={(msg) => toast.info(msg)}
              user={user}
            />
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="flex-1 max-w-3xl">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-jp-text-primary tracking-tight">Profile Settings</h2>
                <p className="text-[14px] text-jp-text-secondary mt-1">Manage your career profile and job preferences.</p>
              </div>

              <ProfileEditor
                profileData={profileData}
                setProfileData={setProfileData}
                user={user}
                editingSection={editingSection}
                setEditingSection={setEditingSection}
                handleSaveProfileChanges={handleSaveProfileChanges}
              />
            </div>

            <div className="w-full lg:w-[300px] shrink-0 space-y-6">
              <div className="p-6 border border-jp-border rounded-2xl bg-jp-bg-surface shadow-sm text-center sticky top-6">
                <div className="relative w-28 h-28 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="56" cy="56" r="48" className="text-jp-bg-inset" stroke="currentColor" strokeWidth="8" fill="none" />
                    <circle
                      cx="56"
                      cy="56"
                      r="48"
                      className="text-jp-accent transition-all duration-700"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray="301.6"
                      strokeDashoffset={301.6 - (301.6 * calculateStrength()) / 100}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-[20px] font-bold text-jp-text-primary">{Math.round(calculateStrength())}%</span>
                  </div>
                </div>
                <h3 className="text-[15px] font-bold text-jp-text-primary mb-1">Profile Strength</h3>
                <p className="text-[13px] text-jp-text-tertiary mb-6 px-2 leading-relaxed">Complete your profile to unlock accurate market insights.</p>
                <button
                  onClick={() => navigate('/insights')}
                  className="w-full py-3 bg-jp-accent hover:bg-jp-accent-hover text-white rounded-xl flex items-center justify-center gap-2 text-[13px] font-bold shadow-lg shadow-jp-accent/20 transition-all"
                >
                  <Icon name="auto_awesome" className="text-[18px]" />
                  View AI Career Agent
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default Profile;
