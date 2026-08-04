import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import ControlPanel from '../components/resume/ControlPanel';
import ResumePreview from '../components/resume/ResumePreview';
import Icon from '../components/common/Icon';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function ResumeEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = id === 'new';

  const [resumeState, setResumeState] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [waitingForUser, setWaitingForUser] = useState(false);
  const [error, setError] = useState(null);
  const [isFetchingState, setIsFetchingState] = useState(!isNew);
  
  // Track the underlying EventSource to close it if needed
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!isNew && id) {
      const fetchResumeState = async () => {
        setIsFetchingState(true);
        try {
          const response = await fetch(`${API_BASE_URL}/api/v2/resume/${id}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          if (response.ok) {
            const data = await response.json();
            setResumeState(data);
            checkHitlStatus(data);
          } else {
            console.error("Failed to fetch existing resume:", response.status);
            alert("Failed to fetch resume state from server! Check backend logs.");
          }
        } catch (err) {
          console.error("Error fetching resume state", err);
          alert("Network error fetching resume state!");
        } finally {
          setIsFetchingState(false);
        }
      };
      fetchResumeState();
    } else {
      setIsFetchingState(false);
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [id, isNew]);

  const startGeneration = async (userQuery, jobDescription) => {
    setIsGenerating(true);
    setWaitingForUser(false);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/resume/generate/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_query: userQuery || "",
          target_job_description: jobDescription || "General Software Engineering Role"
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start generation');
      }

      await readStream(response.body.getReader());
    } catch (err) {
      console.error(err);
      setError(err.message || "An error occurred");
      setIsGenerating(false);
    }
  };

  const sendMessage = async (message, sectionToEdit = null) => {
    if (!resumeState) return;
    
    setIsGenerating(true);
    setWaitingForUser(false);
    setError(null);
    
    // Optimistically add user message
    const newUserMsg = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: message,
      created_at: new Date().toISOString()
    };
    
    setResumeState(prev => ({
      ...prev,
      messages: [...(prev.messages || []), newUserMsg]
    }));
    
    try {
      const targetId = resumeState.id || resumeState.resume_id || id;
      
      const response = await fetch(`${API_BASE_URL}/api/v2/resume/${targetId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: message
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      const newAiMsg = {
        id: Date.now().toString() + 'ai',
        role: 'assistant',
        content: data.reply,
        created_at: new Date().toISOString()
      };
      
      setResumeState(prev => ({
        ...prev,
        drafts: data.drafts,
        pending_sections: data.pending_sections,
        messages: [...(prev.messages || []), newAiMsg]
      }));

    } catch (err) {
      console.error(err);
      setError(err.message || "An error occurred");
    } finally {
      setIsGenerating(false);
    }
  };

  const retryGeneration = async () => {
    if (!resumeState || !resumeState.resume_id) return;
    
    setIsGenerating(true);
    setWaitingForUser(false);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/resume/${resumeState.resume_id}/retry/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to retry generation');
      }

      await readStream(response.body.getReader());
    } catch (err) {
      console.error(err);
      setError(err.message || "An error occurred");
      setIsGenerating(false);
    }
  };

  const cancelGeneration = async () => {
    if (!resumeState || !resumeState.resume_id) return;
    try {
      await fetch(`${API_BASE_URL}/api/resume/${resumeState.resume_id}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setIsGenerating(false);
    } catch (err) {
      console.error("Failed to cancel generation:", err);
    }
  };

  const readStream = async (reader) => {
    const decoder = new TextDecoder();
    let buffer = '';
    let receivedClose = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // keep the incomplete chunk

      for (const block of lines) {
        if (block.startsWith('event: close')) {
          receivedClose = true;
          setIsGenerating(false);
          checkHitlStatus(resumeState);
          return;
        }
        
        if (block.startsWith('event: error')) {
          const lines = block.split('\n');
          const dataLine = lines.find(l => l.startsWith('data: '));
          if (dataLine) {
            try {
              const data = JSON.parse(dataLine.slice(6));
              setError(data.detail || "Generation failed.");
            } catch (e) {
              setError("An unknown error occurred during generation.");
            }
          } else {
            setError("An unknown error occurred during generation.");
          }
          setIsGenerating(false);
          return;
        }

        if (block.startsWith('data: ')) {
          const dataStr = block.slice(6);
          try {
            const parsed = JSON.parse(dataStr);
            const data = parsed.state ? parsed.state : parsed;
            setResumeState(data);
            checkHitlStatus(data);
          } catch (e) {
            console.error("Failed to parse SSE JSON:", e, dataStr);
          }
        }
      }
    }
    
    if (!receivedClose) {
      setError("Connection lost unexpectedly. Please hit Retry Generation.");
    }
    
    setIsGenerating(false);
    // Double check HITL when stream ends
    setResumeState(prev => {
      checkHitlStatus(prev);
      return prev;
    });
  };

  const checkHitlStatus = (state) => {
    if (!state || !state.messages || state.messages.length === 0) return;
    const lastMsg = state.messages[state.messages.length - 1];
    if (lastMsg && lastMsg.message_type === 'HUMAN_INPUT_REQUEST') {
      setWaitingForUser(true);
      setIsGenerating(false);
    } else {
      setWaitingForUser(false);
    }
  };

  const mapDraftsToResumeContent = (drafts) => {
    if (!drafts) return null;
    const sections = [];
    
    // Helper to safely get the latest version from a draft array
    const getLatest = (draftArray) => {
      if (!draftArray || !Array.isArray(draftArray) || draftArray.length === 0) return null;
      return draftArray[draftArray.length - 1];
    };

    // Helper to map V2 keys to V1 keys for ResumePreview
    const mapItems = (items, type) => {
      if (!items || !Array.isArray(items)) return items;
      return items.map(item => {
        const mapped = { ...item };
        // Map tech_stack to technologies
        if (mapped.tech_stack) {
          mapped.technologies = mapped.tech_stack;
        }
        // Map bullet_points to highlights
        if (mapped.bullet_points) {
          mapped.highlights = mapped.bullet_points;
        }
        return mapped;
      });
    };

    const basicInfo = getLatest(drafts.basic_info);
    if (basicInfo) sections.push({ section_type: 'PERSONAL_INFORMATION', content: basicInfo });

    const summary = getLatest(drafts.summary);
    if (summary) sections.push({ section_type: 'SUMMARY', content: summary });

    const experience = getLatest(drafts.experience);
    if (experience) sections.push({ section_type: 'EXPERIENCE', content: mapItems(experience, 'experience') });

    const projects = getLatest(drafts.projects);
    if (projects) sections.push({ section_type: 'PROJECTS', content: mapItems(projects, 'projects') });

    const skills = getLatest(drafts.skills);
    if (skills) sections.push({ section_type: 'SKILLS', content: skills });

    const education = getLatest(drafts.education);
    if (education) sections.push({ section_type: 'EDUCATION', content: education });

    const certifications = getLatest(drafts.certifications);
    if (certifications) sections.push({ section_type: 'CERTIFICATIONS', content: certifications });

    // Handle Custom Sections (which is a dictionary in the latest version of drafts.custom)
    const customSectionsDict = getLatest(drafts.custom);
    if (customSectionsDict && typeof customSectionsDict === 'object') {
      Object.keys(customSectionsDict).forEach(key => {
        if (key && customSectionsDict[key] && customSectionsDict[key].length > 0) {
          // You can map to CO_CURRICULAR or just CUSTOM depending on your UI support.
          // ResumePreview might just need section_type and section_name
          sections.push({ 
            section_type: 'CUSTOM', 
            section_name: key, // Pass the dynamic name down
            content: mapItems(customSectionsDict[key], 'custom') 
          });
        }
      });
    }

    return { sections };
  };

  const previewContent = resumeState?.resume_content || mapDraftsToResumeContent(resumeState?.drafts);

  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "Resumes", href: "/resumes" },
      { label: isNew ? "New Resume" : "Edit Resume" },
    ]}>
      <div className="h-[calc(100vh-64px)] w-full flex overflow-hidden bg-jp-bg-app relative">
        {/* Subtle dynamic background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-jp-accent/5 via-jp-bg-app to-jp-bg-app pointer-events-none" />
        
        {/* Left Panel: Controls */}
        <div className="w-[400px] border-r border-jp-border-subtle bg-jp-bg-raised/80 backdrop-blur-md flex flex-col relative z-10 shadow-[4px_0_24px_rgba(0,0,0,0.2)]">
          {isFetchingState && (
            <div className="absolute inset-0 bg-jp-bg-raised/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center">
              <Icon name="autorenew" className="animate-spin text-jp-accent text-3xl mb-2" />
              <p className="text-sm text-jp-text-secondary">Loading resume data...</p>
            </div>
          )}
          <ControlPanel 
            resumeState={resumeState} 
            isGenerating={isGenerating} 
            waitingForUser={waitingForUser}
            error={error}
            onSendMessage={sendMessage}
            onStartGeneration={startGeneration}
            onRetry={retryGeneration}
            onCancel={cancelGeneration}
          />
        </div>
        
        {/* Right Panel: Live Preview */}
        <div className="flex-1 overflow-y-auto p-12 flex justify-center relative z-0 hide-scrollbar">
          <div className="w-full max-w-4xl">
             <ResumePreview 
               resumeContent={previewContent} 
               onEditRequest={(section, prompt) => sendMessage(prompt, section)} 
               isGenerating={isGenerating}
             />
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default ResumeEditor;
