import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.resume import Resume, ResumeContentModel, ResumeMessageModel
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage

class ResumeRepository:
    """
    Pure persistence layer for the Resume Tailoring Agent.
    Executes all database operations and contains zero graph orchestration or business logic.
    """
    def __init__(self, db: Session):
        self.db = db

    def create_resume(self, user_id: uuid.UUID, title: str = "Tailored Resume") -> Resume:
        resume = Resume(
            user_id=user_id,
            title=title,
            status="GENERATING"
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_resume_by_id(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Resume]:
        return self.db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()

    def rename_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID, title: str) -> Optional[Resume]:
        resume = self.get_resume_by_id(resume_id, user_id)
        if resume:
            resume.title = title
            self.db.commit()
            self.db.refresh(resume)
        return resume

    def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        resume = self.get_resume_by_id(resume_id, user_id)
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    def update_resume_status(self, resume_id: uuid.UUID, status: str) -> Optional[Resume]:
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.status = status
            self.db.commit()
            self.db.refresh(resume)
        return resume

    def save_resume_content(self, resume_id: uuid.UUID, content_dict: Dict[str, Any]) -> ResumeContentModel:
        content_record = self.db.query(ResumeContentModel).filter(
            ResumeContentModel.resume_id == resume_id
        ).first()

        if not content_record:
            content_record = ResumeContentModel(
                resume_id=resume_id,
                data=content_dict
            )
            self.db.add(content_record)
        else:
            content_record.data = content_dict

        self.db.commit()
        self.db.refresh(content_record)
        return content_record

    def save_messages(self, resume_id: uuid.UUID, messages: List[ResumeMessage]) -> List[ResumeMessageModel]:
        # Clear existing messages for this resume (simple append strategy for MVP to ensure sync)
        # Or we can just insert new ones by ID. LangGraph states typically have cumulative messages.
        # Let's do an upsert or bulk delete/insert for simplicity since the graph state is the source of truth.
        self.db.query(ResumeMessageModel).filter(ResumeMessageModel.resume_id == resume_id).delete()
        
        message_models = []
        for msg in messages:
            msg_model = ResumeMessageModel(
                id=msg.id,
                resume_id=resume_id,
                role=msg.role,
                message_type=msg.message_type,
                from_node=msg.from_node,
                to_node=msg.to_node,
                related_section=msg.related_section,
                content=msg.content,
                payload=msg.payload
            )
            message_models.append(msg_model)
            
        self.db.add_all(message_models)
        self.db.commit()
        return message_models
