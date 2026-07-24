from enum import Enum
from typing import Union
from pydantic import BaseModel

from .personal_information import PersonalInformation
from .summary import ProfessionalSummary
from .experience import ExperienceEntry
from .projects import ProjectEntry
from .skills import SkillCategory
from .education import EducationEntry
from .certifications import CertificationEntry
from .achievements import AchievementEntry
from .leadership import PositionOfResponsibilityEntry
from .internships import InternshipEntry
from .publications import PublicationEntry
from .research import ResearchEntry
from .patents import PatentEntry
from .open_source import OpenSourceContributionEntry
from .volunteer import VolunteerEntry
from .languages import LanguageEntry
from .awards import AwardEntry
from .training import TrainingEntry
from .workshops import WorkshopEntry
from .interests import InterestEntry
from .references import ReferenceEntry
from .co_curricular import CoCurricularActivity

class ResumeSectionType(str, Enum):
    PERSONAL_INFORMATION = "PERSONAL_INFORMATION"
    SUMMARY = "SUMMARY"
    EXPERIENCE = "EXPERIENCE"
    PROJECTS = "PROJECTS"
    SKILLS = "SKILLS"
    EDUCATION = "EDUCATION"
    CERTIFICATIONS = "CERTIFICATIONS"
    ACHIEVEMENTS = "ACHIEVEMENTS"
    POSITIONS_OF_RESPONSIBILITY = "POSITIONS_OF_RESPONSIBILITY"
    INTERNSHIPS = "INTERNSHIPS"
    PUBLICATIONS = "PUBLICATIONS"
    RESEARCH = "RESEARCH"
    PATENTS = "PATENTS"
    CO_CURRICULAR = "CO_CURRICULAR"
    OPEN_SOURCE = "OPEN_SOURCE"
    VOLUNTEER = "VOLUNTEER"
    LANGUAGES = "LANGUAGES"
    AWARDS = "AWARDS"
    TRAINING = "TRAINING"
    WORKSHOPS = "WORKSHOPS"
    INTERESTS = "INTERESTS"
    REFERENCES = "REFERENCES"
    CUSTOM = "CUSTOM"

class ResumeSectionState(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    WAITING_FOR_USER = "WAITING_FOR_USER"

class GenericSection(BaseModel):
    title: str
    content: list[str]

class ResumeSection(BaseModel):
    section_type: ResumeSectionType
    display_name: str
    status: ResumeSectionState
    content: Union[
        PersonalInformation,
        ProfessionalSummary,
        list[ExperienceEntry],
        list[ProjectEntry],
        list[SkillCategory],
        list[EducationEntry],
        list[CertificationEntry],
        list[AchievementEntry],
        list[PositionOfResponsibilityEntry],
        list[InternshipEntry],
        list[PublicationEntry],
        list[ResearchEntry],
        list[PatentEntry],
        list[OpenSourceContributionEntry],
        list[VolunteerEntry],
        list[LanguageEntry],
        list[AwardEntry],
        list[TrainingEntry],
        list[WorkshopEntry],
        list[InterestEntry],
        list[ReferenceEntry],
        list[CoCurricularActivity],
        GenericSection
    ]

class ResumeContent(BaseModel):
    sections: list[ResumeSection]
