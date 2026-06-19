import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/layout/SideBar';
import UserProfileCard from '../components/layout/userProfileCard';
import Icon from '../components/common/Icon';
import { themeVars } from '../styles/Theme';

// Modular imports
import { extractStructuredText } from '../services/pdfExtractor';
import OnboardingWizard from '../components/profile/OnboardingWizard';
import ProfileEditor from '../components/profile/ProfileEditor';
import AIInsightsPanel from '../components/profile/AIInsightsPanel';

function Profile() {
  const { user, token, setHasProfile } = useAuth();
  const navigate = useNavigate();

  // Page States
  const [profileExists, setProfileExists] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeStep, setActiveStep] = useState(1); // Onboarding Steps: 1 = Upload, 2 = Verify, 3 = Preferences
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadingStepText, setUploadingStepText] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  
  // Section Edit State (for Existing Profile Mode)
  const [editingSection, setEditingSection] = useState(null); // 'personal' | 'skills' | 'experience' | 'preferences'

  // AI Insights State
  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  // Profile Context Data Schema
  const [profileData, setProfileData] = useState({
    resume_data: {
      contact_info: {
        phone: "",
        linkedin_url: "",
        github_url: "",
        portfolio_url: ""
      },
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
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setProfileData(data.profile_json);
          setProfileExists(true);
        } else {
          throw new Error("Profile API not completed");
        }
      } catch (e) {
        // Fallback to localStorage
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
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      } else {
        console.error("Failed to fetch insights");
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
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
        triggerToast("AI career insights updated!");
      } else {
        const errData = await res.json();
        console.error("Failed to generate insights:", errData);
        triggerToast(errData.detail || "Failed to generate insights.");
      }
    } catch (err) {
      console.error("Error generating insights:", err);
      triggerToast("Error connecting to server to generate insights.");
    } finally {
      setLoadingInsights(false);
    }
  };

  useEffect(() => {
    if (profileExists) {
      fetchInsights();
    }
  }, [profileExists, token]);

  // Calculate dynamic Profile Strength percentage
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

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 4000);
  };

  // Frontend client-side resume extraction using PDF.js
  const handleResumeUpload = (file) => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadingStepText("Uploading resume...");

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target.result;
        
        // Fetch PDF.js library instance from window
        const pdfjsLib = window.pdfjsLib;
        if (!pdfjsLib) {
          throw new Error("PDF.js library not loaded yet.");
        }
        
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
        setUploadingStepText("Logging output...");

        // PRINT THE EXTRACTED OUTPUT ON THE CONSOLE WINDOW
        console.log("=========================================");
        console.log("=== CLIENT-SIDE EXTRACTED RESUME TEXT ===");
        console.log("=========================================");
        console.log(fullText);
        console.log("=========================================");

        setUploadingStepText("AI Resume Parsing...");
        setUploadProgress(80);

        // Make the API call to backend
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
          
          // Add temporary local IDs to experience, education, projects for key/editing state handling
          if (resumeData.experience) {
            resumeData.experience = resumeData.experience.map((exp, idx) => ({
              ...exp,
              id: Date.now() + 10 + idx
            }));
          }
          if (resumeData.education) {
            resumeData.education = resumeData.education.map((edu, idx) => ({
              ...edu,
              id: Date.now() + 20 + idx
            }));
          }
          if (resumeData.projects) {
            resumeData.projects = resumeData.projects.map((proj, idx) => ({
              ...proj,
              id: Date.now() + 30 + idx
            }));
          }
          if (resumeData.certifications) {
            resumeData.certifications = resumeData.certifications.map((cert, idx) => ({
              ...cert,
              id: Date.now() + 40 + idx
            }));
          }

          setProfileData({
            resume_data: {
              contact_info: resumeData.contact_info || { phone: "", linkedin_url: "", github_url: "", portfolio_url: "" },
              summary: resumeData.summary || "",
              skills: resumeData.skills || [],
              experience: resumeData.experience || [],
              education: resumeData.education || [],
              projects: resumeData.projects || [],
              certifications: resumeData.certifications || [],
              co_curricular_activities: resumeData.co_curricular_activities || []
            },
            preferences: {
              preferred_roles: resumeData.preferred_roles || [],
              preferred_locations: resumeData.preferred_locations || [],
              experience_level: "" // start empty to force selection
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
            triggerToast("Resume successfully parsed by AI!");
          }, 800);

        } catch (apiErr) {
          console.warn("Backend parser failed (e.g. unconfigured keys). Falling back to mock details.", apiErr);
          
          // Setup mockup fallbacks
          const parsedName = user?.name || "Alex Chen";
          const cleanName = parsedName.toLowerCase().replace(/\s+/g, "");

          const parsedMockData = {
            resume_data: {
              contact_info: {
                phone: "+1 (555) 304-2831",
                linkedin_url: `https://linkedin.com/in/${cleanName}`,
                github_url: `https://github.com/${cleanName}`,
                portfolio_url: `https://${cleanName}.dev`
              },
              summary: `Innovative and results-driven software professional with 5+ years of experience specializing in building scalable applications, orchestrating cloud architecture, and automating CI/CD pipelines. Passionate about leveraging AI for high-velocity career placements.`,
              skills: ["React", "Node.js", "AWS", "Docker", "Kubernetes", "Python", "SQL", "Terraform", "CI/CD", "Git", "TypeScript"],
              experience: [
                {
                  id: Date.now() + 1,
                  company: "CloudScale Solutions",
                  role: "Senior DevOps Engineer",
                  start_date: "2022-03",
                  end_date: "Present",
                  description: "Led AWS migration project, decreasing hosting costs by 30%. Built automated infrastructure using Terraform and streamlined deployments with GitHub Actions. Mentored a team of 4 junior builders."
                },
                {
                  id: Date.now() + 2,
                  company: "AlphaTech Corp",
                  role: "Software Developer",
                  start_date: "2019-06",
                  end_date: "2022-02",
                  description: "Developed robust full-stack features using React and Express.js. Redesigned PostgreSQL schemas, boosting search performance by 25%. Directed regression code coverage initiatives."
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
              projects: [
                {
                  id: Date.now() + 4,
                  title: "Cloud Migration Pipeline",
                  description: "Containerized 15 monolithic microservices with Docker and deployed to AWS EKS via Kubernetes configurations.",
                  technologies: ["Docker", "Kubernetes", "AWS"]
                }
              ],
              certifications: [
                {
                  id: Date.now() + 5,
                  name: "AWS Certified Solutions Architect - Associate",
                  issuer: "Amazon Web Services",
                  year: "2023",
                  url: "https://aws.amazon.com/verification"
                },
                {
                  id: Date.now() + 6,
                  name: "Certified Kubernetes Administrator (CKA)",
                  issuer: "The Linux Foundation",
                  year: "2024",
                  url: ""
                }
              ],
              co_curricular_activities: [
                "Winner of National Level Hackathon (Hack India 2023)",
                "Open Source contributor to Kubernetes and local tech communities",
                "Organizer of campus programming contests"
              ]
            },
            preferences: {
              preferred_roles: ["Frontend Developer", "DevOps Engineer", "Software Engineer"],
              preferred_locations: ["Remote", "Pune", "San Francisco"],
              experience_level: "2-5 Years"
            },
            resume_metadata: {
              file_name: file.name,
              uploaded_at: new Date().toISOString()
            }
          };

          setUploadProgress(100);
          setUploadingStepText("Demo loading complete!");

          setTimeout(() => {
            setProfileData(parsedMockData);
            setIsUploading(false);
            setActiveStep(2);
            triggerToast("Backend unconfigured or unreachable. Using mock data for demo.");
          }, 850);
        }

      } catch (err) {
        console.error("Failed to parse PDF on frontend:", err);
        setUploadingStepText("Parsing failed. Proceeding manually...");
        setTimeout(() => {
          setIsUploading(false);
          setActiveStep(2);
          triggerToast("Failed to parse PDF. Please verify details manually.");
        }, 1500);
      }
    };
    reader.onerror = (err) => {
      console.error("FileReader error:", err);
      setIsUploading(false);
      triggerToast("File reading error. Please try again.");
    };
    reader.readAsArrayBuffer(file);
  };

  // Complete onboarding wizard action
  const handleCompleteOnboarding = async () => {
    // Basic validations
    if (!profileData.preferences.preferred_roles || profileData.preferences.preferred_roles.length === 0) {
      triggerToast("Please add at least one preferred role.");
      setActiveStep(3);
      return;
    }
    if (!profileData.preferences.preferred_locations || profileData.preferences.preferred_locations.length === 0) {
      triggerToast("Please add at least one preferred location.");
      setActiveStep(3);
      return;
    }
    if (!profileData.preferences.experience_level) {
      triggerToast("Please select your experience level.");
      setActiveStep(3);
      return;
    }

    setLoading(true);

    // Sanitize experience, education, projects, certifications by removing UI-only temp IDs
    const cleanExperience = (profileData.resume_data.experience || []).map(({ id, ...rest }) => rest);
    const cleanEducation = (profileData.resume_data.education || []).map(({ id, ...rest }) => rest);
    const cleanProjects = (profileData.resume_data.projects || []).map(({ id, ...rest }) => rest);
    const cleanCertifications = (profileData.resume_data.certifications || []).map(({ id, ...rest }) => rest);

    const payload = {
      resume_data: {
        ...profileData.resume_data,
        experience: cleanExperience,
        education: cleanEducation,
        projects: cleanProjects,
        certifications: cleanCertifications
      },
      preferences: profileData.preferences,
      resume_metadata: profileData.resume_metadata
    };

    try {
      const res = await fetch("http://localhost:8000/profile/complete-onboarding", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to complete onboarding.");
      }

      // Store locally for offline/stub-compliant persistence fallback
      localStorage.setItem("jobpilot_candidate_profile", JSON.stringify(payload));
      localStorage.setItem("jobpilot_has_profile", "true");
      
      // Sync auth context
      setHasProfile(true);
      setProfileExists(true);
      triggerToast("Career context saved! Welcome to your JobPilot dashboard.");
      navigate('/dashboard');
    } catch (err) {
      console.error("Failed to complete onboarding:", err);
      triggerToast(err.message || "Error saving profile. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Save changes in settings view mode
  const handleSaveProfileChanges = async () => {
    const cleanExperience = (profileData.resume_data.experience || []).map(({ id, ...rest }) => rest);
    const cleanEducation = (profileData.resume_data.education || []).map(({ id, ...rest }) => rest);
    const cleanProjects = (profileData.resume_data.projects || []).map(({ id, ...rest }) => rest);
    const cleanCertifications = (profileData.resume_data.certifications || []).map(({ id, ...rest }) => rest);

    const payload = {
      resume_data: {
        ...profileData.resume_data,
        experience: cleanExperience,
        education: cleanEducation,
        projects: cleanProjects,
        certifications: cleanCertifications
      },
      preferences: profileData.preferences,
      resume_metadata: profileData.resume_metadata
    };

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/profile/complete-onboarding", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error("Failed to update profile on backend");
      }

      localStorage.setItem("jobpilot_candidate_profile", JSON.stringify(payload));
      setEditingSection(null);
      triggerToast("Profile section updated successfully!");
      fetchInsights();
    } catch (err) {
      console.error("Failed to save profile changes:", err);
      localStorage.setItem("jobpilot_candidate_profile", JSON.stringify(payload));
      setEditingSection(null);
      triggerToast("Failed to save changes on backend. Stored locally.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#f8f9ff]">
        <div className="text-center">
          <Icon name="progress_activity" className="text-[48px] text-primary animate-spin" />
          <p className="mt-4 text-[14px] text-on-surface-variant font-medium">Syncing profile data...</p>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        ...themeVars,
        fontFamily: "'Inter', sans-serif",
        backgroundColor: "var(--color-background)",
        color: "var(--color-on-background)",
        minHeight: "100vh",
      }}
      className="selection:bg-[var(--color-primary-container)] selection:text-[var(--color-on-primary-container)]"
    >
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />

      {/* Global Toast */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-inverse-surface text-inverse-on-surface py-3 px-5 rounded-xl shadow-xl animate-bounce">
          <Icon name="check_circle" fill className="text-[20px] text-primary-fixed-dim" />
          <span className="text-body-sm font-semibold">{toastMessage}</span>
        </div>
      )}

      <div className="flex h-screen overflow-hidden">
        {/* Left Sidebar Layout */}
        <Sidebar activeItem="profile" bottomCard={<UserProfileCard name={user?.name || "Candidate"} statusLabel={profileExists ? "Profile Setup Done" : "Incomplete Profile"} />} />

        {/* Middle content area */}
        {profileExists === false ? (
          /* Stepper Wizard */
          <main className="flex-1 h-full overflow-y-auto" style={{ backgroundColor: "rgba(248,249,255,0.4)" }}>
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
              triggerToast={triggerToast}
              user={user}
            />
          </main>
        ) : (
          /* Profile Settings Portal */
          <>
            <main className="flex-1 h-full overflow-y-auto" style={{ backgroundColor: "rgba(248,249,255,0.4)" }}>
              <div className="p-8 space-y-6 max-w-4xl mx-auto">
                <div>
                  <h2 className="text-[32px] font-semibold text-on-surface tracking-tight">Profile Settings</h2>
                  <p className="text-on-surface-variant text-[15px]">Verify your candidate details and preferences matching your job applications.</p>
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
            </main>

            {/* Right Column: AI Analytics & Resume Manager */}
            <AIInsightsPanel
              profileData={profileData}
              strengthScore={calculateStrength()}
              triggerToast={triggerToast}
              setProfileExists={setProfileExists}
              setActiveStep={setActiveStep}
              insights={insights}
              loadingInsights={loadingInsights}
              refetchInsights={fetchInsights}
              generateInsights={generateInsights}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default Profile;
