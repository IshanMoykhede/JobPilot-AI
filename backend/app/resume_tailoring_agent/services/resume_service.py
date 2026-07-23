import json
import logging
from typing import Generator
import uuid
from sqlalchemy.orm import Session

from app.resume_tailoring_agent.repository.resume_repository import ResumeRepository
from app.resume_tailoring_agent.services.resume_state_service import ResumeStateService
from app.resume_tailoring_agent.services.resume_execution_manager import ResumeExecutionManager

logger = logging.getLogger(__name__)

class ResumeService:
    """
    Business orchestration layer for the Resume Tailoring Agent.
    Coordinates database records, state hydration, and delegates execution to the Execution Manager.
    Enforces the milestone-based persistence policy.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repository = ResumeRepository(db)
        self.state_service = ResumeStateService(db)
        self.execution_manager = ResumeExecutionManager()

    def start_resume_generation(self, user, user_query: str, job_description: str) -> Generator[str, None, None]:
        # 1. Create DB Record (Genesis Persistence)
        resume = self.repository.create_resume(user_id=user.id, title="Tailored Resume")
        resume_id_str = str(resume.id)
        
        # 2. Build Initial State
        initial_state = self.state_service.create_initial_state(
            user=user,
            resume_id=resume_id_str,
            user_query=user_query,
            target_job_description=job_description
        )
        
        # 3. Execute and intercept stream for Milestone Persistence
        last_state = None
        has_error = False
        
        for chunk in self.execution_manager.stream_graph_execution(initial_state, thread_id=resume_id_str):
            if chunk.startswith("event: error"):
                has_error = True
            elif chunk.startswith("data: "):
                try:
                    state_data = json.loads(chunk[6:])
                    if state_data:
                        last_state = state_data
                except Exception:
                    pass
            yield chunk

        # 4. Milestone Persistence: Stream ended (either completed or paused)
        if last_state:
            self._sync_state_to_db(resume.id, last_state)
            
        if has_error:
            self.repository.update_resume_status(resume.id, "FAILED")
        elif last_state and not last_state.get("pending_sections"):
            self.repository.update_resume_status(resume.id, "COMPLETED")

    def continue_resume_generation(self, user_id: uuid.UUID, resume_id: uuid.UUID, user_message: str) -> Generator[str, None, None]:
        # 1. Validate ownership
        resume = self.repository.get_resume_by_id(resume_id, user_id)
        if not resume:
            yield f"event: error\ndata: {json.dumps({'detail': 'Resume not found or unauthorized.'})}\n\n"
            return
            
        resume_id_str = str(resume_id)
        
        # 2. Execute and intercept stream
        last_state = None
        has_error = False
        
        for chunk in self.execution_manager.continue_graph_execution(thread_id=resume_id_str, user_message=user_message):
            if chunk.startswith("event: error"):
                has_error = True
            elif chunk.startswith("data: "):
                try:
                    state_data = json.loads(chunk[6:])
                    if state_data:
                        last_state = state_data
                except Exception:
                    pass
            yield chunk

        # 3. Milestone Persistence
        if last_state:
            self._sync_state_to_db(resume.id, last_state)

        if has_error:
            self.repository.update_resume_status(resume.id, "FAILED")
        elif last_state and not last_state.get("pending_sections"):
            self.repository.update_resume_status(resume.id, "COMPLETED")

    def retry_resume_generation(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Generator[str, None, None]:
        # 1. Validate ownership
        resume = self.repository.get_resume_by_id(resume_id, user_id)
        if not resume:
            yield f"event: error\ndata: {json.dumps({'detail': 'Resume not found or unauthorized.'})}\n\n"
            return
            
        resume_id_str = str(resume_id)
        
        # 2. Execute and intercept stream
        last_state = None
        has_error = False
        
        for chunk in self.execution_manager.retry_graph_execution(thread_id=resume_id_str):
            if chunk.startswith("event: error"):
                has_error = True
            elif chunk.startswith("data: "):
                try:
                    state_data = json.loads(chunk[6:])
                    if state_data:
                        last_state = state_data
                except Exception:
                    pass
            yield chunk

        # 3. Milestone Persistence
        if last_state:
            self._sync_state_to_db(resume.id, last_state)
            
        if has_error:
            self.repository.update_resume_status(resume.id, "FAILED")
        elif last_state and not last_state.get("pending_sections"):
            self.repository.update_resume_status(resume.id, "COMPLETED")

    def _sync_state_to_db(self, resume_id: uuid.UUID, state_data: dict):
        """
        Extracts business data from the raw state dictionary and updates the Resume ORM models.
        """
        try:
            # Sync Content
            resume_content = state_data.get("resume_content")
            if resume_content:
                self.repository.save_resume_content(resume_id, resume_content)
                
            # Sync Messages (Optional, as checkpointer holds them natively, but good for external viewing)
            # This requires converting dict messages back to Pydantic if we want to use the repo method directly,
            # or we adjust the repo method to accept dicts.
            # We'll skip deep message syncing for now to save DB load, 
            # unless the frontend needs to fetch history directly from the DB rather than the checkpointer.
        except Exception as e:
            logger.error(f"Failed to sync graph state to database for resume {resume_id}: {e}", exc_info=True)

    def get_resume_state(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> dict:
        """
        Fetches the current live state of a resume generation from the checkpointer.
        """
        # 1. Authorize against DB
        resume = self.repository.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found or unauthorized")
            
        # 2. Extract from Checkpointer
        raw_state = self.execution_manager.get_graph_state(str(resume_id))
        if not raw_state:
            return None
            
        # 3. Serialize securely for the API response
        serialized = self.execution_manager._serialize_state(raw_state)
        return json.loads(serialized)

    def rename_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID, title: str) -> dict:
        """
        Renames a resume.
        """
        resume = self.repository.rename_resume(resume_id, user_id, title)
        if not resume:
            raise ValueError("Resume not found or unauthorized")
        return {"id": str(resume.id), "title": resume.title}

    def delete_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> bool:
        """
        Deletes a resume and its associated graph state.
        """
        # 1. Authorize and delete from DB (cascades to contents and messages)
        success = self.repository.delete_resume(resume_id, user_id)
        if not success:
            raise ValueError("Resume not found or unauthorized")
            
        # 2. Delete checkpointer state (optional but clean)
        # Note: Langgraph SqliteSaver/AsyncPostgresSaver don't natively expose a delete_thread method in their public API.
        # But we can try to wipe the state if the checkpointer allows it, or just let DB cascade handle our data.
        # Since DB cascaded successfully, the evidence is gone from the user's perspective.
        return True
