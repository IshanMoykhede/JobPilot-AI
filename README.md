<div align="center">
  <h1>🚀 JobPilot AI</h1>
  <p>Your Intelligent Co-Pilot for Job Search & Career Advancement</p>
</div>

---

## 🌟 Overview
**JobPilot AI** is a cutting-edge platform designed to supercharge the job search experience. Built with a modern tech stack, it leverages AI-driven agents to provide intelligent career insights, personalized resume tailoring, and smart job recommendations.

---

## 🏗️ System Architecture & AI Pipelines

JobPilot AI is powered by two primary, highly sophisticated AI pipelines that work in tandem to optimize the job search journey:

### 1. 🎯 Job Search Pipeline
This pipeline is responsible for finding the most relevant job opportunities based on the candidate's deep profile and current market conditions.

**How it works:**
- **Profile Ingestion:** Captures and structures the candidate's core profile, including skills, past experience, and role preferences.
- **Semantic Search (Vector DB):** Queries a **Qdrant** vector database to perform a context-aware semantic search against live job descriptions, ensuring matches go far beyond simple keyword hits.
- **Market Intelligence:** Analyzes the raw search results using LLMs to extract key technical requirements, soft skills, and role expectations.
- **Scoring & Recommendation:** An AI recommendation agent scores each job based on its alignment with the candidate's profile, presenting only the most highly matched opportunities to the user.

### 2. 🤖 Resume Tailoring Pipeline
Once a target job is identified, this pipeline dynamically tailors the candidate's resume to maximize ATS scores and interview chances.

**How it works:**
- **Intent Routing:** Analyzes the target job description to understand the specific core competencies and technical intent required for the role.
- **Experience & Project Intelligence:** Specialized generative agents review the candidate's past projects and experiences. They rewrite and emphasize specific achievements and metrics that directly align with the target role.
- **Skill Alignment:** Identifies critical skills in the candidate's profile that are demanded by the job description, naturally bringing them to the forefront of the resume.
- **Final Synthesis:** A synthesizer agent compiles the tailored sections, ensuring consistent tone and professional formatting, resulting in a highly targeted, ATS-friendly resume ready for submission.

---

## ✨ Key Features
- **🤖 AI-Powered Resume Tailoring:** Dynamically adjust your resume and profile to perfectly match targeted job descriptions.
- **🧠 Smart Candidate Insights:** Deep learning analysis that evaluates candidate profiles against market demands and skill gaps.
- **🎯 Precision Job Search:** Context-aware, semantic search capabilities to find the most relevant roles.
- **🎨 Premium UI/UX:** A stunning, modern interface built with the latest frontend technologies.

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, Qdrant (Vector DB), LLM Agent Architecture
- **Frontend:** React, React Router, Tailwind CSS, Lucide React, Vite

## 🚀 Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---
<div align="center">
  <p>Built with ❤️ for the future of recruitment and career growth.</p>
</div>
