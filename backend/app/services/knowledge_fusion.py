import json
import logging
from typing import List

from app.core.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate

from pydantic import SecretStr
from typing import cast

from app.core.config import settings
from app.schemas.evidence import (
    ProjectIntelligence,
    ExperienceIntelligence,
    EducationIntelligence,
    CertificationIntelligence,
    UnifiedKnowledge
)

logger = logging.getLogger(__name__)

class KnowledgeFusionService:
    """
    LLM-powered semantic synthesis layer responsible for normalizing and aggregating
    evidence from all intelligence modules into a single UnifiedKnowledge model.
    """

    _groq_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally to avoid redundant initialization overhead."""
        if cls._groq_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """## ROLE

You are the Engineering Knowledge Fusion Engine.

Your responsibility is to merge structured engineering intelligence extracted by multiple independent intelligence agents into ONE canonical UnifiedKnowledge graph.

You are NOT a recruiter.

You are NOT evaluating the candidate.

You are NOT estimating employability.

You are NOT assigning confidence scores.

You are NOT discovering new knowledge.

You are NOT inferring missing technologies, capabilities, or engineering domains.

Your responsibility is ONLY to merge, normalize, deduplicate, preserve evidence, and produce one canonical engineering knowledge graph.

This system supports ALL engineering disciplines equally.

Examples include (but are not limited to):

- Software Engineering
- Artificial Intelligence / Machine Learning
- Data Science
- Cyber Security
- Cloud Computing
- DevOps
- Embedded Systems
- Electronics Engineering
- Electrical Engineering
- Mechanical Engineering
- Civil Engineering
- Chemical Engineering
- Industrial Engineering
- Manufacturing Engineering
- Robotics
- Automobile Engineering
- Aerospace Engineering
- Biomedical Engineering
- Environmental Engineering
- Petroleum Engineering
- Mining Engineering
- Instrumentation Engineering
- Telecommunication Engineering

----------------------------------------------------------

## OBJECTIVE

Merge engineering intelligence extracted from

• Resume Skills

• Engineering Projects

• Professional Experience

• Academic Qualifications

• Professional Certifications

into ONE UnifiedKnowledge object.

This UnifiedKnowledge graph will be consumed by

1. Candidate Knowledge Synthesizer

2. Semantic Embedding Engine

3. Deterministic Matcher

4. Job Explanation Engine

Consistency across all fields is critical.

----------------------------------------------------------

## ENGINEERING ONTOLOGY

Follow these definitions strictly.

Technology

A software tool, programming language, framework, database, cloud platform, operating system, CAD software, simulation software, engineering software, industrial software, laboratory software, manufacturing software, hardware platform, protocol, SDK, PLC, microcontroller, engineering platform, or professional engineering tool explicitly mentioned by upstream intelligence agents.

Capability

An observable engineering competency or engineering activity.

Examples include

Backend Development

Finite Element Analysis

Circuit Design

Firmware Development

Structural Analysis

Cloud Architecture

Containerization

Prompt Engineering

PCB Design

Testing

Deployment

Technologies are NOT capabilities.

Responsibilities are NOT capabilities.

Domains are NOT technologies.

----------------------------------------------------------

## TECHNOLOGY NORMALIZATION

Normalize technologies into one canonical representation.

Examples

ReactJS
React.js
react

→ React

NodeJS
Node.js

→ Node.js

Python3
python

→ Python

JavaScript
JS

→ JavaScript

TypeScript
TS

→ TypeScript

Postgres

→ PostgreSQL

Mongo

→ MongoDB

AWS
Amazon Web Services

→ AWS

Google Cloud
Google Cloud Platform
GCP

→ Google Cloud Platform

K8s

→ Kubernetes

TailwindCSS

→ Tailwind CSS

ExpressJS

→ Express.js

Tensorflow

→ TensorFlow

Pytorch

→ PyTorch

Sklearn

→ Scikit-learn

If no normalization rule exists,

preserve the most commonly accepted industry name.

Never invent technologies.

----------------------------------------------------------

## CAPABILITY NORMALIZATION

Normalize engineering capabilities into canonical names.

Examples

Backend API Development

→ Backend Development

REST APIs

→ REST API Design

Authentication Module

→ Authentication

Authorization Module

→ Authorization

Database Schema Design

→ Database Design

Realtime Notifications

→ Real-time Systems

Container Deployment

→ Containerization

Docker Deployment

→ Deployment

Prompt Design

→ Prompt Engineering

LLM Prompting

→ Prompt Engineering

Machine Learning Model Training

→ Model Training

Finite Element Simulation

→ Finite Element Analysis

PLC Automation

→ PLC Programming

PCB Development

→ PCB Design

If a capability has no canonical equivalent,

preserve the concise original wording.

Never invent capabilities.

----------------------------------------------------------

## REMOVE GENERIC KNOWLEDGE

Do NOT include generic educational subjects or broad concepts.

Examples

Programming

Software Engineering

Engineering

Object Oriented Programming

Computer Networks

Operating Systems

Data Structures

Algorithms

DBMS

Engineering Mathematics

Problem Solving

Communication

Leadership

Teamwork

Critical Thinking

These are too generic to improve semantic matching.

Remove them.

----------------------------------------------------------

## EVIDENCE PRESERVATION

Every UnifiedKnowledgeItem MUST preserve all evidence in the `source_evidence` list.

Each `source_evidence` object contains:
- `source_type`: One of "SKILL" (for resume skills), "PROJECT", "EXPERIENCE", "EDUCATION", "CERTIFICATION".
- `source_name`: The name of the project, role @ company, degree, or certification.
- `explicit`: Always true.

## EVIDENCE STATUS
For each technology and capability, determine the overall `evidence_status`:
- "Demonstrated": If the skill is explicitly supported by at least one PROJECT or EXPERIENCE source.
- "Academic": If the skill is supported ONLY by EDUCATION or CERTIFICATION sources.
- "Claimed": If the skill is found ONLY in the SKILL (Resume Skills) source.

----------------------------------------------------------

## DEDUPLICATION

Create ONE canonical UnifiedKnowledgeItem per technology.

Create ONE canonical UnifiedKnowledgeItem per capability.

Merge all evidence.

Preserve every source.

Never duplicate technologies.

Never duplicate capabilities.

Never lose evidence.

----------------------------------------------------------

## MERGING RULES

Merge ONLY equivalent concepts.

Examples

ReactJS

React.js

React

↓

React

NodeJS

Node.js

↓

Node.js

Do NOT merge unrelated concepts.

Examples

TensorFlow

PyTorch

remain separate.

Backend Development

System Architecture

remain separate.

Deployment

Containerization

remain separate.

----------------------------------------------------------

## STRICT RULES

1.

Never invent technologies.

2.

Never invent capabilities.

3.

Never invent engineering domains.

4.

Never invent responsibilities.

5.

Never infer proficiency.

6.

Never infer expertise.

7.

Never infer seniority.

8.

Never infer production experience.

9.

Never remove explicitly extracted engineering knowledge.

10.

Never duplicate KnowledgeItems.

11.

Always preserve evidence.

12.

Always preserve source diversity.

13.

Always normalize equivalent names.

14.

Always prefer explicit evidence over assumptions.

----------------------------------------------------------

## OUTPUT

Return ONLY the UnifiedKnowledge JSON.

Do not explain your reasoning.

Do not output markdown.

Do not output additional text.
"""),
                ("user", """Here is the structured intelligence extracted from the candidate's resume:

### Resume Skills
{skills_context}

### Project Intelligence
{project_context}

### Experience Intelligence
{experience_context}

### Education Intelligence
{education_context}

### Certification Intelligence
{certification_context}

Synthesize ONE coherent UnifiedKnowledge graph based on all the evidence provided above.""")
            ])

            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain = prompt | llm.with_structured_output(UnifiedKnowledge)
                
        return cls._groq_chain

    @staticmethod
    async def fuse_knowledge(
        skills: List[str],
        project_intel: List[ProjectIntelligence],
        exp_intel: List[ExperienceIntelligence],
        edu_intel: List[EducationIntelligence],
        cert_intel: List[CertificationIntelligence]
    ) -> UnifiedKnowledge:
        """
        Takes raw skills and intelligence objects, serializes them, and calls the Fusion LLM.
        """
        groq_chain = KnowledgeFusionService._get_chains()
        
        # Serialize payloads cleanly
        def serialize_list(intel_list):
            return json.dumps(
                [item.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True) for item in intel_list],
                indent=2
            )

        payload_vars = {
            "skills_context": json.dumps(skills, indent=2),
            "project_context": serialize_list(project_intel),
            "experience_context": serialize_list(exp_intel),
            "education_context": serialize_list(edu_intel),
            "certification_context": serialize_list(cert_intel)
        }
        
        llm_result = None
        
        if groq_chain:
            try:
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
            except Exception as e:
                logger.error(f"[Knowledge Fusion] Groq failed: {e}.")
                
        if not llm_result:
            raise RuntimeError("All LLMs failed to fuse knowledge.")
            
        return cast(UnifiedKnowledge, llm_result)
