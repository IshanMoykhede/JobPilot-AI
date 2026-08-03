import asyncio
import json
import time
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.common import ResumeContent
from app.resume_tailoring_agent.nodes.project_generator_node import project_generator_node
from langchain_core.exceptions import OutputParserException
from groq import RateLimitError

PROJECT_INTELLIGENCE_DATA = [
    {
      "domains": ["Software Engineering"],
      "complexity": "ADVANCED",
      "achievements": [
        {
          "action": "Architected",
          "impact": "Secure authentication and authorization for users, organizers, and admins",
          "problem": "Multi-role access control and authentication",
          "solution": "REST API backend with role-based access control and JWT authentication",
          "technologies": ["Node.js", "Express.js", "JWT"]
        },
        {
          "action": "Integrated",
          "impact": "Enabled individual and group registrations with dynamic form schemas",
          "problem": "Payment processing and document uploads",
          "solution": "Razorpay payment gateway and Cloudinary-based document uploads",
          "technologies": ["Razorpay", "Cloudinary"]
        },
        {
          "action": "Built",
          "impact": "Improved event management and organization",
          "problem": "Organizer analytics and admin approval workflows",
          "solution": "Admin approval workflows, organizer analytics dashboards, and notification pipelines",
          "technologies": ["Recharts", "MongoDB"]
        }
      ],
      "capabilities": [
        "Backend Development", "Frontend Development", "Full-Stack Development",
        "REST API Design", "Authentication", "Authorization", "Database Design",
        "Payment Integration", "Notification Pipelines"
      ],
      "project_name": "CampusConnect \u2014 Full-Stack Event Management Platform",
      "project_type": "Web Application",
      "technologies": [
        "React.js", "Node.js", "Express.js", "MongoDB", "JWT", "Razorpay",
        "Cloudinary", "Tailwind CSS"
      ],
      "architecture_tags": ["RESTful", "Monolith"]
    },
    {
      "domains": ["Software Engineering", "Artificial Intelligence / Machine Learning"],
      "complexity": "ADVANCED",
      "achievements": [
        {
          "action": "Implemented",
          "impact": "Server never accesses plaintext data",
          "problem": "Secure client-side data encryption",
          "solution": "Client-side AES-GCM encryption with PBKDF2 key derivation and BIP39 recovery",
          "technologies": ["AES-GCM", "PBKDF2", "BIP39"]
        },
        {
          "action": "Engineered",
          "impact": "Zero-knowledge architecture",
          "problem": "Local LLM inference without server access",
          "solution": "Browser-side RAG pipeline using Transformers.js for vector embeddings and WebLLM (Qwen 0.5B) for local LLM inference",
          "technologies": ["Transformers.js", "WebLLM (Qwen 0.5B)"]
        },
        {
          "action": "Developed",
          "impact": "Secure and efficient OCR processing",
          "problem": "Scanned PDF processing with OCR",
          "solution": "FastAPI OCR microservice (EasyOCR + PyMuPDF) for scanned PDFs with Groq LLaMA 3.1 post-processing",
          "technologies": ["FastAPI", "EasyOCR", "PyMuPDF", "Groq LLaMA 3.1"]
        }
      ],
      "capabilities": [
        "Frontend Development", "Backend Development", "Full-Stack Development",
        "REST API Design", "Authentication", "Authorization", "Database Design",
        "Encryption", "Decryption", "Local LLM Inference", "OCR Processing"
      ],
      "project_name": "VaultVani \u2014 Zero-Knowledge AI Document Vault",
      "project_type": "Web Application",
      "technologies": [
        "React.js", "Node.js", "FastAPI", "MongoDB", "WebLLM (Qwen 0.5B)",
        "Transformers.js", "Web Crypto API", "EasyOCR", "AES-GCM", "PBKDF2",
        "BIP39", "bcrypt", "JWT", "Groq LLaMA 3.1", "PyMuPDF", "OTP"
      ],
      "architecture_tags": ["Zero-Knowledge", "Microservices"]
    },
    {
      "domains": ["Artificial Intelligence / Machine Learning", "Software Engineering"],
      "complexity": "ADVANCED",
      "achievements": [
        {
          "action": "Architected",
          "impact": "Automated tailored resume generation per job match",
          "problem": "Job search and resume matching",
          "solution": "Multi-agent pipeline with Intent Router and AI-driven feature extraction",
          "technologies": ["Python", "LangGraph", "OpenAI API", "SerpAPI", "FastAPI", "Redis", "PostgreSQL"]
        },
        {
          "action": "Implemented",
          "impact": "Multi-session state persistence",
          "problem": "State persistence across sessions",
          "solution": "Redis snapshots and PostgreSQL with SerpAPI system.result caching",
          "technologies": ["Redis", "PostgreSQL"]
        }
      ],
      "capabilities": [
        "Backend Development", "API Design", "Database Design",
        "Caching", "System Architecture", "AI API Integration"
      ],
      "project_name": "AI Job Search Agent \u2014 Multi-Agent LangGraph Workflow",
      "project_type": "API Service",
      "technologies": [
        "Python", "LangGraph", "OpenAI API", "SerpAPI", "FastAPI", "Redis", "PostgreSQL"
      ],
      "architecture_tags": ["Microservices", "Event-Driven"]
    }
]

JDS = {
    "AI Engineering": "Looking for an AI Engineer with experience in LLM integration, LangGraph, Python, multi-agent workflows, vector databases, and scalable AI infrastructure. Must have strong RAG experience and microservices architecture.",
    "Software Developer": "We need a Full Stack Software Developer proficient in React.js, Node.js, Express, and MongoDB. Experience with JWT authentication, payment gateways like Stripe/Razorpay, and building robust RESTful APIs is required.",
    "Mechanical Engineer": "Seeking a Mechanical Engineer for HVAC systems design, CAD modeling, thermodynamics, and manufacturing process optimization. Must have experience with AutoCAD, SolidWorks, and physical prototyping."
}

def create_state(jd: str) -> ResumeAgentState:
    candidate_synthesis = json.dumps({
        "project_intelligence": PROJECT_INTELLIGENCE_DATA
    })
    return ResumeAgentState(
        resume_id="test_1",
        session_id="session_1",
        user_id="user_1",
        messages=[],
        job_knowledge=jd,
        candidate_synthesis=candidate_synthesis,
        pending_sections=[],
        resume_content=None,
        user_query="Please tailor my projects to fit this job."
    )

def test_project_generator():
    for role, jd in JDS.items():
        print(f"\n{'='*50}\nTesting Role: {role}\n{'='*50}")
        state = create_state(jd)
        
        success = False
        attempts = 0
        while not success and attempts < 3:
            try:
                # Mock running the node synchronously for testing since the node is sync
                state = project_generator_node(state)
                success = True
            except Exception as e:
                # check if rate limited
                if "429" in str(e):
                    print(f"Rate limited (429)! Waiting 60 seconds before retrying... ({attempts + 1}/3)")
                    time.sleep(60)
                    attempts += 1
                else:
                    print(f"Error occurred: {e}")
                    break
        
        if success:
            print(f"Next Node: {state.next_node}")
            print(f"Response Message: {state.response_message}")
            if state.resume_content and state.resume_content.sections:
                for section in state.resume_content.sections:
                    if section.section_type == "PROJECTS":
                        print("\nGenerated Projects:")
                        for p in section.content:
                            print(f"\nTitle: {p.title}")
                            print(f"Role: {p.role}")
                            print(f"Technologies: {', '.join(p.technologies)}")
                            print("Highlights:")
                            for h in p.highlights:
                                print(f" - {h}")
            else:
                print("No projects generated.")
                
        # Wait slightly between successful calls to avoid immediately hitting limits
        time.sleep(5)

if __name__ == "__main__":
    test_project_generator()
