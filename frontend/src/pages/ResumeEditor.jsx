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
          const response = await fetch(`${API_BASE_URL}/api/resume/${id}`, {
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
    
    try {
      // The resume state ID is used to continue the graph
      const resumeId = resumeState.resume_id;
      
      const response = await fetch(`${API_BASE_URL}/api/resume/${resumeId}/continue/stream`, {
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

      await readStream(response.body.getReader());
    } catch (err) {
      console.error(err);
      setError(err.message || "An error occurred");
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

  const readStream = async (reader) => {
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // keep the incomplete chunk

      for (const block of lines) {
        if (block.startsWith('event: close')) {
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
            const data = JSON.parse(dataStr);
            setResumeState(data);
            checkHitlStatus(data);
          } catch (e) {
            console.error("Failed to parse SSE JSON:", e, dataStr);
          }
        }
      }
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

  return (
    <AppShell breadcrumbs={[
      { label: "Dashboard", href: "/dashboard" },
      { label: "Resumes", href: "/resumes" },
      { label: isNew ? "New Resume" : "Edit Resume" },
    ]}>
      <div className="h-[calc(100vh-64px)] w-full flex overflow-hidden bg-jp-bg-app">
        {/* Left Panel: Controls */}
        <div className="w-[400px] border-r border-jp-border-subtle bg-jp-bg-raised flex flex-col relative">
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
          />
        </div>
        
        {/* Right Panel: Live Preview */}
        <div className="flex-1 overflow-y-auto bg-jp-bg-app p-8 flex justify-center">
          <div className="w-full max-w-4xl">
             <ResumePreview 
               resumeContent={resumeState?.resume_content} 
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
